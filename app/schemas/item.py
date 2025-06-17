from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.base import TransferDirection
from app.schemas.resource import ResourceCountSchema


class ItemLocation(Enum):
    inventory = "inventory"
    storage = "storage"


class ItemTypeSchema(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class ItemSchema(BaseModel):
    id: int
    name: str
    tier: int
    icon: str
    type: Optional[str]

    model_config = ConfigDict(populate_by_name=True)


class ItemSchemaResponse(ItemSchema):
    id: int
    active_item: bool = False


class CraftItemSchema(BaseModel):
    map_id: int
    item_id: int


class RecipeSchema(BaseModel):
    resources: list[ResourceCountSchema]


class ItemResponseSchema(BaseModel):
    id: int
    name: str
    can_craft: bool
    icon: str
    recipe: RecipeSchema


class InventoryItemCreateSchema(BaseModel):
    item_id: int
    count: int
    tier: int
    player_id: int

    model_config = ConfigDict(from_attributes=True)


class StorageItemCreateSchema(BaseModel):
    player_base_id: int
    item_id: int
    count: int
    tier: int
    player_id: int

    model_config = ConfigDict(from_attributes=True)


class TransferItemSchema(BaseModel):
    map_id: int
    item_id: int
    count: int
    direction: TransferDirection


class EquipItemSchema(BaseModel):
    map_id: int
    item_id: int
