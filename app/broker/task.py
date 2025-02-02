import asyncio
import json

from fastapi import HTTPException
from faststream.redis import RedisRouter
from sqlalchemy.exc import IntegrityError

from app.core import config
from app.core.database import async_session_maker
from app.models import PlayerResources
from app.repository import (farm_session_repository, player_repository,
                            player_resource_repository)

router = RedisRouter()


@router.subscriber("farm_session_task")
async def farm_session_task(message: str):
    data = json.loads(message)
    if config.DEV:
        await asyncio.sleep(10)
    else:
        await asyncio.sleep(data["total_minutes"] * 60)
    async with async_session_maker() as session:
        farm_session = await farm_session_repository.get_by_id(session, data["farm_session_id"])
        if not farm_session or farm_session.status != "in_progress":
            return
        farm_session.status = "completed"

        player = await player_repository.get_by_id(session, farm_session.player_id)
        player.status = "waiting"

        player_resource = await player_resource_repository.get(
            session,
            player_id=farm_session.player_id,
            resource_id=farm_session.resource_id
        )
        if not player_resource:
            player_resource = PlayerResources(player_id=farm_session.player_id,
                                              resource_id=farm_session.resource_id, )
            session.add(player_resource)
            await session.flush()

        player_resource.resource_quantity += data["total_resources"]

        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e.orig))
