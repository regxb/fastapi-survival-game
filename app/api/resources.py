from typing import Annotated

from aiogram.utils.web_app import WebAppUser
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.depends.deps import get_user_data_from_request
from app.schemas.farm import FarmResourcesSchema, FarmSessionSchema
from app.schemas.resource import ResourceSchema
from app.services import FarmingService

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("/", response_model=list[ResourceSchema])
async def get_resources(session: Annotated[AsyncSession, Depends(get_async_session)]):
    return await FarmingService(session).get_resources()


@router.patch("/farm/", response_model=FarmSessionSchema)
async def farm_resources(
        farm_data: FarmResourcesSchema,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await FarmingService(session).start_farming(farm_data, user.id)
