from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PlayerBaseCreateDBSchema(BaseModel):
    map_object_id: int
    map_id: int
    owner_id: int


class PlayerBaseSchema(BaseModel):
    map_object_id: int

    model_config = ConfigDict(from_attributes=True)


class BasePlayerSchema(BaseModel):
    status: str
    health: int
    energy: int

    model_config = ConfigDict(from_attributes=True)


class PlayerSchema(BasePlayerSchema):
    map_object_id: int
    in_base: bool
    base: Optional[PlayerBaseSchema]

    model_config = ConfigDict(from_attributes=True)


class PlayerResourcesSchema(BaseModel):
    resource: dict

    model_config = ConfigDict(from_attributes=True)


class PlayerResponseSchema(PlayerSchema):
    resources: Optional[dict]

    model_config = ConfigDict(from_attributes=True)


class PlayerCreateSchema(BaseModel):
    map_id: int


class PlayerDBCreateSchema(PlayerCreateSchema):
    player_id: int
    name: str


class PlayerBaseCreateSchema(BaseModel):
    x1: int = Field(ge=0)
    y1: int = Field(ge=0)
    map_id: int
