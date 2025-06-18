import json
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from taskiq.compat import model_validate

from app.core.database import redis_client
from app.models import MapObject, Player, Resource, ResourcesZone, FarmSession, PlayerResources
from app.repository import (farm_session_repository,
                            player_repository)
from app.schemas import (StartFarmResourcesSchema, FarmSessionCreateSchema,
                         FarmSessionSchema, StopFarmResourcesSchema, StopFarmingResourcesSchema)
from app.services.base import BaseService
from app.services.item import ItemService
from app.services.player import PlayerResponseService
from app.services.validation import ValidationService


class FarmingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def start_farming(self, farm_data: StartFarmResourcesSchema, telegram_id: int) -> FarmSessionSchema:
        player = await player_repository.get(
            self.session,
            options=[
                joinedload(Player.map_object).
                joinedload(MapObject.resource_zone).
                joinedload(ResourcesZone.resource),
                joinedload(Player.resources)
            ],
            player_id=telegram_id,
            map_id=farm_data.map_id,
        )
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        ValidationService.can_player_do_something(player)
        ValidationService.is_farmable_area(player.map_object)
        ValidationService.can_player_start_farming(player.energy, farm_data.total_minutes)

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

        await self._publish_farm_task(farm_data.total_minutes, farm_session, player.resources)

        await BaseService.commit_or_rollback(self.session)

        total_seconds = int((farm_session.end_time - farm_session.start_time).total_seconds())
        seconds_pass = int((datetime.now() - farm_session.start_time).total_seconds())
        return FarmSessionSchema(total_seconds=total_seconds, seconds_pass=seconds_pass)

    async def stop_farming(self, telegram_id: int, farm_data: StopFarmResourcesSchema):
        player = await player_repository.get(
            self.session,
            options=[
                joinedload(Player.map_object),
                joinedload(Player.resources).joinedload(PlayerResources.resource),
                joinedload(Player.farm_sessions.and_(FarmSession.status == "in_progress"))
            ],
            player_id=telegram_id,
            map_id=farm_data.map_id,
        )
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        ValidationService.is_farmable_area(player.map_object)

        if player.status == "farming" and player.farm_sessions[0].status == "in_progress":
            player.status = "waiting"
            player.farm_sessions[0].status = "completed"
            await BaseService.commit_or_rollback(self.session)
            player_resources = PlayerResponseService.serialize_resources(player.resources)

            return StopFarmingResourcesSchema(
                player_energy=player.energy,
                player_health=player.health,
                resources=player_resources
            )
        else:
            raise HTTPException(status_code=400, detail="Something went wrong")

    async def _publish_farm_task(
            self,
            total_minutes: int,
            farm_session: FarmSession,
            resources: list[PlayerResources]
    ) -> None:
        resources_before_farming = next((r for r in resources if r.resource_id == farm_session.resource_id), None)
        task_data = {
            "total_minutes": total_minutes,
            "farm_session_id": farm_session.id,
            "status": farm_session.status,
            "resource_id": farm_session.resource_id,
            "resources_before_farming": resources_before_farming.resource_quantity
        }
        redis_client.hset(f'farm:{farm_session.player_id}', mapping=task_data)
        redis_client.rpush('task_queue', json.dumps(task_data))

    async def get_resources(self):
        result = await self.session.execute(select(Resource).order_by(Resource.id))
        return result.scalars().all()
