from fastapi import HTTPException
from sqlalchemy import select, and_, or_, not_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.crud.base import CRUDBase
from app.models.maps import Map, MapObject, MapObjectPosition, ResourcesZone, FarmMode
from app.schemas.maps import MapObjectCreateSchema, MapCreateSchema

CRUDMapObject = CRUDBase[MapObject, MapObjectCreateSchema]
base_crud_map_object = CRUDMapObject(MapObject)

CRUDMap = CRUDBase[Map, MapCreateSchema]
base_crud_map = CRUDMap(Map)


async def get_map_with_objects(session: AsyncSession, map_id: int) -> Map:
    stmt = ((select(Map).
             where(Map.id == map_id)).
    options(
        joinedload(Map.map_objects),
        joinedload(Map.map_objects).joinedload(MapObject.position),
        joinedload(Map.map_objects).joinedload(MapObject.resource_zone).joinedload(ResourcesZone.resource),
    ))
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(status_code=404, detail="Map not found")
    return result


async def get_map_object(session: AsyncSession, map_object_id: int):
    stmt = (select(MapObject).
    where(MapObject.id == map_object_id).
    options(
        joinedload(MapObject.position),
        joinedload(MapObject.resource_zone).joinedload(ResourcesZone.resource),

    ))
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(status_code=404, detail="Map object not found")
    return result


async def get_resource_zone(session: AsyncSession, map_object_id: int):
    stmt = (
        select(ResourcesZone).
        where(ResourcesZone.map_object_id == map_object_id).
        options(joinedload(ResourcesZone.farm_modes))
    )
    result = await session.scalar(stmt)
    return result


async def get_farm_mode(session: AsyncSession, resource_zone_id: int, farm_mode: str):
    stmt = (select(FarmMode).
            where(and_(FarmMode.resource_zone_id == resource_zone_id, FarmMode.mode == farm_mode)))
    result = await session.scalar(stmt)
    if result is None:
        raise HTTPException(status_code=404, detail="FarmMode not found")
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
    map_object = MapObject(name=f"{name} base", type="base", is_farmable=False, map_id=map_id)
    session.add(map_object)
    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=404, detail="Map not found")
    return map_object


async def create_object_position(
        session: AsyncSession,
        map_object_id: int,
        x1: int,
        y1: int,
        x2: int,
        y2: int
):
    object_position = MapObjectPosition(
        map_object_id=map_object_id, x1=x1, y1=y1, x2=x2, y2=y2)
    session.add(object_position)
    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=404, detail="Map object not found")
    return object_position
