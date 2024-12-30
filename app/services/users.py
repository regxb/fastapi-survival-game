from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.users import base_crud_user
from app.schemas.users import UserCreateSchema


class UserService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: UserCreateSchema) -> UserCreateSchema:
        user = await base_crud_user.create(self.session, user)
        return user

    async def get_users(self):
        users = await base_crud_user.get_multi(self.session)
        return users

    async def get_user(self, telegram_id: int):
        user = await base_crud_user.get(self.session, telegram_id=telegram_id)
        return user

    async def update_user(self, user_data: UserCreateSchema):
        user = await base_crud_user.update(self.session, user_data, telegram_id=user_data.telegram_id)
        return user