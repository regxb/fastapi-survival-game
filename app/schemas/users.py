from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.players import BasePlayerSchema


class BaseUserSchema(BaseModel):
    telegram_id:int
    username: str
    photo_url: str

    model_config = ConfigDict(from_attributes=True)


class UserSchemaResponse(BaseUserSchema):
    players: list[BasePlayerSchema]
