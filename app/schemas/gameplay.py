from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class FarmStatus(Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class FarmModeEnum(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class BuildingType(Enum):
    BASE = "base"


class PlayerMoveSchema(BaseModel):
    map_id: int
    map_object_id: int


class PlayerMoveResponseSchema(BaseModel):
    player_id: int
    new_map_object_id: int


class ResourceSchema(BaseModel):
    id: int
    name: str
    icon: str

    model_config = ConfigDict(from_attributes=True)


class ResourceCountSchema(ResourceSchema):
    count: int


class FarmResourcesSchema(BaseModel):
    map_id: int
    mode: FarmModeEnum


class FarmModeLevelSchema(BaseModel):
    mode: FarmModeEnum
    total_minutes: int
    total_energy: int
    total_resources: int

    model_config = ConfigDict(from_attributes=True)


class FarmModeSchema(BaseModel):
    player_resource_multiplier: int
    player_energy_multiplier: int
    farm_modes: list[FarmModeLevelSchema]

    model_config = ConfigDict(from_attributes=True)


class FarmSessionCreateSchema(BaseModel):
    map_id: int
    resource_id: int
    player_id: int
    start_time: datetime
    end_time: datetime


class FarmSessionSchema(BaseModel):
    total_seconds: int
    seconds_pass: int

    model_config = ConfigDict(from_attributes=True)


class BuildingCostSchema(BaseModel):
    resources: dict[str, int]
    can_build: bool


class BuildingCostResponseSchema(BaseModel):
    resources: list[BuildingCostSchema]


class ItemSchema(BaseModel):
    item_id: int
    name: str
    tier: int
    icon: str


class InventoryItemCreateSchema(BaseModel):
    item_id: int
    tier: int
    player_id: int

    model_config = ConfigDict(from_attributes=True)


class ItemStorageCreateSchema(BaseModel):
    player_base_id: int
    item_id: int
    tier: int
    player_id: int

    model_config = ConfigDict(from_attributes=True)


class ItemSchemaResponse(ItemSchema):
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
