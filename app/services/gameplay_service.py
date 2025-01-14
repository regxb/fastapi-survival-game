import json
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.broker.main import broker
from app.models import MapObject, Player, ResourcesZone, Inventory
from app.models.gameplay_model import Item, ItemRecipe
from app.repository import (repository_farm_mode, repository_farm_session,
                            repository_player)
from app.repository.gameplay_repository import repository_item
from app.schemas.gameplay import (FarmResourcesSchema,
                                  FarmSessionCreateSchema, FarmSessionSchema, CraftItemSchema)
from app.services.base_service import BaseService
from app.services.player_service import PlayerService
from app.services.validation_service import ValidationService


class FarmingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def start_farming(self, farm_data: FarmResourcesSchema, telegram_id: int) -> FarmSessionSchema:
        player = await repository_player.get(
            self.session,
            options=[
                joinedload(Player.map_object).
                joinedload(MapObject.resource_zone).
                joinedload(ResourcesZone.resource)
            ],
            player_id=telegram_id,
            map_id=farm_data.map_id,
        )
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        ValidationService.can_player_do_something(player)
        ValidationService.is_farmable_area(player.map_object)

        current_mode = await repository_farm_mode.get(
            self.session,
            resource_zone_id=player.map_object.resource_zone.id,
            mode=farm_data.mode.value,
        )
        ValidationService.can_player_start_farming(player.energy, current_mode)

        player.energy -= current_mode.total_energy
        player.status = "farming"

        farm_session = await repository_farm_session.create(
            self.session,
            FarmSessionCreateSchema(
                map_id=farm_data.map_id,
                resource_id=player.map_object.resource_zone.resource.id,
                player_id=player.id,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(minutes=current_mode.total_minutes)
            )
        )

        await self._publish_farm_task(farm_session, current_mode)

        await BaseService.commit_or_rollback(self.session)

        time_left = BaseService.get_time_left(farm_session.end_time)
        return FarmSessionSchema(time_left=time_left, **farm_session.__dict__)

    async def _publish_farm_task(self, farm_session, current_farm_mode) -> None:
        task_data = {
            "farm_session_id": farm_session.id,
            "farm_mode": current_farm_mode.mode,
            "total_minutes": current_farm_mode.total_minutes,
            "total_energy": current_farm_mode.total_energy,
            "total_resources": current_farm_mode.total_resources,
        }
        await broker.publish(json.dumps(task_data), "farm_session_task")


class ItemService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_items(self):
        items = await repository_item.get_multi(
            self.session,
            options=[joinedload(Item.recipe).joinedload(ItemRecipe.resource)],
        )
        response = [
            {
                "tier": item.tier,
                "id": item.id,
                "name": item.name,
                "can_craft": True,
                "recipe": {
                    "resources": {
                        recipe.resource.name: recipe.resource_quantity
                        for recipe in item.recipe
                    }
                },
            }
            for item in items
        ]
        return response

    async def craft_item(self, telegram_id: int, craft_data: CraftItemSchema):
        player = await repository_player.get(
            self.session,
            options=[
                joinedload(Player.resources),
                joinedload(Player.inventory).joinedload(Inventory.item)
            ],
            player_id=telegram_id,
            map_id=craft_data.map_id
        )

        item = await repository_item.get(
            self.session,
            options=[joinedload(Item.recipe).joinedload(ItemRecipe.resource)],
            id=craft_data.item_id
        )
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        if not ValidationService.does_user_have_enough_resources(item.recipe, player.resources):
            raise HTTPException(status_code=400, detail="Not enough items")

        for recipe in item.recipe:
            PlayerService.update_player_resources(player.resources, recipe.resource_id, recipe.resource_quantity,
                                                  "decrease")
        player_inventory = Inventory(player_id=player.player_id, item_id=item.id)
        self.session.add(player_inventory)
        await BaseService.commit_or_rollback(self.session)


        response = [item.item.name for item in player.inventory]

        return {"player_items": response}
