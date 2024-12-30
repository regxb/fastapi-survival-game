from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import map_objects as crud_map_object
from app.crud.map_objects import base_crud_map_object, base_crud_map
from app.models.map_objects import Map
from app.schemas.map_objects import MapResponseSchema, MapObjectResponseSchema, MapObjectCreateSchema


class MapObjectService:
    def __init__(self, map_id: int, session: AsyncSession):
        self.map_id = map_id
        self.session = session

    async def add_object_on_map(self, object_data: MapObjectCreateSchema) -> MapObjectCreateSchema:
        if await self.can_place_object(**object_data.model_dump(include={"x", "y", "height", "width"})):
            return await base_crud_map_object.create(self.session, object_data)
        raise HTTPException(status_code=409, detail="The place is already taken")


    async def can_place_object(self, x: int, y: int, height: int, width: int) -> bool:
        if x < 0 or y < 0 or height < 0 or width < 0:
            raise HTTPException(status_code=422, detail="Coordinates must be positive numbers only")
        map_ = await base_crud_map.get_by_id(self.session, self.map_id)
        if x + width > map_.size or y + height > map_.size:
            raise HTTPException(status_code=422, detail="Coordinates cannot go beyond the map")
        result = await crud_map_object.check_placement_on_map(self.session, x, y, height, width, self.map_id)
        return result


class MapObjectResponseService:

    def __init__(self, map_id: int, session: AsyncSession):
        self.map_id = map_id
        self.session = session

    async def make_map_data_response(self) -> MapObjectResponseSchema:
        map_ = await base_crud_map.get_by_id(self.session, self.map_id)
        if not map_:
            raise HTTPException(status_code=404, detail="Map not found")
        map_objects = await crud_map_object.get_map_objects(self.session, self.map_id)

        response = MapResponseSchema(
            size=map_.size,
            map_objects=[MapObjectResponseSchema(
                type=game_obj.type.name,
                x1=game_obj.x,
                y1=game_obj.y,
                x2=game_obj.height + game_obj.y - 1,
                y2=game_obj.width + game_obj.x - 1
            ) for game_obj in map_objects]
        )
        return response
