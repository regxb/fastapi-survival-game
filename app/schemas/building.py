from enum import Enum

from pydantic import BaseModel, ConfigDict

from app.schemas.resource import ResourceSchema


class BuildingType(Enum):
    BASE = "base"


class BuildingCostSchema(BaseModel):
    resource: ResourceSchema
    resource_quantity: int
    id: int
    model_config = ConfigDict(from_attributes=True)


class BuildingCostResponseSchema(BaseModel):
    resources: list[BuildingCostSchema]
    can_build: bool
