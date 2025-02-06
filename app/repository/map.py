from sqlalchemy import and_, not_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import map_bits

from app.models.map import Map, MapObject, MapObjectPosition, ResourcesZone
from app.repository.base import BaseRepository

MapObjectRepository = BaseRepository[MapObject]
map_object_repository = MapObjectRepository(MapObject)

MapRepository = BaseRepository[Map]
map_repository = MapRepository(Map)

MapObjectPositionRepository = BaseRepository[MapObjectPosition]
map_object_position_repository = MapObjectPositionRepository(MapObjectPosition)

ResourceZoneRepository = BaseRepository[ResourcesZone]
resource_zone_repository = ResourceZoneRepository(ResourcesZone)


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
