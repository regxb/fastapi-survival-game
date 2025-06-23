from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Player, PlayerResources
from app.repository import (create_inventory_resource, create_storage_resource,
                            get_player_with_all_resources,
                            get_player_with_resources_for_transfer,
                            player_resource_repository)
from app.schemas import PlayerResourcesSchema, TransferResourceSchema
from app.serialization.player import serialize_player_resources
from app.services.base import BaseService, BaseTransferService
from app.validation.player import can_player_transfer_resources


class ResourceService(BaseService):

    @staticmethod
    async def get_resources(session: AsyncSession, player_id: int) -> Sequence[PlayerResources]:
        player_resources = await player_resource_repository.get_multi(session, player_id=player_id)
        return player_resources

    @staticmethod
    def get_resource_count_after_farming(total_minutes: int):
        multiplier = 1
        total_resource_quantity = 0
        for minutes in range(1, total_minutes + 1):
            if minutes % 5 == 0:
                multiplier += 1
            total_resource_quantity += 1 * multiplier
        return total_resource_quantity


class ResourceTransferService(BaseTransferService):
    async def transfer(self, telegram_id: int, transfer_data: TransferResourceSchema) -> PlayerResourcesSchema:
        player = await get_player_with_resources_for_transfer(
            self.session,
            telegram_id,
            transfer_data.map_id,
            transfer_data.resource_id
        )
        can_player_transfer_resources(player, transfer_data.count, transfer_data.direction.value)
        self._update_resources(transfer_data.direction.value, transfer_data.count, player, transfer_data.resource_id)
        await BaseService.commit_or_rollback(self.session)
        player = await get_player_with_all_resources(self.session, telegram_id, transfer_data.map_id)
        return serialize_player_resources(player)

    def _update_resources(self, direction: str, count: int, player: Player, resource_id: int) -> None:
        if direction == "to_storage":
            if player.base.resources:
                player.base.resources[0].resource_quantity += count
            else:
                create_storage_resource(self.session, resource_id, count, player.base.id, player.id)
            player.resources[0].resource_quantity -= count
        elif direction == "from_storage":
            if player.resources:
                player.resources[0].resource_quantity += count
            else:
                create_inventory_resource(self.session, resource_id, count, player.id)
            player.base.resources[0].resource_quantity -= count
