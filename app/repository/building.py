from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import BuildingCost
from app.repository import BaseRepository

BuildingCostRepository = BaseRepository[BuildingCost]
building_cost_repository = BuildingCostRepository(BuildingCost)


async def get_building_cost(session: AsyncSession, building_type: str) -> Sequence[BuildingCost]:
    stmt = select(BuildingCost).where(BuildingCost.type == building_type).options(joinedload(BuildingCost.resource))
    result = await session.execute(stmt)
    return result.scalars().all()
