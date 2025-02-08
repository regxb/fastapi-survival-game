from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import TransferDirection


class ResourceSchema(BaseModel):
    id: int
    name: str
    icon: str

    model_config = ConfigDict(from_attributes=True)

class ResourceCountSchema(ResourceSchema):
    count: int


class TransferResourceSchema(BaseModel):
    map_id: int
    resource_id: int
    count: int = Field(ge=1)
    direction: TransferDirection
