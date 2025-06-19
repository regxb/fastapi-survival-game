from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Player, PlayerResources, PlayerBase, PlayerResourcesStorage
from app.repository import player_repository, player_resource_repository
from app.schemas import TransferResourceSchema, PlayerResourcesSchema
from app.services import ValidationService
from app.services.base import BaseTransferService, BaseService
from app.services.player import PlayerResponseService


class ResourceService(BaseService):

    @staticmethod
    async def get_resources(session: AsyncSession, player_id: int) -> Sequence[PlayerResources]:
        player_resources = await player_resource_repository.get_multi(session, player_id=player_id)
        return player_resources


class ResourceTransferService(BaseTransferService):
    async def transfer(self, telegram_id: int, transfer_data: TransferResourceSchema) -> PlayerResourcesSchema:
        player = await self._get_player_with_resources(telegram_id, transfer_data.map_id, transfer_data.resource_id)

        ValidationService.can_player_transfer_resources(
            player,
            transfer_data.count,
            transfer_data.direction.value
        )
        self._update_resources(transfer_data.direction.value, transfer_data.count, player, transfer_data.resource_id)
        await BaseService.commit_or_rollback(self.session)
        self.session.expire_all()
        player = await self._get_player_with_all_resources(telegram_id, transfer_data.map_id)
        return self._serialize_player_resources(player)

    async def _get_player_with_resources(self, telegram_id: int, map_id: int, resource_id: int) -> Player:
        player = await player_repository.get(
            self.session,
            options=[
                joinedload(Player.resources.and_(PlayerResources.resource_id == resource_id))
                .joinedload(PlayerResources.resource),
                joinedload(Player.base)
                .joinedload(PlayerBase.resources.and_(PlayerResourcesStorage.resource_id == resource_id))
            ],
            player_id=telegram_id,
            map_id=map_id
        )
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        if not player.base:
            raise HTTPException(status_code=404, detail="Player has no base")
        return player

    def _update_resources(self, direction: str, count: int, player: Player, resource_id: int) -> None:
        if direction == "to_storage":
            if player.base.resources:
                player.base.resources[0].resource_quantity += count
            else:
                storage_resource = PlayerResourcesStorage(
                    player_base_id=player.base.id,
                    resource_id=resource_id,
                    player_id=player.id,
                    resource_quantity=count
                )
                self.session.add(storage_resource)
            player.resources[0].resource_quantity -= count
        elif direction == "from_storage":
            if player.resources:
                player.resources[0].resource_quantity += count
            else:
                inventory_resource = PlayerResources(
                    resource_id=resource_id,
                    player_id=player.id,
                    resource_quantity=count
                )
                self.session.add(inventory_resource)
            player.base.resources[0].resource_quantity -= count

    def _serialize_player_resources(self, player: Player) -> PlayerResourcesSchema:
        player_resources = PlayerResponseService.serialize_resources(player.resources)
        storage_resources = PlayerResponseService.serialize_resources(player.base.resources)
        response = PlayerResourcesSchema(player_resources=player_resources, storage_resources=storage_resources)
        return response

    async def _get_player_with_all_resources(self, telegram_id: int, map_id: int) -> Player:
        player = await player_repository.get(
            self.session,
            options=[
                joinedload(Player.resources).joinedload(PlayerResources.resource),
                joinedload(Player.base).joinedload(PlayerBase.resources)
            ],
            player_id=telegram_id,
            map_id=map_id
        )
        return player
