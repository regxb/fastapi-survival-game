from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.gameplay import FarmSessionSchema, ItemSchemaResponse, ItemSchema
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


class PlayerBaseSchema(BaseModel):
    map_object_id: int
    resources: Optional[dict[str, int]]
    items: Optional[list]

    model_config = ConfigDict(from_attributes=True)


class BasePlayerSchema(BaseModel):
    status: str
    health: int
    energy: int

    model_config = ConfigDict(from_attributes=True)


class PlayerSchema(BaseModel):
    id: int
    name: str
    energy: int
    # resource_multiplier: float
    # energy_multiplier: float
    status: str
    health: int
    inventory_slots: int
    map_id: int
    map_object_id: int
    in_base: bool
    base: Optional[PlayerBaseSchema] = None
    farm_sessions: Optional[FarmSessionSchema] = None
    resources: Optional[dict[str, int]] = None
    items: Optional[list[ItemSchemaResponse]] = None

    model_config = ConfigDict(from_attributes=True)


class PlayerResourcesSchema(BaseModel):
    player_resources: dict[str, int]
    storage_resources: dict[str, int]

    model_config = ConfigDict(from_attributes=True)


class PlayerItemsSchema(BaseModel):
    inventory_items: list
    storage_items: list

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


class PlayerResourcesStorageCreate(BaseModel):
    player_base_id: int
    resource_id: int


class PlayerTransferResourceSchema(BaseModel):
    map_id: int
    resource: Resources
    count: int = Field(ge=1)
    direction: TransferDirection


class PlayerTransferItemSchema(BaseModel):
    map_id: int
    item_id: int
    direction: TransferDirection


class PlayerInventoryResponseSchema(BaseModel):
    items: list

    model_config = ConfigDict(from_attributes=True)
