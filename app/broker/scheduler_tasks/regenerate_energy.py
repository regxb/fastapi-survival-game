from app.core.database import async_session_maker


async def regenerate_energy():
    ...
    # from app.services import PlayerService
    # async with async_session_maker() as session:
    #     await PlayerService(session).update_energy()
    #     await PlayerService(session).update_health()


async def farming_resources():
    from app.services import PlayerService
    async with async_session_maker() as session:
        await PlayerService(session).add_farming_resources()
