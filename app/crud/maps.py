from typing import Sequence

from asyncpg import ForeignKeyViolationError
from fastapi import HTTPException
from sqlalchemy import select, and_, or_, not_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.crud.base import CRUDBase
from app.models.maps import Map, MapObject, MapObjectPosition, PlayerBase, ResourcesZone
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


async def get_farm_zone(session: AsyncSession, map_id: int, map_object_id: int):
    stmt = (select(ResourcesZone).
            where(and_(ResourcesZone.map_id == map_id, ResourcesZone.map_object_id == map_object_id)))
    result = await session.scalar(stmt)
    return result


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


async def create_map_object(session: AsyncSession, name: str, map_id: int):
    map_object = MapObject(name=f"{name} base", map_id=map_id)
    session.add(map_object)
    try:
        await session.flush()
    except IntegrityError:
        raise HTTPException(status_code=404, detail="Map not found")
    finally:
        await session.rollback()


async def create_object_position(
        session: AsyncSession,
        map_object_id: int,
        x1:int,
        y1:int,
        x2:int,
        y2:int
):
    object_position = MapObjectPosition(
        map_object_id=map_object_id, x1=x1, y1=y1, x2=x2, y2=y2)
    session.add(object_position)
    try:
        await session.flush()
    except IntegrityError:
        raise HTTPException(status_code=404, detail="Map object not found")
    finally:
        await session.rollback()
