import json

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.gameplay import create_farm_session, get_building_cost, get_resources
from app.crud.maps import get_resource_zone, base_crud_map_object, get_farm_mode
from app.crud.players import get_player, base_crud_player
from app.faststream.main import broker
from app.models.maps import FarmMode
from app.schemas.gameplay import FarmModeSchema, FarmModeEnum, FarmSessionSchema, BuildingCostSchema, \
    BuildingCostResponseSchema, ResourceSchema


class FarmingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def start_farming(self, map_id: int, telegram_id: int, farm_mode: FarmModeEnum) -> FarmSessionSchema:
        player = await get_player(self.session, map_id, telegram_id)
        self._validate_player_status(player)
        self._validate_farmable_area(player.map_object)

        resource_zone = await get_resource_zone(self.session, player.map_object_id)
        current_farm_mode = await self._get_farm_mode_for_zone(resource_zone.id, farm_mode)

        self._deduct_energy(player, current_farm_mode.total_energy)

        farm_session = await create_farm_session(
            self.session, player.id, resource_zone.resource_id, map_id, current_farm_mode.total_minutes
        )
        player.status = "farming"

        await self._publish_farm_task(farm_session, current_farm_mode)
        await self._commit_and_refresh(farm_session)

        return FarmSessionSchema.model_validate(farm_session)

    async def get_farm_mode(self, map_id: int, telegram_id: int) -> FarmModeSchema:
        player = await base_crud_player.get(self.session, map_id=map_id, user_id=telegram_id)
        if player is None:
            raise HTTPException(status_code=404, detail="Player not found")

        map_object = await base_crud_map_object.get_by_id(self.session, player.map_object_id)
        self._validate_farmable_area(map_object)

        resource_zone = await get_resource_zone(self.session, map_object.id)

        return FarmModeSchema(
            player_resource_multiplier=player.resource_multiplier,
            player_energy_multiplier=player.energy_multiplier,
            **resource_zone.__dict__)

    async def get_resources(self) -> list[ResourceSchema]:
        resources = await get_resources(self.session)
        return [ResourceSchema.model_validate(resource) for resource in resources]

    # --- Вспомогательные методы ---
    def _validate_player_status(self, player) -> None:
        if player.status != "waiting":
            raise HTTPException(status_code=400, detail="The player is currently doing some action")

    def _validate_farmable_area(self, map_object) -> None:
        if not map_object.is_farmable:
            raise HTTPException(status_code=400, detail="Can't farm in this area")

    async def _get_farm_mode_for_zone(self, resource_zone_id: int, farm_mode: FarmModeEnum) -> FarmMode:
        farm_mode = await get_farm_mode(self.session, resource_zone_id, farm_mode.value)
        if farm_mode is None:
            raise HTTPException(status_code=404, detail="Farm mode not found")
        return farm_mode

    def _deduct_energy(self, player, required_energy: int) -> None:
        player.energy -= required_energy
        if player.energy < 0:
            raise HTTPException(status_code=400, detail="Not enough energy to start farming")

    async def _publish_farm_task(self, farm_session, current_farm_mode) -> None:
        task_data = {
            "farm_session_id": farm_session.id,
            "farm_mode": current_farm_mode.mode,
            "total_minutes": current_farm_mode.total_minutes,
            "total_energy": current_farm_mode.total_energy,
            "total_resources": current_farm_mode.total_resources,
        }
        await broker.publish(json.dumps(task_data), "farm_session_task")

    async def _commit_and_refresh(self, entity):
        try:
            await self.session.commit()
            await self.session.refresh(entity)
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Database error occurred")


class BuildingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_cost_building_base(self, building_type: str) -> BuildingCostResponseSchema:
        costs = await get_building_cost(self.session, building_type)
        resources = [BuildingCostSchema(amount=cost.quantity, id=cost.resource.id) for cost in costs]
        return BuildingCostResponseSchema(resources=resources)
