import json
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.faststream.main import broker
from app.models import MapObject, Player, ResourcesZone, FarmSession
from app.repository import (repository_farm_mode, repository_farm_session,
                            repository_player)
from app.schemas.gameplay import (FarmResourcesSchema,
                                  FarmSessionCreateSchema, FarmSessionSchema)
from app.services.base_service import BaseService
from app.services.validation_service import ValidationService


class FarmingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def start_farming(self, farm_data: FarmResourcesSchema, telegram_id: int) -> FarmSessionSchema:
        player = await repository_player.get(
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

        current_mode = await repository_farm_mode.get(
            self.session,
            resource_zone_id=player.map_object.resource_zone.id,
            mode=farm_data.mode.value,
        )
        ValidationService.can_player_start_farming(player.energy, current_mode)

        player.energy -= current_mode.total_energy
        player.status = "farming"

        farm_session = await repository_farm_session.create(
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

        return FarmSessionSchema(time_left=self.get_time_left(farm_session.end_time), **farm_session.__dict__)

    async def _publish_farm_task(self, farm_session, current_farm_mode) -> None:
        task_data = {
            "farm_session_id": farm_session.id,
            "farm_mode": current_farm_mode.mode,
            "total_minutes": current_farm_mode.total_minutes,
            "total_energy": current_farm_mode.total_energy,
            "total_resources": current_farm_mode.total_resources,
        }
        await broker.publish(json.dumps(task_data), "farm_session_task")

    @staticmethod
    def get_time_left(time_end: datetime):
        time_diff = time_end - datetime.now()
        total_seconds = time_diff.total_seconds()

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds % 1) * 1000)

        return {
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "milliseconds": milliseconds
        }
