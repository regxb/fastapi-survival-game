from faststream.redis import RedisBroker

from app.core.database import async_session_maker

router = RedisBroker()


@router.subscriber("regenerate_energy")
async def regenerate_energy():
    from app.services import PlayerService
    async with async_session_maker() as session:
        await PlayerService(session).update_energy()
