from typing import Annotated

from aiogram.utils.web_app import WebAppUser
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.depends.deps import get_user_data_from_request
from app.schemas import (ResourceSchema, StartFarmResourcesSchema,
                         StopFarmResourcesSchema, TransferResourceSchema, PlayerResourcesSchema, FarmSessionSchema)
from app.services import FarmingService
from app.services.resource import ResourceTransferService, ResourceService

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("/", response_model=list[ResourceSchema])
async def get_resources(session: Annotated[AsyncSession, Depends(get_async_session)]):
    return await FarmingService(session).get_resources()


@router.patch("/farm/start/", response_model=FarmSessionSchema)
async def start_farm_resources(
        farm_data: StartFarmResourcesSchema,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
) -> FarmSessionSchema:
    return await FarmingService(session).start_farming(farm_data, user.id)


@router.patch("/farm/stop/")
async def stop_farm_resources(
        farm_data: StopFarmResourcesSchema,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await FarmingService(session).stop_farming(user.id, farm_data)


@router.patch("/transfer/", response_model=PlayerResourcesSchema)
async def transfer_resources(
        transfer_data: TransferResourceSchema,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
) -> PlayerResourcesSchema:
    return await ResourceTransferService(session).transfer(user.id, transfer_data)


@router.get("/farming/")
async def get_resource_count_after_farming(total_minutes: int):
    return ResourceService.get_resource_count_after_farming(total_minutes)
