from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.gameplay import FarmSessionSchema
from app.schemas.maps import Resources


class PlayerStatus(Enum):
    WAITING = "waiting"
    FARMING = "farming"
    TRAVELING = "traveling"


class TransferDirection(Enum):
    TO_STORAGE = "to_storage"
    FROM_STORAGE = "from_storage"


class PlayerBaseCreateDBSchema(BaseModel):
    map_object_id: int
    map_id: int
    owner_id: int


class PlayerBaseStorageCreateSchema(BaseModel):
    player_base_id: int
    resource_id: int
    count: int


class PlayerBaseSchema(BaseModel):
    map_object_id: int
    resources: Optional[dict]

    model_config = ConfigDict(from_attributes=True)


class BasePlayerSchema(BaseModel):
    status: str
    health: int
    energy: int

    model_config = ConfigDict(from_attributes=True)


class PlayerSchema(BasePlayerSchema):
    map_object_id: int
    in_base: bool
    resources: Optional[dict]
    base: Optional[PlayerBaseSchema]
    farm_sessions: Optional[FarmSessionSchema]

    model_config = ConfigDict(from_attributes=True)


class PlayerResourcesSchema(BaseModel):
    resource: dict

    model_config = ConfigDict(from_attributes=True)


# class PlayerResponseSchema(PlayerSchema):
#     resources: Optional[dict]
#
#     model_config = ConfigDict(from_attributes=True)


class PlayerCreateSchema(BaseModel):
    map_id: int


class PlayerDBCreateSchema(PlayerCreateSchema):
    player_id: int
    name: str


class PlayerBaseCreateSchema(BaseModel):
    x1: int = Field(ge=0)
    y1: int = Field(ge=0)
    map_id: int


class PlayerBaseStorageCreate(BaseModel):
    player_base_id: int
    resource_id: int


class PlayerTransferItemSchema(BaseModel):
    map_id: int
    item: Resources
    count: int = Field(ge=1)
    direction: TransferDirection
