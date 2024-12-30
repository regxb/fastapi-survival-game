from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_async_session
from app.schemas.users import UserCreateSchema
from app.services.users import UserService

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/")
async def create_user(user_data: UserCreateSchema, session: AsyncSession = Depends(get_async_session)):
    return await UserService(session).create_user(user_data)

@router.get("/")
async def get_users(session: AsyncSession = Depends(get_async_session)):
    return await UserService(session).get_users()

@router.get("/{telegram_id}")
async def get_user(telegram_id: int, session: AsyncSession = Depends(get_async_session)):
    return await UserService(session).get_user(telegram_id)
