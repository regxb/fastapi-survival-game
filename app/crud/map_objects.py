from typing import Sequence

from sqlalchemy import select, and_, or_, not_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.crud.base import CRUDBase
from app.models.map_objects import Map, MapObject
from app.schemas.map_objects import MapObjectCreateSchema, MapCreateSchema

CRUDMapObject = CRUDBase[MapObject, MapObjectCreateSchema]
base_crud_map_object = CRUDMapObject(MapObject)
CRUDMap = CRUDBase[Map, MapCreateSchema]
base_crud_map = CRUDMap(Map)


async def get_map_objects(session: AsyncSession, map_id: int) -> Sequence[MapObject]:
    stmt = (select(MapObject).
            options(
        joinedload(MapObject.type),
    ).
            where(MapObject.map_id == map_id))
    result = await session.execute(stmt)
    map_objects = result.scalars().all()
    return map_objects


async def check_placement_on_map(
        session: AsyncSession, x: int, y: int, height: int, width: int, map_id: int) -> bool:
    stmt = (select(MapObject).
    where(and_(
        MapObject.map_id == map_id,
        not_(
            or_(
                MapObject.x + MapObject.width < x,
                x + width < MapObject.x,
                MapObject.y + MapObject.height < y,
                y + height < MapObject.y
            )
        )
    )))
    result = await session.execute(stmt)
    map_objects = result.scalars().all()
    return False if map_objects else True
