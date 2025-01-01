from pydantic import BaseModel


class PlayerMoveSchema(BaseModel):
    map_id: int
    map_object_id: int
