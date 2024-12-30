from pydantic import BaseModel


class MapCreateSchema(BaseModel):
    size: int


class MapObjectCreateSchema(BaseModel):
    name: str
    x: int
    y: int
    height: int
    width: int
    map_id: int
    type_id: int


class MapObjectResponseSchema(BaseModel):
    type: str
    x1: int
    y1: int
    x2: int
    y2: int


class MapResponseSchema(BaseModel):
    size: int
    map_objects: list[MapObjectResponseSchema]
