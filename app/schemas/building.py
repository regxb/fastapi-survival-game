from enum import Enum

from pydantic import BaseModel


class BuildingType(Enum):
    BASE = "base"


class BuildingCostSchema(BaseModel):
    resources: dict[str, int]
    can_build: bool


class BuildingCostResponseSchema(BaseModel):
    resources: list[BuildingCostSchema]
