from aiogram.utils.web_app import WebAppInitData, WebAppUser
from fastapi import APIRouter, Query
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.depends.auth import get_user_data_from_request
from app.models.users import User
from app.schemas.users import UserSchema
from app.services.users import UserService

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/", response_model=UserSchema)
async def create_user(
        user: WebAppUser = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session)
):
    return await UserService(session).create_user(user)

@router.get("/list", response_model=list[UserSchema])
async def get_users(
        offset: int = Query(ge=0, default=0),
        limit: int = Query(ge=0, le=100, default=100),
        session: AsyncSession = Depends(get_async_session)):
    return await UserService(session).get_users(offset, limit)

@router.get("/", response_model=UserSchema)
async def get_user(
        user: WebAppUser = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session)
):
    return await UserService(session).get_user(user.id)
