from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Mapped

from app.schemas.farm import FarmSessionSchema
from app.schemas.item import ItemSchemaResponse, ItemSchema
from app.schemas.resource import ResourceCountSchema


class PlayerStatus(Enum):
    WAITING = "waiting"
    FARMING = "farming"
    TRAVELING = "traveling"


class PlayerBaseCreateDBSchema(BaseModel):
    map_object_id: int
    map_id: int
    owner_id: int


class PlayerBaseSchema(BaseModel):
    map_object_id: int
    resources: Optional[list[ResourceCountSchema]] = None
    # items: Optional[list]

    model_config = ConfigDict(from_attributes=True)


class BasePlayerSchema(BaseModel):
    status: str
    health: int
    energy: int

    model_config = ConfigDict(from_attributes=True)


class PlayerStatsSchema(BaseModel):
    damage: int
    armor: int

    model_config = ConfigDict(from_attributes=True)


class PlayerSchema(BaseModel):
    id: int
    name: str
    energy: int
    status: str
    health: int
    inventory_slots: int
    map_id: int
    map_object_id: int
    in_base: bool
    stats: PlayerStatsSchema
    base: Optional[PlayerBaseSchema] = None
    farm_sessions: Optional[FarmSessionSchema] = None
    resources: Optional[list[ResourceCountSchema]] = None
    inventory_items: Optional[list[ItemSchema]] = None
    equip_items: Optional[list[ItemSchema]] = None

    model_config = ConfigDict(from_attributes=True)


class PlayerResourcesSchema(BaseModel):
    player_resources: Optional[list] = None
    storage_resources: Optional[list] = None

    model_config = ConfigDict(from_attributes=True)


class PlayerItemsSchema(BaseModel):
    inventory_items: Optional[list] = None
    storage_items: Optional[list] = None
    equip_items: Optional[list] = None

    model_config = ConfigDict(from_attributes=True)


class PlayerEquipItemResponseSchema(BaseModel):
    stats: PlayerStatsSchema
    items: Optional[PlayerItemsSchema] = None


class PlayerCreateSchema(BaseModel):
    map_id: int


class PlayerDBCreateSchema(PlayerCreateSchema):
    player_id: int
    name: Optional[str] = None


class PlayerBaseCreateSchema(BaseModel):
    x1: int = Field(ge=0)
    y1: int = Field(ge=0)
    map_id: int


class ResourcesStorageCreate(BaseModel):
    player_base_id: int
    resource_id: int
    player_id: int
    resource_quantity: int


class PlayerMoveSchema(BaseModel):
    map_id: int
    map_object_id: int


class PlayerMoveResponseSchema(BaseModel):
    player_id: int
    new_map_object_id: int
