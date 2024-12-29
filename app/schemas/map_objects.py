from pydantic import BaseModel


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
    x: int
    y: int
    height: int
    width: int


class MapResponseSchema(BaseModel):
    size: int
    map_objects: list[MapObjectResponseSchema]
