from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.gameplay import ResourceSchema


class ObjectType(Enum):
    WOOD = "wood"
    STONE = "stone"
    IRON = "iron"
    CITY = "city"
    BASE = "base"


class MapCreateSchema(BaseModel):
    height: int = Field(gt=0)
    width: int = Field(gt=0)


class MapObjectCreateSchema(BaseModel):
    x1: int = Field(ge=0)
    y1: int = Field(ge=0)
    map_id: int


class ResourceZoneSchema(BaseModel):
    resource: Optional[ResourceSchema]

    model_config = ConfigDict(from_attributes=True)


class MapObjectPositionSchema(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int

    model_config = ConfigDict(from_attributes=True)


class MapObjectResponseSchema(BaseModel):
    name: str
    id: int
    type: ObjectType
    is_farmable: bool
    position: Optional[MapObjectPositionSchema]
    resource_zone: Optional[ResourceZoneSchema]

    model_config = ConfigDict(from_attributes=True)


class BaseMapSchema(BaseModel):
    id: int
    height: int
    width: int

    model_config = ConfigDict(from_attributes=True)


class MapResponseSchema(BaseMapSchema):
    map_objects: Optional[list[MapObjectResponseSchema]] = None

    model_config = ConfigDict(from_attributes=True)
