from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped

from app.models import MapObject, PlayerBase
from app.repository import building_cost_repository, get_building_cost
from app.repository.player import (get_player_with_base_and_resources,
                                   get_player_with_resources,
                                   player_base_repository)
from app.schemas.building import BuildingCostResponseSchema, BuildingCostSchema
from app.schemas.player import (PlayerBaseCreateDBSchema,
                                PlayerBaseCreateSchema, PlayerBaseSchema)
from app.serialization.resource import serialize_resources
from app.services.base import BaseService
from app.services.map import MapObjectService, MapService
from app.services.player import PlayerService
from app.validation.building import validate_before_building
from app.validation.player import (does_player_have_enough_resources,
                                   validate_player)


class BuildingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.map_service = MapService(session)
        self.map_object_service = MapObjectService(session)

    async def create_base(self, telegram_id: int, object_data: PlayerBaseCreateSchema, ) -> PlayerBaseSchema:
        player = await get_player_with_base_and_resources(self.session, telegram_id, object_data.map_id)
        building_costs = await building_cost_repository.get_multi(self.session, type="base")

        await validate_before_building(
            self.session, building_costs, player, object_data.x1, object_data.y1, object_data.map_id  # type: ignore
        )

        new_map_object = await self._add_object_on_map(object_data, player.name)
        new_map_object_id = new_map_object.id
        await self._create_player_base(player.id, new_map_object)  # type: ignore
        self._update_resources_after_building(building_costs, player.resources)  # type: ignore

        await BaseService.commit_or_rollback(self.session)
        player = await get_player_with_resources(self.session, telegram_id, object_data.map_id)
        resources = serialize_resources(player.resources)
        return PlayerBaseSchema(
            map_object_id=new_map_object_id,
            resources=resources,
        )

    async def _create_player_base(self, player_id: int | Mapped[int], map_object: MapObject) -> PlayerBase:
        new_player_base = await player_base_repository.create(
            self.session,
            PlayerBaseCreateDBSchema(
                map_object_id=map_object.id,
                map_id=map_object.map_id,
                owner_id=player_id  # type: ignore
            )
        )
        return new_player_base

    def _update_resources_after_building(self, building_costs, player_resources) -> None:
        for cost in building_costs:
            PlayerService.update_resources(
                player_resources, cost.resource_id, cost.resource_quantity, "decrease"
            )

    async def _add_object_on_map(self, object_data: PlayerBaseCreateSchema,
                                 player_name: str | Mapped[str]) -> MapObject:
        new_map_object = await self.map_service.create_map_object(player_name, object_data.map_id)
        await MapObjectService(self.session).add_position(
            object_data.x1,
            object_data.y1,
            object_data.x1 + 1,
            object_data.y1 + 1,
            new_map_object.id
        )
        return new_map_object

    async def get_cost(self, building_type: str, telegram_id: int, map_id: int) -> BuildingCostResponseSchema:
        costs = await get_building_cost(self.session, building_type)
        if not costs:
            raise HTTPException(status_code=404, detail="Building cost not found")
        player = await get_player_with_resources(self.session, telegram_id, map_id)
        validate_player(player)
        can_build = does_player_have_enough_resources(costs, player.resources)
        resources = [BuildingCostSchema.model_validate(model) for model in costs]
        return BuildingCostResponseSchema(can_build=can_build, resources=resources)
