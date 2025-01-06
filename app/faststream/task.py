import asyncio
import json
from datetime import datetime

from faststream.redis import RedisRouter

from app.core.database import async_session_maker
from app.crud.gameplay import get_farm_session
from app.crud.players import get_player_resource, base_crud_player
from app.models.maps import FarmMode
from app.models.players import PlayerResources

router = RedisRouter()


@router.subscriber("farm_session_task")
async def farm_session_task(message: str):
    data = json.loads(message)
    await asyncio.sleep(10)
    # await asyncio.sleep(data["total_time"] * 60)
    async with async_session_maker() as session:
        farm_session = await get_farm_session(session, data["farm_session_id"])
        if not farm_session or farm_session.status != "in_progress":
            return
        farm_session.status = "completed"

        player = await base_crud_player.get_by_id(session, farm_session.player_id)
        player.status = "waiting"

        player_resource = await get_player_resource(session, farm_session.player_id, farm_session.resource_id)
        if not player_resource:
            player_resource = PlayerResources(player_id=farm_session.player_id,
                                              resource_id=farm_session.resource_id, )
            session.add(player_resource)
            await session.flush()

        player_resource.count += data["total_resources"]
        await session.commit()
