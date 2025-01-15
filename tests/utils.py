from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Player, PlayerResources, PlayerBase, Inventory
from app.models.gameplay_model import Item, ItemRecipe
from app.models.player_model import PlayerItemStorage


async def create_player(session: AsyncSession):
    player = Player(map_id=1, player_id=111, name="test_name")
    session.add(player)
    await session.commit()


async def create_players_with_resources(session: AsyncSession):
    player = Player(map_id=1, player_id=111, name="test_name")
    session.add(player)
    await session.flush()
    player_resources = PlayerResources(player_id=player.id, resource_id=1, resource_quantity=10)
    session.add(player_resources)
    player_resources = PlayerResources(player_id=player.id, resource_id=2, resource_quantity=20)
    session.add(player_resources)
    await session.commit()
    await session.refresh(player)
    return player


async def add_item_to_player(session: AsyncSession):
    inventory = Inventory(player_id=1, item_id=1, tier=1)
    session.add(inventory)
    await session.commit()
    return inventory


async def create_player_outside_base(session: AsyncSession):
    player_base = PlayerBase(map_object_id=2, map_id=1, owner_id=1)
    session.add(player_base)
    await session.commit()


async def create_player_base(session: AsyncSession):
    player_base = PlayerBase(map_object_id=1, map_id=1, owner_id=1)
    session.add(player_base)
    await session.commit()


async def create_low_cost_item_with_recipe(session: AsyncSession):
    item = Item(name="test_name")
    session.add(item)
    await session.flush()
    item_recipe = ItemRecipe(item_id=item.id, resource_id=1, resource_quantity=5)
    session.add(item_recipe)
    await session.commit()
    return item


async def create_high_cost_item_with_recipe(session: AsyncSession):
    item = Item(name="test_name")
    session.add(item)
    await session.flush()
    item_recipe = ItemRecipe(item_id=item.id, resource_id=1, resource_quantity=500)
    session.add(item_recipe)
    await session.commit()


async def add_item_to_player_storage(session: AsyncSession):
    item_storage = PlayerItemStorage(item_id=1, player_id=1, player_base_id=1)
    session.add(item_storage)
    await session.commit()
