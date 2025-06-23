from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Map, MapObject
from app.repository import check_placement_on_map, map_repository
from app.schemas import PlayerBaseCreateSchema


def validate_map_object(map_object: MapObject):
    if not map_object:
        raise HTTPException(status_code=404, detail="Map object not found")

async def area_is_free(map_id: int, x1: int, y1: int, x2: int, y2: int) -> bool:
    map_ = await map_repository.get_by_id(session, map_id)
    validate_map_bounds(x2, y2, map_.width, map_.height)
    return await check_placement_on_map(session, x1, y1, x2, y2, map_id)

def validate_map(map: Map):
    if map is None:
        raise HTTPException(status_code=404, detail="Map not found")

def validate_map_bounds(x2: int, y2: int, width: int, height: int):
    if x2 > width or y2 > height:
        raise HTTPException(status_code=422, detail="Coordinates cannot go beyond the map")

async def validate_map_area(
        session: AsyncSession,
        x1: int,
        y1: int,
        map_id: int,
) -> None:
    x2, y2 = x1 + 1, y1 + 1

    map_ = await map_repository.get_by_id(session, map_id)
    validate_map_bounds(x2, y2, map_.width, map_.height)

    if not await check_placement_on_map(session, x1, y1, x2, y2, map_id):
        raise HTTPException(status_code=409, detail="The place is already taken")


def is_farmable_area(map_object) -> None:
    if not map_object.is_farmable:
        raise HTTPException(status_code=400, detail="Can't farm in this area")

