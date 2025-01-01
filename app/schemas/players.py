from typing import Optional

from pydantic import BaseModel


class PlayerCreateSchema(BaseModel):
    map_id: int


class PlayerCreateDB(BaseModel):
    user_id: int
    map_id: int


class PlayerResponseSchema(BaseModel):
    id: int
    user_id: int
    map_id: int
    health: int
    map_object_name: str
    x1: Optional[int]
    y1: Optional[int]
    x2: Optional[int]
    y2: Optional[int]
