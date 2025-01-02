import enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PlayerCreateSchema(BaseModel):
    map_id: int


class BasePlayerSchema(BaseModel):
    id: int
    map_id: int

    model_config = ConfigDict(from_attributes=True)


class PlayerResponseSchema(BaseModel):
    id: int
    user_id: int
    map_id: int
    health: int
    map_object_name: str
    map_object_id: int

    model_config = ConfigDict(from_attributes=True)
