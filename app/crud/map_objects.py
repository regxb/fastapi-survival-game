from typing import Sequence

from sqlalchemy import select, and_, or_, not_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.map_objects import Map, MapObject
from app.schemas.map_objects import MapObjectCreateSchema


async def get_map_objects(map_id: int, session: AsyncSession) -> Sequence[MapObject]:
    stmt  = (select(MapObject).
             options(
        joinedload(MapObject.type),
    ).
             where(MapObject.map_id == map_id))
    result = await session.execute(stmt)
    map_objects = result.scalars().all()
    return map_objects


async def get_map(map_id: int, session: AsyncSession):
    stmt = select(Map).where(Map.id == map_id)
    game_map = await session.scalar(stmt)
    return game_map


async def add_object_on_map(object_data: MapObjectCreateSchema, session: AsyncSession):
    new_object = MapObject(**object_data.model_dump())
    session.add(new_object)
    await session.commit()
    return new_object


async def check_placement_on_map(x: int, y: int, height: int, width: int, map_id: int, session: AsyncSession):
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
    return map_objects