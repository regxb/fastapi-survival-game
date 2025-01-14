import asyncio
import json

from fastapi import HTTPException
from faststream.redis import RedisRouter
from sqlalchemy.exc import IntegrityError

from app.core.database import async_session_maker
from app.models import PlayerResources
from app.repository import (repository_farm_session, repository_player,
                            repository_player_resource)

router = RedisRouter()


@router.subscriber("farm_session_task")
async def farm_session_task(message: str):
    data = json.loads(message)
    await asyncio.sleep(10)
    async with async_session_maker() as session:
        farm_session = await repository_farm_session.get_by_id(session, data["farm_session_id"])
        if not farm_session or farm_session.status != "in_progress":
            return
        farm_session.status = "completed"

        player = await repository_player.get_by_id(session, farm_session.player_id)
        player.status = "waiting"

        player_resource = await repository_player_resource.get(
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
