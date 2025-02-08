from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Player, PlayerBase, BuildingCost
from app.repository import player_repository, building_cost_repository
from app.repository.player import player_base_repository, \
    player_resource_repository
from app.schemas import ResourceSchema
from app.schemas.building import BuildingCostResponseSchema, BuildingCostSchema
from app.schemas.player import PlayerBaseCreateDBSchema, \
    PlayerBaseCreateSchema, PlayerBaseSchema
from app.services.base import BaseService
from app.services.map import MapObjectService
from app.services.map import MapService
from app.services.player import PlayerService
from app.services.validation import ValidationService


class BuildingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.map_service = MapService(session)
        self.map_object_service = MapObjectService(session)

    async def create(self, telegram_id: int, object_data: PlayerBaseCreateSchema, ) -> PlayerBaseSchema:
        player = await player_repository.get(self.session, player_id=telegram_id, map_id=object_data.map_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        await self._validate_player_base_exists(player, object_data.map_id)

        building_costs = await building_cost_repository.get_multi(self.session, type="base")
        player_resources = await player_resource_repository.get_multi(self.session, player_id=player.id)
        if not ValidationService.does_user_have_enough_resources(building_costs, player_resources):
            raise HTTPException(status_code=400, detail="Not enough resources")

        await self._validate_map_area(object_data)

        new_map_object = await self._add_object_on_map(object_data, player.name)

        new_player_base = await player_base_repository.create(
            self.session,
            PlayerBaseCreateDBSchema(
                map_object_id=new_map_object.id,
                map_id=new_map_object.map_id,
                owner_id=player.id
            )
        )

        self._update_resources_after_building(building_costs, player_resources)

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

    def _update_resources_after_building(self, building_costs, player_resources):
        for cost in building_costs:
            PlayerService.update_resources(
                player_resources, cost.resource_id, cost.resource_quantity, "decrease"
            )

    async def _add_object_on_map(self, object_data: PlayerBaseCreateSchema, player_name: str):
        new_map_object = await self.map_service.create_player_base_map_object(player_name, object_data.map_id)
        await MapObjectService(self.session).add_position(
            object_data.x1,
            object_data.y1,
            object_data.x1 + 1,
            object_data.y1 + 1,
            new_map_object.id
        )

        return new_map_object

    async def _validate_map_area(self, object_data: PlayerBaseCreateSchema) -> None:
        x1, y1 = object_data.x1, object_data.y1
        x2, y2 = x1 + 1, y1 + 1

        if not await self.map_service.area_is_free(object_data.map_id, x1, y1, x2, y2):
            raise HTTPException(status_code=409, detail="The place is already taken")

    async def _validate_player_base_exists(self, player: Player, map_id: int):
        ValidationService.can_player_do_something(player)
        if await player_base_repository.get(self.session, owner_id=player.id, map_id=map_id):
            raise HTTPException(status_code=400, detail="Player already has a base on this map")

    async def get_cost(self, building_type: str, telegram_id: int, map_id: int) -> BuildingCostResponseSchema:
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
        resources = [BuildingCostSchema.model_validate(model) for model in costs]
        return BuildingCostResponseSchema(can_build=can_build, resources=resources)
