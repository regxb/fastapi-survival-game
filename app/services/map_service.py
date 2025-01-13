from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.map_model import Map, MapObject, ResourcesZone
from app.repository import map_repository
from app.repository.map_repository import (repository_map,
                                           repository_map_object,
                                           repository_map_object_position)
from app.schemas.maps import (BaseMapSchema, MapObjectCreateSchema,
                              MapObjectPositionSchema, MapResponseSchema)


class MapService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_maps(self, offset: int = 0, limit: int = 100) -> list[BaseMapSchema]:
        maps = await repository_map.get_multi(self.session, offset=offset, limit=limit)
        return [BaseMapSchema.model_validate(map_) for map_ in maps]

    async def get_map_with_objects(self, map_id: int) -> MapResponseSchema:
        map_objects = await repository_map.get(
            self.session,
            options=[
                joinedload(Map.map_objects),
                joinedload(Map.map_objects).joinedload(MapObject.position),
                joinedload(Map.map_objects).joinedload(MapObject.resource_zone).joinedload(ResourcesZone.resource),
                joinedload(Map.map_objects).joinedload(MapObject.resource_zone).joinedload(ResourcesZone.farm_modes)
            ],
            id=map_id)
        return MapResponseSchema.model_validate(map_objects)

    async def create_player_base_map_object(self, name: str, map_id: int):
        new_map_object = await repository_map_object.create(
            self.session,
            MapObjectCreateSchema(
                name=f"{name} base",
                is_farmable=False,
                map_id=map_id,
                type="base"
            )
        )
        return new_map_object

    async def add_position_to_map_object(self, x1: int, y1: int, x2: int, y2: int, map_object_id: int):
        new_map_object_position = await repository_map_object_position.create(
            self.session,
            MapObjectPositionSchema(
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
                map_object_id=map_object_id
            )
        )
        return new_map_object_position

    async def area_is_free(self, map_id: int, x1: int, y1: int, x2: int, y2: int) -> bool:
        map_ = await repository_map.get_by_id(self.session, map_id)
        if x2 > map_.width or y2 > map_.height:
            raise HTTPException(status_code=422, detail="Coordinates cannot go beyond the map")
        return await map_repository.check_placement_on_map(self.session, x1, y1, x2, y2, map_id)
