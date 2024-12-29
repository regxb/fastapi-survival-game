from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import map_objects as crud_map_objects
from app.models.map_objects import Map
from app.schemas.map_objects import MapResponseSchema, MapObjectResponseSchema, MapObjectCreateSchema


class MapObjectService:
    def __init__(self, map_id: int, session: AsyncSession):
        self.map_id = map_id
        self.session = session

    async def add_object_on_map(self, object_data: MapObjectCreateSchema):
        if await self.can_place_object(**object_data.model_dump(include={"x", "y", "height", "width"})):
            return await crud_map_objects.add_object_on_map(object_data, self.session)
        raise HTTPException(status_code=409, detail="The place is already taken")


    async def can_place_object(self, x: int, y: int, height: int, width: int) -> bool:
        result = await crud_map_objects.check_placement_on_map(x, y, height, width, self.map_id, self.session)
        return False if result else True


class MapObjectResponseService:

    def __init__(self, map_id: int, session: AsyncSession):
        self.map_id = map_id
        self.session = session

    async def make_map_data_response(self):
        map_ = await crud_map_objects.get_map(self.map_id, self.session)
        if not map_:
            raise HTTPException(status_code=404, detail="Map not found")
        map_objects = await crud_map_objects.get_map_objects(self.map_id, self.session)
        response = MapResponseSchema(
            size=map_.size,
            map_objects=[MapObjectResponseSchema(
                type=game_obj.type.name,
                x=game_obj.x,
                y=game_obj.y,
                height=game_obj.height,
                width=game_obj.width
            ) for game_obj in map_objects]
        )
        return response
