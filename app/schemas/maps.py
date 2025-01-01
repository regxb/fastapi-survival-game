from enum import Enum

from pydantic import BaseModel, PrivateAttr, model_validator, Field


class ObjectType(Enum):
    WOOD = "wood"
    STONE = "stone"
    IRON = "iron"


class MapCreateSchema(BaseModel):
    size: int = Field(gt=0)


class MapObjectCreateSchema(BaseModel):
    name: str
    x1: int = Field(ge=0)
    y1: int = Field(ge=0)
    x2: int = Field(ge=0)
    y2: int = Field(ge=0)
    map_id: int

    @model_validator(mode="before")
    def check_different_coordinates(cls, values):
        if values['x1'] >= values['x2'] or values['y1'] >= values['y2']:
            raise ValueError("Second coordinates must be greater than the first")
        return values


class MapObjectResponseSchema(BaseModel):
    name: str
    map_object_id: int
    type: ObjectType
    x1: int
    y1: int
    x2: int
    y2: int


class MapResponseSchema(BaseModel):
    size: int
    map_objects: list[MapObjectResponseSchema]
