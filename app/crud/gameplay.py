import datetime

from fastapi import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.gameplay import FarmSession, BuildingCost, Resource


async def get_farm_session(session: AsyncSession, farm_session_id: int):
    stmt = select(FarmSession).where(FarmSession.id == farm_session_id)
    result = await session.scalar(stmt)
    if not result:
        raise HTTPException(status_code=404, detail="Farm session not found")
    return result


async def get_active_farm_session(session: AsyncSession, telegram_id: int, map_id: int):
    stmt = (select(FarmSession).
    where(and_(
        FarmSession.player_id == telegram_id,
        FarmSession.status == "in_progress",
        FarmSession.map_id == map_id))
    )
    result = await session.scalar(stmt)
    return result


async def create_farm_session(
        session: AsyncSession, player_id: int, resource_id: int, map_id: int, total_minutes: int
):
    farm_session = FarmSession(
        player_id=player_id,
        resource_id=resource_id,
        map_id=map_id,
        start_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        end_time=(
                datetime.datetime.now()
                + datetime.timedelta(minutes=total_minutes)
        ).strftime('%Y-%m-%d %H:%M:%S'))
    session.add(farm_session)
    await session.flush()
    return farm_session


async def get_building_cost(session: AsyncSession, building_type: str):
    stmt = (select(BuildingCost).
            options(joinedload(BuildingCost.resource)).
            where(BuildingCost.type == building_type))
    result = await session.execute(stmt)
    if not result:
        raise HTTPException(status_code=404, detail="Building cost not found")
    return result.scalars().all()


async def get_resources(session: AsyncSession):
    result = await session.execute(select(Resource).order_by(Resource.id))
    return result.scalars().all()
