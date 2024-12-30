from typing import Optional

from pydantic import BaseModel, PrivateAttr


class PlayerCreateSchema(BaseModel):
    username: str
    telegram_id: int


class PlayerDBSchema(BaseModel):
    username: str
    user_id: int
