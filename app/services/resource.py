from fastapi import HTTPException
from sqlalchemy.orm import joinedload

from app.models import Player, PlayerResources, PlayerBase, PlayerResourcesStorage
from app.repository import repository_resource, player_repository, player_resources_storage_repository
from app.schemas import TransferResourceSchema, PlayerResourcesSchema, ResourcesStorageCreate
from app.services import ValidationService, PlayerService
from app.services.base import BaseTransferService, BaseService
from app.services.player import PlayerResponseService


class ResourceTransferService(BaseTransferService):
    async def transfer(self, telegram_id: int, transfer_data: TransferResourceSchema) -> PlayerResourcesSchema:
        player = await self._get_player_with_resources(telegram_id, transfer_data.map_id)
        resource = await repository_resource.get(self.session, id=transfer_data.resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")

        base_storage = await self._get_or_create_base_storage(player, resource.id)

        self._validate_resource_transfer(
            player, base_storage,
            resource.id,
            transfer_data.count,
            transfer_data.direction.value
        )

        self._update_resources(transfer_data.direction.value, transfer_data.count, player, resource.id,
                                     base_storage)

        await BaseService.commit_or_rollback(self.session)

        await self.session.refresh(player)

        return self._serialize_player_resources(player)

    async def _get_player_with_resources(self, telegram_id: int, map_id: int) -> Player:
        player = await player_repository.get(
            self.session,
            options=[
                joinedload(Player.resources).joinedload(PlayerResources.resource),
                joinedload(Player.base).joinedload(PlayerBase.resources)
            ],
            player_id=telegram_id,
            map_id=map_id
        )
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        if not player.base:
            raise HTTPException(status_code=404, detail="Player has no base")
        return player

    async def _get_or_create_base_storage(self, player: Player, resource_id: int) -> PlayerResourcesStorage:
        base_storage = await player_resources_storage_repository.get(
            self.session,
            options=[joinedload(PlayerResourcesStorage.resource)],
            player_base_id=player.base.id,
            resource_id=resource_id,
        )
        if not base_storage:
            base_storage = await player_resources_storage_repository.create(
                self.session,
                ResourcesStorageCreate(
                    player_base_id=player.base.id,
                    resource_id=resource_id,
                    player_id=player.id
                )
            )


        return base_storage

    def _validate_resource_transfer(self, player: Player, base_storage: PlayerResourcesStorage, resource_id: int,
                                    count: int, direction: str) -> None:
        ValidationService.can_player_transfer_resources(player, base_storage, resource_id, count, direction)

    def _update_resources(self, direction: str, count: int, player: Player, resource_id: int,
                                base_storage: PlayerResourcesStorage) -> None:
        if direction == "to_storage":
            base_storage.resource_quantity += count
            PlayerService(self.session).update_resources(player.resources, resource_id, count, "decrease")
        elif direction == "from_storage":
            base_storage.resource_quantity -= count
            PlayerService(self.session).update_resources(player.resources, resource_id, count, "increase")

    def _serialize_player_resources(self, player: Player) -> PlayerResourcesSchema:
        player_resources = PlayerResponseService.serialize_resources(player.resources)
        storage_resources = PlayerResponseService.serialize_resources(player.base.resources)
        return PlayerResourcesSchema(player_resources=player_resources, storage_resources=storage_resources)
