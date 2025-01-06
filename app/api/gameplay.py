from aiogram.utils.web_app import WebAppUser
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.depends.auth import get_user_data_from_request
from app.models.gameplay import Resource
from app.schemas.gameplay import PlayerMoveSchema, FarmModeEnum, BuildingType, ResourceSchema, BuildingCostResponseSchema, \
    PlayerMoveResponseSchema, FarmModeSchema, FarmSessionSchema
from app.schemas.maps import MapObjectCreateSchema
from app.schemas.players import PlayerResponseSchema
from app.services.gameplay import FarmingService, BuildingService
from app.services.maps import MapService
from app.services.players import PlayerService

router = APIRouter(prefix="/gameplay", tags=["gameplay"])


@router.get("/resources", response_model=list[ResourceSchema])
async def get_resources(session: AsyncSession = Depends(get_async_session)):
    return await FarmingService(session).get_resources()


@router.get("/cost-of-building-base", response_model=BuildingCostResponseSchema)
async def get_cost_building_base(
        building_type:  BuildingType,
        session: AsyncSession = Depends(get_async_session)
):
    return await BuildingService(session).get_cost_building_base(building_type.value)


@router.post("/build-base")
async def build_base(
        object_data: MapObjectCreateSchema,
        user: WebAppUser = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session)
):
    return await MapService(session).add_player_base_on_map(user, object_data)


@router.patch("/move-player", response_model=PlayerMoveResponseSchema)
async def move_player(
        player_data: PlayerMoveSchema,
        user: WebAppUser = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session)
):
    return await PlayerService(session).move_player(user.id, player_data)


@router.get("/choose-farm-mode", response_model=FarmModeSchema)
async def get_farm_mode(
        map_id: int,
        session: AsyncSession = Depends(get_async_session),
        user: WebAppUser = Depends(get_user_data_from_request),
):
    return await FarmingService(session).get_farm_mode(map_id, user.id)


@router.patch("/farm-resources", response_model=FarmSessionSchema)
async def farm_resources(
        map_id: int,
        farm_mode: FarmModeEnum,
        session: AsyncSession = Depends(get_async_session),
        user: WebAppUser = Depends(get_user_data_from_request),
):
    return await FarmingService(session).start_farming(map_id, user.id, farm_mode)
