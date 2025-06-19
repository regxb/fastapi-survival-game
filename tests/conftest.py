import pytest
from httpx import ASGITransport, AsyncClient
from pytest_asyncio import is_async_test
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from starlette.testclient import TestClient

from app.core.database import TEST_DATABASE_URL, get_async_session
from app.main import app
from app.models import (BuildingCost, FarmMode, Inventory, Item, ItemRecipe,
                        Map, MapObject, MapObjectPosition, Player, PlayerBase,
                        PlayerItemStorage, PlayerResources, Resource,
                        ResourcesZone, PlayerResourcesStorage)
from app.models.base import Base

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def pytest_collection_modifyitems(items):
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


@pytest.fixture()
async def connection_test():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture()
async def db_session(connection_test):
    async with async_session_maker() as session:
        yield session
        await session.rollback()
        await session.close()


@pytest.fixture()
async def client(db_session) -> TestClient:
    app.dependency_overrides[get_async_session] = lambda: db_session
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test/", headers={"authorization": "123"}
    ) as ac:
        yield ac


# @pytest.fixture
# async def test_broker():
#     broker = RedisBroker()
#     async with TestApp(app=faststream_app):
#         yield broker


# database fixture

@pytest.fixture
async def map_with_objects(db_session):
    map1 = Map(height=111, width=222)
    db_session.add(map1)
    await db_session.flush()

    map_object1 = MapObject(name="city", type="city", map_id=map1.id, is_farmable=False)
    db_session.add(map_object1)
    await db_session.flush()
    map_object_position = MapObjectPosition(x1=11, y1=11, x2=15, y2=15, map_object_id=map_object1.id)
    db_session.add(map_object_position)

    map_object2 = MapObject(name="sawmill", type="wood", map_id=map1.id, is_farmable=True)
    db_session.add(map_object2)
    await db_session.flush()
    sawmill_map_object_position = MapObjectPosition(x1=32, y1=32, x2=35, y2=35, map_object_id=map_object2.id)
    db_session.add(sawmill_map_object_position)

    await db_session.commit()

    return [map_object1, map_object2]


@pytest.fixture
async def resources(db_session):
    wood = Resource(name="wood", icon="icon.svg")
    stone = Resource(name="stone", icon="icon.svg")
    db_session.add(wood)
    db_session.add(stone)
    await db_session.commit()


@pytest.fixture
async def resources_zone(db_session, resources):
    wood_resource_zone = ResourcesZone(map_object_id=2, resource_id=1, map_id=1)
    db_session.add(wood_resource_zone)
    await db_session.commit()
    return wood_resource_zone


@pytest.fixture
async def farming_mode(db_session, resources_zone):
    wood_easy_farm_mode = FarmMode(
        mode="easy", total_minutes=1, total_energy=5, total_resources=10, resource_zone_id=1
    )
    db_session.add(wood_easy_farm_mode)
    await db_session.commit()


@pytest.fixture
async def building_cost(db_session, resources):
    building_cost1 = BuildingCost(type="base", resource_id=1, resource_quantity=10)
    db_session.add(building_cost1)
    building_cost2 = BuildingCost(type="base", resource_id=2, resource_quantity=20)
    db_session.add(building_cost2)
    await db_session.commit()
    return [building_cost1, building_cost2]


@pytest.fixture
async def player(db_session, map_with_objects):
    player = Player(map_id=1, player_id=111, name="test_name")
    db_session.add(player)
    await db_session.commit()
    return player


@pytest.fixture
async def player_resources(db_session, player, resources):
    player_resources1 = PlayerResources(player_id=1, resource_id=1, resource_quantity=10)
    db_session.add(player_resources1)
    player_resources2 = PlayerResources(player_id=1, resource_id=2, resource_quantity=20)
    db_session.add(player_resources2)
    await db_session.commit()
    return [player_resources1, player_resources2]

@pytest.fixture
async def map_(db_session):
    map_ = Map(height=333, width=333)
    db_session.add(map_)
    await db_session.commit()
    return map_

@pytest.fixture
async def player_base(db_session, player, map_):
    player_base = PlayerBase(map_object_id=1, map_id=1, owner_id=1)
    db_session.add(player_base)
    await db_session.commit()
    return player_base

@pytest.fixture
async def player_base_with_resources(db_session, player, map_, resources):
    player_base = PlayerBase(map_object_id=1, map_id=1, owner_id=1)
    db_session.add(player_base)
    player_item_storage = PlayerResourcesStorage(resource_id=1, player_base_id=1, player_id=1, resource_quantity=22)
    db_session.add(player_item_storage)
    await db_session.commit()
    return player_base

@pytest.fixture
async def player_outside_base(db_session, player, map_):
    player_base = PlayerBase(map_object_id=2, map_id=1, owner_id=1)
    db_session.add(player_base)
    await db_session.commit()
    return player_base

@pytest.fixture
async def player_with_items(db_session, player, item):
    inventory = Inventory(player_id=1, item_id=1, tier=1, count=1)
    db_session.add(inventory)
    await db_session.commit()
    return inventory


@pytest.fixture
async def item(db_session):
    item = Item(name="test_name", icon="icon.svg", max_count=1, type="test")
    db_session.add(item)
    await db_session.commit()


@pytest.fixture
async def items_recipe(db_session, item, resources):
    item_recipe = ItemRecipe(item_id=1, resource_id=1, resource_quantity=5)
    db_session.add(item_recipe)
    await db_session.commit()
    # return item_recipe


@pytest.fixture
async def player_base_storage_with_items(db_session, player_base, item):
    item_storage = PlayerItemStorage(item_id=1, player_id=1, player_base_id=1)
    db_session.add(item_storage)
    await db_session.commit()
    return item_storage


@pytest.fixture
async def player_with_resources(db_session, player, resources):
    player_resources = PlayerResources(player_id=1, resource_id=1, resource_quantity=10)
    db_session.add(player_resources)
    player_resources = PlayerResources(player_id=1, resource_id=2, resource_quantity=20)
    db_session.add(player_resources)
    await db_session.commit()
