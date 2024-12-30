from typing import Optional

from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    telegram_id:int
    username: str
    photo_url: str
