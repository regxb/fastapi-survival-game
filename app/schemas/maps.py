from enum import Enum

from pydantic import BaseModel, PrivateAttr, model_validator, Field


class ObjectType(Enum):
    WOOD = "wood"
    STONE = "stone"
    IRON = "iron"
    CITY = "city"
    BASE = "base"


class MapResponseSchema(BaseModel):
    id: int
    height: int
    width: int


class MapCreateSchema(BaseModel):
    height: int = Field(gt=0)
    width: int = Field(gt=0)


class MapObjectCreateSchema(BaseModel):
    name: str
    x1: int = Field(ge=0)
    y1: int = Field(ge=0)
    map_id: int


class MapObjectResponseSchema(BaseModel):
    name: str
    map_object_id: int
    type: ObjectType
    is_farmable: bool
    x1: int
    y1: int
    x2: int
    y2: int


class MapsObjectsResponseSchema(BaseModel):
    height: int
    width: int
    map_objects: list[MapObjectResponseSchema]
