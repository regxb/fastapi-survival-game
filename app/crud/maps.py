from typing import Sequence

from sqlalchemy import select, and_, or_, not_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.crud.base import CRUDBase
from app.models.maps import Map, MapObject, MapObjectPosition, PlayerBase
from app.schemas.maps import MapObjectCreateSchema, MapCreateSchema

CRUDMapObject = CRUDBase[MapObject, MapObjectCreateSchema]
base_crud_map_object = CRUDMapObject(MapObject)

CRUDMap = CRUDBase[Map, MapCreateSchema]
base_crud_map = CRUDMap(Map)


async def get_map_with_objects(session: AsyncSession, map_id: int) -> Sequence[MapObject]:
    stmt = (select(MapObject).
            options(joinedload(MapObject.position)).
            where(MapObject.map_id == map_id))
    result = await session.execute(stmt)
    map_objects = result.scalars().all()
    return map_objects


async def check_placement_on_map(
        session: AsyncSession, x1: int, y1: int, x2: int, y2: int, map_id: int) -> bool:
    stmt = (select(MapObject).
    join(MapObjectPosition, MapObjectPosition.map_object_id == MapObject.id).
    where(and_(
        MapObject.map_id == map_id,
        not_(
            or_(
                MapObjectPosition.x2 < x1,
                x2 < MapObjectPosition.x1,
                MapObjectPosition.y2 < y1,
                y2 < MapObjectPosition.y1,
            )
        )
    )))
    result = await session.execute(stmt)
    map_objects = result.scalars().all()
    return False if map_objects else True
