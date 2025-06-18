from typing import Annotated

from aiogram.utils.web_app import WebAppUser
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.depends.deps import get_user_data_from_request
from app.schemas import PlayerResourcesSchema, TransferResourceSchema, ResourceSchema, FarmSessionSchema, \
    StartFarmResourcesSchema, StopFarmResourcesSchema
from app.services import FarmingService
from app.services.resource import ResourceTransferService

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("/", response_model=list[ResourceSchema])
async def get_resources(session: Annotated[AsyncSession, Depends(get_async_session)]):
    return await FarmingService(session).get_resources()


@router.patch("/farm/start")
async def farm_resources(
        farm_data: StartFarmResourcesSchema,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await FarmingService(session).start_farming(farm_data, user.id)

@router.patch("/farm/stop")
async def stop_farm_resources(
        farm_data: StopFarmResourcesSchema,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await FarmingService(session).stop_farming(user.id, farm_data)


@router.patch("/transfer/")
async def transfer_resources(
        transfer_data: TransferResourceSchema,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await ResourceTransferService(session).transfer(user.id, transfer_data)
