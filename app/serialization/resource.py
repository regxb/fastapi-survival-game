from typing import List, Optional

from app.schemas import ResourceCountSchema


def serialize_resources(resources) -> Optional[List[ResourceCountSchema]]:
    filtered_resources = [
        ResourceCountSchema(id=resource.resource.id,
                            name=resource.resource.name,
                            icon=resource.resource.icon,
                            count=resource.resource_quantity)
        for resource in resources
        if resource.resource_quantity > 0
    ]
    return filtered_resources or None