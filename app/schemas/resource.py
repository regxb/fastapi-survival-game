from pydantic import BaseModel, ConfigDict


class ResourceSchema(BaseModel):
    id: int
    name: str
    icon: str

    model_config = ConfigDict(from_attributes=True)

class ResourceCountSchema(ResourceSchema):
    count: int