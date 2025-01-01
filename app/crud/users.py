from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.crud.base import CRUDBase
from app.models.players import Player
from app.models.users import User
from app.schemas.users import BaseUserSchema

CRUDUsers = CRUDBase[User, BaseUserSchema]
base_crud_user = CRUDUsers(User)


async def get_user_with_players(session: AsyncSession, telegram_id: int):
    stmt = select(User).where(User.telegram_id == telegram_id).options(selectinload(User.players))
    result = await session.execute(stmt)
    return result.scalar_one_or_none()