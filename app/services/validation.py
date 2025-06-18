from typing import Type, TypeVar

from fastapi import HTTPException
from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import FarmMode, Inventory
from app.models.item import Item
from app.models.player import Player, PlayerResources, PlayerResourcesStorage
from app.services.map import MapService

ModelType = TypeVar("ModelType")


class ValidationService:

    @staticmethod
    def does_player_have_empty_slot(player: Player, craft_item: Item) -> bool:
        for item in player.inventory:
            if item.item_id == craft_item.id and item.count < craft_item.max_count:
                # print(1)
                return True
        if player.inventory_slots > len(player.inventory):
            # print(2)
            return True
        # print(3)
        return False


    @staticmethod
    def does_user_have_enough_resources(
            costs: Sequence[Type[ModelType]],
            player_resources: Sequence[PlayerResources]
    ) -> bool:
        if not player_resources:
            return False
        player_resource_dict = {res.resource_id: res.resource_quantity for res in player_resources}
        for cost in costs:
            if player_resource_dict.get(cost.resource_id, 0) < cost.resource_quantity:
                return False
        return True

    @staticmethod
    def can_player_do_something(player: Player) -> None:
        if player.status != "waiting" and player.status != "recovery":
            raise HTTPException(status_code=400, detail="The player is currently doing some action")
        if not player or player.map_id is None:
            raise HTTPException(status_code=404, detail="Player is not on the map")

    @staticmethod
    async def validate_area_and_resources_for_building(
            session: AsyncSession, map_id: int, x1: int, y1: int, x2: int, y2: int, building_costs, player_resources
    ):
        if not await MapService(session).area_is_free(map_id, x1, y1, x2, y2):
            raise HTTPException(status_code=409, detail="The place is already taken")
        ValidationService.does_user_have_enough_resources(building_costs, player_resources)

    @staticmethod
    def is_farmable_area(map_object) -> None:
        if not map_object.is_farmable:
            raise HTTPException(status_code=400, detail="Can't farm in this area")

    @staticmethod
    def can_player_start_farming(player_energy: int, total_minutes: int) -> None:
        player_energy -= total_minutes
        if player_energy < 0:
            raise HTTPException(status_code=400, detail="Not enough energy to start farming")

    @staticmethod
    def can_player_transfer_resources(player: Player, base_storage: PlayerResourcesStorage, resource_id: int,
                                      count: int,
                                      direction: str) -> None:
        if not player.base:
            raise HTTPException(status_code=404, detail="Player has no base")
        if player.map_object_id != player.base.map_object_id:
            raise HTTPException(status_code=404, detail="The player is not at the base")
        if direction == "to_storage" and not player.resources:
            raise HTTPException(status_code=400, detail="Not enough resources")
        if direction == "from_storage" and not base_storage:
            raise HTTPException(status_code=400, detail="Not enough resources")

        for resource in player.resources:
            if direction == "to_storage" and resource.resource_id == resource_id and resource.resource_quantity < count:
                raise HTTPException(status_code=400, detail="Not enough resources")
            elif (direction == "from_storage" and
                  resource.resource_id == resource_id and
                  base_storage.resource_quantity < count):
                raise HTTPException(status_code=400, detail="Not enough resources")

    @staticmethod
    def can_player_transfer_items(player: Player, direction: str):
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        if direction == "to_storage" and not player.inventory:
            raise HTTPException(status_code=404, detail="Player has no item")
        if not player.base:
            raise HTTPException(status_code=404, detail="Player has no base")

    @staticmethod
    def can_player_craft_item(player: Player, item: Item) -> None:
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        if not player.base:
            raise HTTPException(status_code=404, detail="Player has no base")
        if player.map_object_id != player.base.map_object_id:
            raise HTTPException(status_code=400, detail="The player is not at the base")
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if not ValidationService.does_user_have_enough_resources(item.recipe, player.resources):
            raise HTTPException(status_code=400, detail="Not enough resources")
        if not ValidationService.does_player_have_empty_slot(player, item):
            raise HTTPException(status_code=400, detail="Inventory is full")

