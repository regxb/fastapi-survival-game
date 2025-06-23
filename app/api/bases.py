from typing import Annotated

from aiogram.utils.web_app import WebAppUser
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.depends.deps import get_user_data_from_request
from app.schemas.building import BuildingCostResponseSchema, BuildingType
from app.schemas.player import PlayerBaseCreateSchema, PlayerBaseSchema
from app.services.building import BuildingService

router = APIRouter(prefix="/bases", tags=["Bases"])


@router.get("/cost/", response_model=BuildingCostResponseSchema)
async def get_cost_for_building_base(
        map_id: int,
        building_type: BuildingType,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)],
) -> BuildingCostResponseSchema:
    return await BuildingService(session).get_cost(building_type.value, user.id, map_id)


@router.post("/", response_model=PlayerBaseSchema)
async def build_base(
        object_data: PlayerBaseCreateSchema,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
) -> PlayerBaseSchema:
    return await BuildingService(session).create_base(user.id, object_data)
