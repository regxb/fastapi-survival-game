import asyncio

from app.core.database import async_session_maker


async def regenerate_energy():
    from app.services import PlayerService
    async with async_session_maker() as session:
        await PlayerService(session).update_energy()
        await PlayerService(session).update_health()
