from typing import Sequence

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, Mapped

from app.models import Inventory, Player, PlayerBase, PlayerResources, MapObject, ResourcesZone, EquipItem, Item
from app.models.player import PlayerItemStorage, PlayerResourcesStorage, PlayerStats
from app.repository.base import BaseRepository

PlayerRepository = BaseRepository[Player]
player_repository = PlayerRepository(Player)

PlayerBaseRepository = BaseRepository[PlayerBase]
player_base_repository = PlayerBaseRepository(PlayerBase)

PlayerResourcesRepository = BaseRepository[PlayerResources]
player_resource_repository = PlayerResourcesRepository(PlayerResources)

PlayerResourcesStorageRepository = BaseRepository[PlayerResourcesStorage]
player_resources_storage_repository = PlayerResourcesStorageRepository(PlayerResourcesStorage)

PlayerItemStorageRepository = BaseRepository[PlayerItemStorage]
player_item_storage_repository = PlayerItemStorageRepository(PlayerItemStorage)

InventoryRepository = BaseRepository[Inventory]
inventory_repository = InventoryRepository(Inventory)


def create_new_player(session: AsyncSession, telegram_id: int, name: str, map_id: int):
    player = Player(player_id=telegram_id, name=name, map_id=map_id)
    session.add(player)
    return player


def create_player_stats(session: AsyncSession, player_id: int):
    player_stats = PlayerStats(player_id=player_id)
    session.add(player_stats)
    return player_stats


async def get_all_players(session: AsyncSession, telegram_id: int):
    stmt = select(Player).where(Player.player_id == telegram_id).options(joinedload(Player.base))
    result = await session.execute(stmt)
    return result.scalars().unique().all()


async def get_player_with_all_items(session: AsyncSession, player_id: int | Mapped[int]):
    stmt = (
        select(Player)
        .where(Player.id == player_id)
        .options(
            joinedload(Player.inventory).joinedload(Inventory.item).joinedload(Item.stats),
            joinedload(Player.base).joinedload(PlayerBase.items).joinedload(PlayerItemStorage.item).joinedload(
                Item.stats),
            joinedload(Player.equip_item).joinedload(EquipItem.item).joinedload(Item.stats),
            joinedload(Player.stats)
        )
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_player_with_items(session: AsyncSession, telegram_id: int, map_id: int) -> Player | None:
    stmt = (
        select(Player)
        .where(and_(Player.player_id == telegram_id, Player.map_id == map_id))
        .options(
            joinedload(Player.inventory).joinedload(Inventory.item).joinedload(Item.stats),
            joinedload(Player.base).joinedload(PlayerBase.items).joinedload(PlayerItemStorage.item).joinedload(
                Item.stats)
        )
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_player_with_base_and_resources(session: AsyncSession, telegram_id: int, map_id: int) -> Player | None:
    stmt = (
        select(Player)
        .where(and_(Player.player_id == telegram_id, Player.map_id == map_id))
        .options(joinedload(Player.base), joinedload(Player.resources)
                 )
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_player_with_resources_for_craft(session: AsyncSession, telegram_id: int, map_id: int):
    stmt = (
        select(Player)
        .where(and_(Player.player_id == telegram_id, Player.map_id == map_id))
        .options(
            joinedload(Player.resources),
            joinedload(Player.inventory).joinedload(Inventory.item)
        )
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_player_with_resources_for_transfer(
        session: AsyncSession, telegram_id: int, map_id: int, resource_id: int
) -> Player:
    stmt = (
        select(Player)
        .where(and_(Player.player_id == telegram_id, Player.map_id == map_id))
        .options(
            joinedload(Player.resources.and_(PlayerResources.resource_id == resource_id))
            .joinedload(PlayerResources.resource),
            joinedload(Player.base)
            .joinedload(PlayerBase.resources.and_(PlayerResourcesStorage.resource_id == resource_id))
        )
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_player_with_all_resources(session: AsyncSession, telegram_id: int, map_id: int) -> Player:
    stmt = (
        select(Player)
        .where(and_(Player.player_id == telegram_id, Player.map_id == map_id))
        .options(
            joinedload(Player.resources).joinedload(PlayerResources.resource),
            joinedload(Player.base).joinedload(PlayerBase.resources)
        )
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_player_inventory(session: AsyncSession, player_id: int) -> Sequence[Inventory]:
    stmt = (
        select(Inventory)
        .where(Inventory.player_id == player_id)
        .options(joinedload(Inventory.item).joinedload(Item.stats)))
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_player_with_equip_items(session: AsyncSession, telegram_id: int, map_id: int):
    stmt = (
        select(Player)
        .where(and_(Player.player_id == telegram_id, Player.map_id == map_id))
        .options(joinedload(Player.equip_item).joinedload(EquipItem.item))
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def create_player_inventory(session: AsyncSession, player_id: int, item_id: int) -> Inventory:
    player_inventory = Inventory(player_id=player_id, item_id=item_id)
    session.add(player_inventory)
    return player_inventory


async def get_player_with_resources_and_items(session: AsyncSession, telegram_id: int, map_id: int):
    stmt = (
        select(Player)
        .where(and_(Player.player_id == telegram_id, Player.map_id == map_id))
        .options(
            joinedload(Player.resources).joinedload(PlayerResources.resource),
            joinedload(Player.stats),
            joinedload(Player.equip_item).joinedload(EquipItem.item).joinedload(Item.stats),
            joinedload(Player.base).joinedload(PlayerBase.resources),
            joinedload(Player.base).joinedload(PlayerBase.items).joinedload(PlayerItemStorage.item).joinedload(
                Item.stats),
            joinedload(Player.inventory).joinedload(Inventory.item).joinedload(Item.stats)
        )
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_player_with_base(session: AsyncSession, telegram_id: int, map_id: int):
    stmt = (
        select(Player)
        .where(and_(Player.player_id == telegram_id, Player.map_id == map_id))
        .options(joinedload(Player.base))
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_player_with_resources(session: AsyncSession, telegram_id: int, map_id: int):
    stmt = (
        select(Player)
        .where(and_(Player.player_id == telegram_id, Player.map_id == map_id))
        .options(joinedload(Player.resources).joinedload(PlayerResources.resource))
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_player_with_resources_and_zone_resources(session: AsyncSession, telegram_id: int, map_id: int):
    stmt = (
        select(Player)
        .where(and_(Player.player_id == telegram_id, Player.map_id == map_id))
        .options(
            joinedload(Player.map_object).joinedload(MapObject.resource_zone).joinedload(ResourcesZone.resource),
            joinedload(Player.resources)
        )
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_player_with_specific_resource(session: AsyncSession, player_id: int, resource_id: int):
    stmt = (
        select(Player)
        .where(Player.id == player_id)
        .options(joinedload(Player.resources.and_(PlayerResources.resource_id == resource_id)))
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_player_resource_quantity(session: AsyncSession, player_id: int, resource_id: int):
    stmt = (select(PlayerResources.resource_quantity)
            .where(and_(PlayerResources.player_id == player_id, PlayerResources.resource_id == resource_id)
                   )
            )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_player_with_specific_item(session: AsyncSession, telegram_id: int, map_id: int, item_id: int):
    stmt = (
        select(Player)
        .where(and_(Player.player_id == telegram_id, Player.map_id == map_id))
        .options(
            joinedload(Player.inventory.and_(Inventory.id == item_id)).joinedload(Inventory.item),
        )
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_specific_player_equip_items(session: AsyncSession, player_id: int, item_type: str):
    stmt = (
        select(Player).where(Player.id == player_id)
        .options(joinedload(Player.equip_item).joinedload(EquipItem.item.and_(Item.type == item_type)))
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_inventory_item_with_stats(session: AsyncSession, player_id: int, item_id: int):
    stmt = (
        select(Inventory)
        .where(and_(Inventory.player_id == player_id, Inventory.id == item_id))
        .options(joinedload(Inventory.item).joinedload(Item.stats))
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_equip_item_with_specific_type(session: AsyncSession, player_id: int, item_type: str):
    stmt = (
        select(EquipItem)
        .where(and_(EquipItem.player_id == player_id))
        .options(joinedload(EquipItem.item.and_(Item.type == item_type)).joinedload(Item.stats))
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_player_with_stats(session: AsyncSession, telegram_id: int, map_id: int):
    stmt = (
        select(Player)
        .where(and_(Player.player_id == telegram_id, Player.map_id == map_id))
        .options(joinedload(Player.stats))
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


async def get_player_with_inventory_items(session: AsyncSession, telegram_id: int, map_id: int):
    stmt = (
        select(Player)
        .where(and_(Player.player_id == telegram_id, Player.map_id == map_id))
        .options(
            joinedload(Player.stats),
            joinedload(Player.inventory).joinedload(Inventory.item).joinedload(Item.stats),
        )
    )
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()
