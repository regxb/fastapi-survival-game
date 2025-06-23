import asyncio
import json
from datetime import datetime, timedelta

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import redis_client
from app.models import (Resource, PlayerResources)
from app.repository import farm_session_repository, player_repository, get_player_with_resources_and_zone_resources, \
    get_player_resource_quantity, get_player_with_specific_resource
from app.schemas import (FarmSessionCreateSchema, FarmSessionSchema,
                         StartFarmResourcesSchema, StopFarmResourcesSchema)
from app.services.base import BaseService
from app.validation.farm import validate_farm_session
from app.validation.player import validate_player_before_farming, validate_player


class FarmingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def start_farming(self, farm_data: StartFarmResourcesSchema, telegram_id: int) -> FarmSessionSchema:
        player = await get_player_with_resources_and_zone_resources(self.session, telegram_id, farm_data.map_id)
        validate_player_before_farming(player, farm_data.total_minutes)
        player_id = player.id
        player.status = "farming"

        farm_session = await farm_session_repository.create(
            self.session,
            FarmSessionCreateSchema(
                map_id=farm_data.map_id,
                resource_id=player.map_object.resource_zone.resource.id,
                player_id=player.id,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(minutes=farm_data.total_minutes)
            )
        )

        farm_session_id = farm_session.id
        resource_id = farm_session.resource_id
        total_seconds = int((farm_session.end_time - farm_session.start_time).total_seconds())
        seconds_pass = int((datetime.now() - farm_session.start_time).total_seconds())

        await BaseService.commit_or_rollback(self.session)

        player_resource_quantity = await get_player_resource_quantity(self.session, player_id, resource_id)

        await self._publish_farm_task(
            farm_data.total_minutes,
            player_resource_quantity,
            farm_session_id,
            resource_id,
            player_id,
        )

        return FarmSessionSchema(total_seconds=total_seconds, seconds_pass=seconds_pass)

    @staticmethod
    async def update_player_resources_while_farming(
            session: AsyncSession,
            resource_id: int,
            player_id: int,
            minute: int,
            multiplier: int
    ):
        player = await get_player_with_specific_resource(session, player_id, resource_id)
        if player.status != "farming":
            raise ValueError("Player is not farming")
        base_gain = 1
        if minute % 5 == 0:
            multiplier += 1
        if not player.resources:
            player_resource = PlayerResources(
                player_id=player.id, resource_id=resource_id, resource_quantity=base_gain * multiplier
            )
            session.add(player_resource)
        else:
            player.resources[0].resource_quantity += base_gain * multiplier
        player.energy -= 1
        await asyncio.sleep(60)
        await BaseService.commit_or_rollback(session)

    async def stop_farming(self, telegram_id: int, farm_data: StopFarmResourcesSchema):
        player = await player_repository.get(
            self.session, player_id=telegram_id, map_id=farm_data.map_id, status="farming"
        )
        validate_player(player)
        farm_session = await farm_session_repository.get(
            self.session, player_id=player.id, status="in_progress", map_id=farm_data.map_id
        )
        validate_farm_session(farm_session)
        player.status = "waiting"
        farm_session.status = "completed"
        await BaseService.commit_or_rollback(self.session)
        return status.HTTP_204_NO_CONTENT

    async def _publish_farm_task(
            self,
            total_minutes: int,
            resource_count: int,
            farm_session_id: int,
            resource_id: int,
            player_id: int,
    ) -> None:
        task_data = {
            "total_minutes": total_minutes,
            "farm_session_id": farm_session_id,
            "resource_id": resource_id,
            "player_id": player_id,
            "resources_before_farming": resource_count if resource_count else 0
        }
        redis_client.rpush('task_queue', json.dumps(task_data))

    async def get_resources(self):
        result = await self.session.execute(select(Resource).order_by(Resource.id))
        return result.scalars().all()
