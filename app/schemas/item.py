from pydantic import BaseModel, ConfigDict

from app.schemas.resource import ResourceCountSchema


class ItemSchema(BaseModel):
    item_id: int
    name: str
    tier: int
    icon: str


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


class InventoryItemCreateSchema(BaseModel):
    item_id: int
    tier: int
    player_id: int

    model_config = ConfigDict(from_attributes=True)


class StorageItemCreateSchema(BaseModel):
    player_base_id: int
    item_id: int
    tier: int
    player_id: int

    model_config = ConfigDict(from_attributes=True)
