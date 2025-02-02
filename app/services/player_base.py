from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Player, PlayerResources, PlayerBase, BuildingCost, MapObject
from app.models.player import PlayerResourcesStorage, PlayerItemStorage, Inventory
from app.repository import player_repository, building_cost_repository, player_base_repository, \
    player_resource_repository
from app.repository.resource import repository_resource
from app.repository.player import player_resources_storage_repository, player_base_repository, \
    player_resource_repository, player_item_storage_repository, inventory_repository
from app.schemas import InventoryItemCreateSchema, StorageItemCreateSchema, PlayerBaseCreateSchema, \
    PlayerBaseCreateDBSchema, BuildingCostSchema
from app.schemas.building import BuildingCostSchema
from app.schemas.player import PlayerTransferResourceSchema, PlayerResourcesStorageCreate, PlayerBaseCreateDBSchema, \
    PlayerBaseCreateSchema, PlayerResourcesSchema, PlayerTransferItemSchema, PlayerItemsSchema, PlayerBaseSchema
from app.services.map import MapService
from app.services.base import BaseService
from app.services.map import MapObjectService
from app.services.player import PlayerService, PlayerResponseService
from app.services.validation import ValidationService


class PlayerBaseService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def transfer_items(self, telegram_id: int, transfer_data: PlayerTransferItemSchema) -> PlayerItemsSchema:
        player = await player_repository.get(
            self.session,
            options=[
                joinedload(Player.inventory).joinedload(Inventory.item),
                joinedload(Player.base).joinedload(PlayerBase.items).joinedload(PlayerItemStorage.item),
            ],
            player_id=telegram_id,
            map_id=transfer_data.map_id
        )

        ValidationService.can_player_transfer_items(player, transfer_data.direction.value)

        await self._update_items(player, transfer_data.item_id, transfer_data.direction.value)

        await BaseService.commit_or_rollback(self.session)
        await self.session.refresh(player)

        storage_items = PlayerResponseService.serialize_storage_items(player.base.items)
        inventory_items = PlayerResponseService.serialize_inventory(player.inventory)
        return PlayerItemsSchema(storage_items=storage_items, inventory_items=inventory_items)

    async def transfer_resources(
            self, telegram_id: int, transfer_data: PlayerTransferResourceSchema
    ) -> PlayerResourcesSchema:
        player = await self._get_player_with_detail(telegram_id, transfer_data.map_id)
        resource = await repository_resource.get(self.session, id=transfer_data.resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")

        base_storage = await player_resources_storage_repository.get(
            self.session,
            options=[joinedload(PlayerResourcesStorage.resource)],
            player_base_id=player.base.id,
            resource_id=resource.id,
        )

        ValidationService.can_player_transfer_resources(
            player,
            base_storage,
            resource.id,
            transfer_data.count,
            transfer_data.direction.value
        )

        if not base_storage:
            base_storage = await player_resources_storage_repository.create(
                self.session,
                PlayerResourcesStorageCreate(
                    player_base_id=player.base.id,
                    resource_id=resource.id,
                    player_id=player.id
                )
            )

        self._update_resources(transfer_data.direction.value, transfer_data.count, player, resource.id, base_storage)
        await self.session.refresh(player)
        player_resources = PlayerResponseService.serialize_resources(player.resources)
        storage_resources = PlayerResponseService.serialize_resources(player.base.resources)
        await BaseService.commit_or_rollback(self.session)

        return PlayerResourcesSchema(player_resources=player_resources, storage_resources=storage_resources)





    async def _get_player_with_detail(self, telegram_id: int, map_id: int) -> Player:
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

    async def _update_items(self, player: Player, item_id: int, direction: str, ) -> None:
        if direction == "to_storage":
            item = await inventory_repository.get_by_id(self.session, item_id)
            if not item or item.player_id != player.id:
                raise HTTPException(status_code=404, detail="Item not found")
            item_storage = StorageItemCreateSchema(player_base_id=player.base.id, **item.__dict__)
            await player_item_storage_repository.create(self.session, item_storage)
            await self.session.delete(item)
        elif direction == "from_storage":
            item = await player_item_storage_repository.get_by_id(self.session, item_id)
            if not item or item.player_id != player.id:
                raise HTTPException(status_code=404, detail="Item not found")
            inventory_item = InventoryItemCreateSchema.model_validate(item)
            await inventory_repository.create(self.session, inventory_item)
            await self.session.delete(item)

    def _update_resources(
            self,
            direction: str,
            count: int,
            player: Player,
            resource_id: int,
            base_storage: PlayerResourcesStorage
    ) -> None:
        if direction == "to_storage":
            base_storage.resource_quantity += count
            PlayerService(self.session).update_resources(
                player.resources, resource_id, count, "decrease"
            )
        elif direction == "from_storage":
            base_storage.resource_quantity -= count
            PlayerService(self.session).update_resources(
                player.resources, resource_id, count, "increase"
            )


class BuildingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
            self,
            telegram_id: int,
            object_data: PlayerBaseCreateSchema,
    ) -> PlayerBaseSchema:
        player = await player_repository.get(self.session, player_id=telegram_id, map_id=object_data.map_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        ValidationService.can_player_do_something(player)
        if await player_base_repository.get(self.session, owner_id=player.id, map_id=object_data.map_id):
            raise HTTPException(status_code=400, detail="Player already has a base on this map")

        building_costs = await building_cost_repository.get_multi(self.session, type="base")
        player_resources = await player_resource_repository.get_multi(self.session, player_id=player.id)
        if not ValidationService.does_user_have_enough_resources(building_costs, player_resources):
            raise HTTPException(status_code=400, detail="Not enough resources")

        x1, y1 = object_data.x1, object_data.y1
        x2, y2 = x1 + 1, y1 + 1

        map_service = MapService(self.session)
        if not await map_service.area_is_free(object_data.map_id, x1, y1, x2, y2):
            raise HTTPException(status_code=409, detail="The place is already taken")

        new_map_object = await map_service.create_player_base_map_object(player.name, object_data.map_id)
        await MapObjectService(self.session).add_position(x1, y1, x2, y2, new_map_object.id)

        new_player_base = await player_base_repository.create(
            self.session,
            PlayerBaseCreateDBSchema(
                map_object_id=new_map_object.id,
                map_id=new_map_object.map_id,
                owner_id=player.id
            )
        )

        for cost in building_costs:
            PlayerService.update_resources(
                player_resources, cost.resource_id, cost.resource_quantity, "decrease"
            )

        await BaseService.commit_or_rollback(self.session)

        player_base = await player_base_repository.get(
            self.session,
            options=[joinedload(PlayerBase.resources), joinedload(PlayerBase.items)],
            id=new_player_base.id,
        )

        return PlayerBaseSchema(
            map_object_id=new_map_object.id,
            resources=player_base.resources,
            items=player_base.items
        )

    async def get_cost(self, building_type: str, telegram_id: int, map_id: int) -> BuildingCostSchema:
        costs = await building_cost_repository.get_multi(
            self.session,
            options=[joinedload(BuildingCost.resource)],
            type=building_type
        )
        if not costs:
            raise HTTPException(status_code=404, detail="Building cost not found")
        player = await player_repository.get(
            self.session,
            options=[joinedload(Player.resources)],
            player_id=telegram_id,
            map_id=map_id
        )
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        can_build = ValidationService.does_user_have_enough_resources(costs, player.resources)
        resources = {cost.resource.name: cost.resource_quantity for cost in costs}
        return BuildingCostSchema(can_build=can_build, resources=resources)
