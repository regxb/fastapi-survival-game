from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.bot.bot import bot
from app.core.database import async_session_maker
from app.models import PlayerResources
from app.repository import (farm_session_repository, player_repository,
                            player_resource_repository, repository_resource)


async def farm_session_task(task_data: dict):
    async with async_session_maker() as session:
        farm_session = await farm_session_repository.get_by_id(session, task_data["farm_session_id"])
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

        player_resource.resource_quantity += task_data["total_resources"]

        resource = await repository_resource.get(session, id=player_resource.resource_id)

        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e.orig))

        message = (f'<b>✨ Фарм завершён успешно! ✨</b>\n\n\n'
                   f'<b>🧑🏻‍🎤Персонаж</b> успешно завершил фарм и добыл ресурсы:\n'
                   f'<b>{resource.icon}{resource.name}</b> - {task_data["total_resources"]}')

        await bot.send_message(player.player_id, message, parse_mode="html")
