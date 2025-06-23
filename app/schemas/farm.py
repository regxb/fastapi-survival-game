from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class FarmStatus(Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class FarmModeEnum(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


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


class StartFarmResourcesSchema(BaseModel):
    map_id: int
    total_minutes: int = Field(ge=1)

class StopFarmResourcesSchema(BaseModel):
    map_id: int


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
