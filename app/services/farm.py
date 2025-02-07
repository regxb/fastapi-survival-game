import json
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.broker.main import broker
from app.models import MapObject, Player, Resource, ResourcesZone
from app.repository import (farm_mode_repository, farm_session_repository,
                            player_repository)
from app.schemas import (FarmResourcesSchema, FarmSessionCreateSchema,
                         FarmSessionSchema)
from app.services.base import BaseService
from app.services.validation import ValidationService


class FarmingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def start_farming(self, farm_data: FarmResourcesSchema, telegram_id: int) -> FarmSessionSchema:
        player = await player_repository.get(
            self.session,
            options=[
                joinedload(Player.map_object).
                joinedload(MapObject.resource_zone).
                joinedload(ResourcesZone.resource)
            ],
            player_id=telegram_id,
            map_id=farm_data.map_id,
        )
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        ValidationService.can_player_do_something(player)
        ValidationService.is_farmable_area(player.map_object)

        current_mode = await farm_mode_repository.get(
            self.session,
            resource_zone_id=player.map_object.resource_zone.id,
            mode=farm_data.mode.value,
        )
        ValidationService.can_player_start_farming(player.energy, current_mode)

        player.energy -= current_mode.total_energy
        player.status = "farming"

        farm_session = await farm_session_repository.create(
            self.session,
            FarmSessionCreateSchema(
                map_id=farm_data.map_id,
                resource_id=player.map_object.resource_zone.resource.id,
                player_id=player.id,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(minutes=current_mode.total_minutes)
            )
        )

        await self._publish_farm_task(farm_session, current_mode)

        await BaseService.commit_or_rollback(self.session)

        total_seconds = int((farm_session.end_time - farm_session.start_time).total_seconds())
        seconds_pass = int((datetime.now() - farm_session.start_time).total_seconds())
        return FarmSessionSchema(total_seconds=total_seconds, seconds_pass=seconds_pass)

    async def _publish_farm_task(self, farm_session, current_farm_mode) -> None:
        task_data = {
            "farm_session_id": farm_session.id,
            "farm_mode": current_farm_mode.mode,
            "total_minutes": current_farm_mode.total_minutes,
            "total_energy": current_farm_mode.total_energy,
            "total_resources": current_farm_mode.total_resources,
        }
        await broker.publish(json.dumps(task_data), "farm_session_task")

    async def get_resources(self):
        result = await self.session.execute(select(Resource).order_by(Resource.id))
        return result.scalars().all()
