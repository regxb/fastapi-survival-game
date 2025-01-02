from aiogram.utils.web_app import WebAppInitData
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.users import base_crud_user, get_user_with_players
from app.schemas.players import BasePlayerSchema
from app.schemas.users import BaseUserSchema, UserSchemaResponse


class UserService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: WebAppInitData) -> BaseUserSchema:
        user_schema = BaseUserSchema(
            telegram_id=user.user.id,
            username=user.user.username,
            photo_url=user.user.photo_url
        )
        user = await base_crud_user.create(self.session, user_schema)
        return user

    async def get_users(self, offset: int = 0, limit: int = 100):
        users = await base_crud_user.get_multi(self.session, offset=offset, limit=limit)
        return users

    async def get_user(self, telegram_id: int):
        user = await get_user_with_players(self.session, telegram_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        user_response = UserSchemaResponse.model_validate(user)
        return user_response

    async def update_user(self, user_data: BaseUserSchema):
        user = await base_crud_user.update(self.session, user_data, telegram_id=user_data.telegram_id)
        return user