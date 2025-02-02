from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.resource import ResourceSchema
from app.schemas.farm import FarmModeLevelSchema


class ObjectType(Enum):
    WOOD = "wood"
    STONE = "stone"
    IRON = "iron"
    CITY = "city"
    BASE = "base"


class Resources(Enum):
    WOOD = "wood"
    STONE = "stone"
    IRON = "iron"


class MapCreateSchema(BaseModel):
    height: int = Field(gt=0)
    width: int = Field(gt=0)


class MapObjectCreateSchema(BaseModel):
    name: str
    map_id: int
    is_farmable: bool
    type: str


class ResourceZoneSchema(BaseModel):
    resource: Optional[ResourceSchema]
    farm_modes: Optional[list[FarmModeLevelSchema]]

    model_config = ConfigDict(from_attributes=True)


class MapObjectPositionSchema(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int
    map_object_id: int

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
