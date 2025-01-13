from aiogram.utils.web_app import WebAppUser
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.gameplay_model import BuildingCost
from app.models.map_model import MapObject
from app.models.player_model import Player
from app.repository.gameplay_repository import repository_building_cost
from app.repository.player_repository import (repository_player,
                                              repository_player_base,
                                              repository_player_resource)
from app.schemas.gameplay import BuildingCostResponseSchema, BuildingCostSchema
from app.schemas.players import (PlayerBaseCreateDBSchema,
                                 PlayerBaseCreateSchema)
from app.services.base_service import BaseService
from app.services.map_service import MapService
from app.services.player_service import PlayerService
from app.services.validation_service import ValidationService


class BuildingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_player_base(
            self,
            telegram_id: int,
            object_data: PlayerBaseCreateSchema,
    ) -> MapObject:
        player = await repository_player.get(self.session, player_id=telegram_id, map_id=object_data.map_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        ValidationService.can_player_do_something(player)
        if await repository_player_base.get(self.session, owner_id=player.id, map_id=object_data.map_id):
            raise HTTPException(status_code=400, detail="Player already has a base on this map")

        building_costs = await repository_building_cost.get_multi(self.session, type="base")
        player_resources = await repository_player_resource.get_multi(self.session, player_id=player.id)
        if not ValidationService.can_player_build(building_costs, player_resources):
            raise HTTPException(status_code=400, detail="Not enough resources")

        x1, y1 = object_data.x1, object_data.y1
        x2, y2 = x1 + 1, y1 + 1

        map_service = MapService(self.session)
        if not await map_service.area_is_free(object_data.map_id, x1, y1, x2, y2):
            raise HTTPException(status_code=409, detail="The place is already taken")

        new_map_object = await map_service.create_player_base_map_object(player.name, object_data.map_id)
        await map_service.add_position_to_map_object(x1, y1, x2, y2, new_map_object.id)
        await repository_player_base.create(
            self.session,
            PlayerBaseCreateDBSchema(
                map_object_id=new_map_object.id,
                map_id=new_map_object.map_id,
                owner_id=player.id
            )
        )
        PlayerService.update_player_resources(player_resources, building_costs)

        await BaseService.commit_or_rollback(self.session)
        return new_map_object

    async def get_cost_building_base(self, building_type: str, telegram_id: int) -> BuildingCostSchema:
        costs = await repository_building_cost.get_multi(
            self.session,
            options=[joinedload(BuildingCost.resource)],
            type=building_type
        )
        if not costs:
            raise HTTPException(status_code=404, detail="Building cost not found")
        player = await repository_player.get(
            self.session,
            options=[joinedload(Player.resources)],
            player_id=telegram_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        can_build = ValidationService.can_player_build(costs, player.resources)
        resources = {cost.resource.name: cost.quantity for cost in costs}
        return BuildingCostSchema(can_build=can_build, resources=resources)
