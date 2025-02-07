from typing import Annotated

from aiogram.utils.web_app import WebAppUser
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.depends.deps import get_user_data_from_request
from app.schemas import PlayerTransferItemSchema
from app.schemas.building import BuildingCostResponseSchema
from app.schemas.building import BuildingType
from app.schemas.player import (PlayerBaseCreateSchema, PlayerBaseSchema,
                                PlayerResourcesSchema,
                                PlayerTransferResourceSchema)
from app.services.player_base import BuildingService, StorageService

router = APIRouter(prefix="/bases",tags=["Bases"])


@router.get("/cost/", response_model=BuildingCostResponseSchema)
async def get_cost_for_building_base(
        map_id: int,
        building_type: BuildingType,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)],
):
    return await BuildingService(session).get_cost(building_type.value, user.id, map_id)


@router.post("/", response_model=PlayerBaseSchema)
async def build_base(
        object_data: PlayerBaseCreateSchema,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await BuildingService(session).create(user.id, object_data)


@router.patch("/transfer/resources/", response_model=PlayerResourcesSchema)
async def transfer_resources(
        transfer_data: PlayerTransferResourceSchema,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await StorageService(session).transfer_resources(user.id, transfer_data)


@router.patch("/transfer/items/")
async def transfer_item(
        transfer_data: PlayerTransferItemSchema,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await StorageService(session).transfer_items(user.id, transfer_data)
