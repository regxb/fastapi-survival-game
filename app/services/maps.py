from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import maps as crud_map_object
from app.crud.maps import get_map_with_objects as crud_get_map_with_objects, base_crud_map_object, base_crud_map, \
    create_map_object, create_object_position
from app.crud.players import create_player_base, base_crud_player
from app.models.maps import Map, MapObject, PlayerBase, MapObjectPosition
from app.schemas.maps import MapsObjectsResponseSchema, MapObjectResponseSchema, MapObjectCreateSchema


class MapService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_maps(self, offset: int = 0, limit: int = 100):
        maps = await base_crud_map.get_multi(self.session, offset=offset, limit=limit)
        return maps

    async def get_map_with_objects(self, map_id: int):
        map_ = await base_crud_map.get_by_id(self.session, map_id)
        map_objects = await crud_get_map_with_objects(self.session, map_id)

        map_objects_response = [MapObjectResponseSchema(
            name=map_object.name,
            map_object_id=map_object.id,
            type=map_object.type,
            is_farmable=map_object.is_farmable,
            x1=map_object.position.x1,
            y1=map_object.position.y1,
            x2=map_object.position.x2,
            y2=map_object.position.y2
        ) for map_object in map_objects]

        return MapsObjectsResponseSchema(height=map_.height, width=map_.width, map_objects=map_objects_response)

    async def get_map_by_id(self, map_id: int) -> Map:
        map_ = await base_crud_map.get_by_id(self.session, map_id)
        return map_

    async def add_player_base_on_map(self, telegram_id: int, object_data: MapObjectCreateSchema):
        player = await base_crud_player.get(self.session, user_id=telegram_id, map_id=object_data.map_id)
        if player is None:
            raise HTTPException(status_code=404, detail="Player not found")
        x2 = object_data.x1 + 1
        y2 = object_data.y1 + 1
        if await self.can_place_object(object_data.map_id, object_data.x1, object_data.y1, x2, y2):
            map_object = await create_map_object(self.session, object_data.name, object_data.map_id)
            await create_object_position(self.session, map_object.id, object_data.x1, object_data.y1, x2, y2)
            await create_player_base(self.session, map_object.id, map_object.map_id, telegram_id)

            try:
                await self.session.commit()
            except IntegrityError:
                await self.session.rollback()
                raise HTTPException(status_code=500, detail="Database error occurred.")
            return map_object

        raise HTTPException(status_code=409, detail="The place is already taken")

    async def can_place_object(self, map_id: int, x1: int, y1: int, x2: int, y2: int) -> bool:
        map_ = await base_crud_map.get_by_id(self.session, map_id)
        if x2 > map_.width or y2 > map_.height:
            raise HTTPException(status_code=422, detail="Coordinates cannot go beyond the map")
        result = await crud_map_object.check_placement_on_map(self.session, x1, y1, x2, y2, map_id)
        return result
