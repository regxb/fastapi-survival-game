from aiogram.utils.web_app import WebAppUser
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.depends.deps import get_user_data_from_request
from app.schemas.gameplay import BuildingType, FarmResourcesSchema
from app.schemas.players import PlayerBaseCreateSchema
from app.services.building_service import BuildingService
from app.services.gameplay_service import FarmingService

router = APIRouter(prefix="/gameplay", tags=["gameplay"])


@router.get("/cost-of-building-base/")
async def get_cost_building_base(
        building_type: BuildingType,
        user: WebAppUser = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session)
):
    return await BuildingService(session).get_cost_building_base(building_type.value, user.id)


@router.post("/build-base/")
async def build_base(
        object_data: PlayerBaseCreateSchema,
        user: WebAppUser = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session)
):
    return await BuildingService(session).create_player_base(user.id, object_data)


# @router.get("/choose-farm-mode/")
# async def get_farm_mode(
#         map_id: int,
#         session: AsyncSession = Depends(get_async_session),
#         user: WebAppUser = Depends(get_user_data_from_request),
# ):
#     return await FarmingService(session).get_farm_mode(map_id, user.id)


@router.patch("/farm-resources/")
async def farm_resources(
        farm_data: FarmResourcesSchema,
        session: AsyncSession = Depends(get_async_session),
        user: WebAppUser = Depends(get_user_data_from_request),
):
    return await FarmingService(session).start_farming(farm_data, user.id)
