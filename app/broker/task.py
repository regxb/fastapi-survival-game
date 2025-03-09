import random

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.bot.bot import bot
from app.core.database import async_session_maker
from app.models import PlayerResources, Player, FarmSession
from app.repository import (farm_session_repository, player_repository,
                            player_resource_repository, repository_resource)


async def farm_session_task(task_data: dict):
    total_minutes = task_data.get("total_minutes", 0)
    attack_chance = min(60, int(total_minutes * 2))


    async with async_session_maker() as session:
        farm_session = await farm_session_repository.get_by_id(session, task_data["farm_session_id"])
        if not farm_session or farm_session.status != "in_progress":
            return
        farm_session.status = "completed"

        player = await player_repository.get_by_id(session, farm_session.player_id)
        player.status = "waiting"

        if random.randint(1, 100) <= attack_chance:
            message = await random_zombie_attack(session, player)
        else:
            message = await success_farm(session, farm_session,task_data)
        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e.orig))

        await bot.send_message(player.player_id, message, parse_mode="html")


async def success_farm(session, farm_session: FarmSession, task_data: dict):
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
    resource_new_count = task_data["total_resources"] + random.randint(1, 10)
    player_resource.resource_quantity += resource_new_count

    resource = await repository_resource.get(session, id=player_resource.resource_id)

    message = (f'<b>✨ Фарм завершён успешно! ✨</b>\n\n\n'
               f'<b>🧑🏻‍🎤Персонаж</b> успешно завершил фарм и добыл ресурсы:\n'
               f'<b>{resource.icon}{resource.name}</b> - {resource_new_count}')
    return message
async def random_zombie_attack(session, player: Player):

    lost_health = random.randint(15, 35)
    player.health = max(0, player.health - lost_health)

    player_resources = await player_resource_repository.get_multi(
        session,
        PlayerResources.resource_quantity > 0,
        player_id=player.id
    )
    if player_resources:
        lost_resource = random.choice(player_resources)
        lost_quantity = max(1, lost_resource.resource_quantity // 4)
        lost_resource.resource_quantity = max(0, lost_resource.resource_quantity - lost_quantity)

        resource = await repository_resource.get(session, id=lost_resource.resource_id)


        message = (f"🧟‍♂️ <b>Зомби атаковал игрока!</b>\n\n"
                   f"💥 Игрок потерял <b>{lost_health} HP</b>\n"
                   f"📉 Потерян ресурс: <b>{resource.icon} {resource.name} -{lost_quantity}</b>")

        return message
