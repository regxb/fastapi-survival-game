import enum
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.gameplay import ResourceSchema
from app.schemas.maps import MapObjectPositionSchema


class PlayerCreateSchema(BaseModel):
    map_id: int


class BasePlayerSchema(BaseModel):
    id: int
    map_id: int
    map_object_id: int
    status: str
    health: int
    energy: int

    model_config = ConfigDict(from_attributes=True)


class PlayerHouseSchema(BaseModel):
    defense_level: int
    position: Optional[MapObjectPositionSchema]


class PlayerResourcesSchema(BaseModel):
    resource_id: int
    count: int
    model_config = ConfigDict(from_attributes=True)


class PlayerResponseSchema(BaseModel):
    id: int
    user_id: int
    map_id: int
    health: int
    energy: int
    map_object_id: int
    status: str
    resources: Optional[list[PlayerResourcesSchema]]

    model_config = ConfigDict(from_attributes=True)
