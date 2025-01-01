from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.users import base_crud_user
from app.schemas.users import UserCreateSchema


class UserService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: dict) -> UserCreateSchema:
        user_schema = UserCreateSchema(telegram_id=user["id"], username=user["username"], photo_url=user["photo_url"])
        user = await base_crud_user.create(self.session, user_schema)
        return user

    async def get_users(self, offset: int = 0, limit: int = 100):
        users = await base_crud_user.get_multi(self.session, offset=offset, limit=limit)
        return users

    async def get_user(self, telegram_id: int):
        user = await base_crud_user.get_by_id(self.session, telegram_id)
        return user

    async def update_user(self, user_data: UserCreateSchema):
        user = await base_crud_user.update(self.session, user_data, telegram_id=user_data.telegram_id)
        return user