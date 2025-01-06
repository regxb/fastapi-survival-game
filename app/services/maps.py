from aiogram.types import WebAppData
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import maps as crud_map_object
from app.crud.gameplay import get_building_cost
from app.crud.maps import get_map_with_objects as crud_get_map_with_objects, base_crud_map, \
    create_map_object, create_object_position, get_map_object
from app.crud.players import create_player_base, base_crud_player, get_player_base, get_player_resources
from app.models.gameplay import BuildingCost
from app.models.maps import Map, MapObject
from app.models.players import PlayerResources
from app.schemas.maps import MapObjectResponseSchema, MapObjectCreateSchema, MapResponseSchema, BaseMapSchema


class MapService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_maps(self, offset: int = 0, limit: int = 100) -> list[BaseMapSchema]:
        maps = await base_crud_map.get_multi(self.session, offset=offset, limit=limit)
        return [BaseMapSchema.model_validate(map_) for map_ in maps]

    async def get_map_object(self, map_object_id: int) -> MapObjectResponseSchema:
        map_object = await get_map_object(self.session, map_object_id)
        return MapObjectResponseSchema.model_validate(map_object)

    async def get_map_with_objects(self, map_id: int) -> MapResponseSchema:
        map_objects = await crud_get_map_with_objects(self.session, map_id)
        return MapResponseSchema.model_validate(map_objects)

    async def get_map_by_id(self, map_id: int) -> Map:
        return await base_crud_map.get_by_id(self.session, map_id)

    async def add_player_base_on_map(self, user: WebAppData, object_data: MapObjectCreateSchema) -> MapObject:
        player = await base_crud_player.get(self.session, user_id=user.id, map_id=object_data.map_id)
        if player is None:
            raise HTTPException(status_code=404, detail="Player not found")

        if await get_player_base(self.session, player.id):
            raise HTTPException(status_code=400, detail="Player already has a base on this map")

        x1, y1 = object_data.x1, object_data.y1
        x2, y2 = x1 + 1, y1 + 1

        building_costs = await get_building_cost(self.session, "base")
        player_resources = await get_player_resources(self.session, player.id)

        if (await self.can_place_object(object_data.map_id, x1, y1, x2, y2) and
                await self.can_user_build(building_costs, player_resources)):
            map_object = await create_map_object(self.session, user.username, object_data.map_id)
            await create_object_position(self.session, map_object.id, x1, y1, x2, y2)
            await create_player_base(self.session, map_object.id, map_object.map_id, player.id)

            await self.update_player_resources(player_resources, building_costs)
            return map_object

        raise HTTPException(status_code=409, detail="The place is already taken")

    async def can_place_object(self, map_id: int, x1: int, y1: int, x2: int, y2: int) -> bool:
        map_ = await base_crud_map.get_by_id(self.session, map_id)
        if x2 > map_.width or y2 > map_.height:
            raise HTTPException(status_code=422, detail="Coordinates cannot go beyond the map")
        return await crud_map_object.check_placement_on_map(self.session, x1, y1, x2, y2, map_id)

    async def can_user_build(self, building_costs: list[BuildingCost], player_resources: list[PlayerResources]) -> bool:
        costs = {building_cost.resource_id: building_cost.quantity for building_cost in building_costs}
        resources = {player_resource.resource_id: player_resource.count for player_resource in player_resources}
        if not player_resources:
            raise HTTPException(status_code=400, detail="Not enough resources")
        for resource_id, count in costs.items():
            if resource_id not in resources or resources[resource_id] < count:
                raise HTTPException(status_code=400, detail="Not enough resources")
        return True

    async def update_player_resources(
            self, player_resources: list[PlayerResources], building_costs: list[BuildingCost]
    ) -> None:
        costs = {cost.resource_id: cost.quantity for cost in building_costs}
        for resource in player_resources:
            if resource.resource_id in costs:
                resource.count -= costs[resource.resource_id]

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Database error occurred")
