from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Inventory, Item, ItemRecipe, PlayerItemStorage, EquipItem
from app.repository import BaseRepository

ItemRepository = BaseRepository[Item]
item_repository = ItemRepository(Item)

EquipItemRepository = BaseRepository[EquipItem]
equip_item_repository = EquipItemRepository(EquipItem)


async def get_items_for_craft(session: AsyncSession):
    stmt = select(Item).options(joinedload(Item.recipe).joinedload(ItemRecipe.resource))
    result = await session.execute(stmt)
    return result.scalars().unique().all()


async def get_item_for_craft(session: AsyncSession, item_id: int):
    stmt = select(Item).where(Item.id == item_id).options(joinedload(Item.recipe).joinedload(ItemRecipe.resource))
    result = await session.execute(stmt)
    return result.unique().scalar_one_or_none()


def create_storage_item(
        session: AsyncSession, item_id: int, count: int, player_base_id: int, player_id: int, tier: int = 1
):
    item = PlayerItemStorage(item_id=item_id, count=count, player_base_id=player_base_id, player_id=player_id, tier=tier)
    session.add(item)
    return item


def create_inventory_item(session: AsyncSession, item_id: int, player_id: int, tier: int=1, count: int=1):
    item = Inventory(item_id=item_id, count=count, player_id=player_id, tier=tier)
    session.add(item)
    return item


def create_equip_item(session: AsyncSession, item_id: int, player_id: int, tier: int=1):
    item = EquipItem(item_id=item_id, player_id=player_id, tier=tier)
    session.add(item)
    return item

async def get_specific_equip_item(session: AsyncSession, player_id: int, item_id: int):
    stmt = (select(EquipItem).where(and_(EquipItem.player_id == player_id, EquipItem.item_id == item_id)))
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
