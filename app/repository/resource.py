from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PlayerResources, PlayerResourcesStorage, Resource
from app.repository import BaseRepository

RepositoryResource = BaseRepository[Resource]
repository_resource = RepositoryResource(Resource)


def create_storage_resource(
        session: AsyncSession,
        resource_id: int,
        count: int,
        player_base_id: int,
        player_id: int
) -> None:
    storage_resource = PlayerResourcesStorage(
        player_base_id=player_base_id,
        resource_id=resource_id,
        player_id=player_id,
        resource_quantity=count
    )
    session.add(storage_resource)


def create_inventory_resource(session: AsyncSession, resource_id: int, count: int, player_id: int) -> None:
    inventory_resource = PlayerResources(
        resource_id=resource_id,
        player_id=player_id,
        resource_quantity=count
    )
    session.add(inventory_resource)
