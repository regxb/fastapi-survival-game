from pydantic import BaseModel


class PlayerMoveSchema(BaseModel):
    telegram_id: int
    map_object_id: int
