import pytest
from faststream import TestApp
from faststream.redis import RedisBroker
from httpx import ASGITransport, AsyncClient
from pytest_asyncio import is_async_test
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from starlette.testclient import TestClient

from app.broker.main import app as faststream_app
from app.core.database import TEST_DATABASE_URL, get_async_session
from app.main import app
from app.models import (BuildingCost, FarmMode, Map, MapObject,
                        MapObjectPosition, Resource, ResourcesZone)
from app.models.base_model import Base

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
        await populate_bd(session)
        yield session
        await session.rollback()
        await session.close()


@pytest.fixture()
async def client(db_session) -> TestClient:
    app.dependency_overrides[get_async_session] = lambda: db_session
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test/"
    ) as ac:
        yield ac


@pytest.fixture
async def test_broker():
    broker = RedisBroker()
    async with TestApp(app=faststream_app):
        yield broker


async def populate_bd(db_session):
    # add map
    map1 = Map(height=111, width=222)
    db_session.add(map1)
    map2 = Map(height=333, width=333)
    db_session.add(map2)
    await db_session.flush()

    # add map object(city) and position
    map_object = MapObject(name="city", type="city", map_id=map1.id, is_farmable=False)
    db_session.add(map_object)
    await db_session.flush()
    map_object_position = MapObjectPosition(x1=11, y1=11, x2=15, y2=15, map_object_id=map_object.id)
    db_session.add(map_object_position)

    # add map object(quarry) and position
    quarry_map_object = MapObject(name="quarry", type="stone", map_id=map1.id, is_farmable=True)
    db_session.add(quarry_map_object)
    await db_session.flush()
    quarry_map_object_position = MapObjectPosition(x1=22, y1=22, x2=25, y2=25, map_object_id=quarry_map_object.id)
    db_session.add(quarry_map_object_position)

    # add map object(sawmill) and position
    sawmill_map_object = MapObject(name="sawmill", type="wood", map_id=map1.id, is_farmable=True)
    db_session.add(sawmill_map_object)
    await db_session.flush()
    sawmill_map_object_position = MapObjectPosition(x1=32, y1=32, x2=35, y2=35, map_object_id=sawmill_map_object.id)
    db_session.add(sawmill_map_object_position)

    # add resources
    wood = Resource(name="wood")
    stone = Resource(name="stone")
    db_session.add(wood)
    db_session.add(stone)
    await db_session.flush()

    # add resources zone
    wood_resource_zone = ResourcesZone(map_object_id=sawmill_map_object.id, resource_id=wood.id, map_id=map1.id)
    db_session.add(wood_resource_zone)
    stone_resource_zone = ResourcesZone(map_object_id=quarry_map_object.id, resource_id=stone.id, map_id=map1.id)
    db_session.add(stone_resource_zone)
    await db_session.flush()

    # add farm modes
    wood_easy_farm_mode = FarmMode(
        mode="easy", total_minutes=1, total_energy=5, total_resources=10, resource_zone_id=wood_resource_zone.id
    )
    db_session.add(wood_easy_farm_mode)

    wood_medium_farm_mode = FarmMode(
        mode="medium", total_minutes=5, total_energy=25, total_resources=50, resource_zone_id=wood_resource_zone.id
    )
    db_session.add(wood_medium_farm_mode)

    wood_hard_farm_mode = FarmMode(
        mode="hard", total_minutes=10, total_energy=50, total_resources=100, resource_zone_id=wood_resource_zone.id
    )
    db_session.add(wood_hard_farm_mode)

    stone_easy_farm_mode = FarmMode(
        mode="easy", total_minutes=1, total_energy=5, total_resources=10, resource_zone_id=stone_resource_zone.id
    )
    db_session.add(stone_easy_farm_mode)

    stone_medium_farm_mode = FarmMode(
        mode="medium", total_minutes=5, total_energy=25, total_resources=50, resource_zone_id=stone_resource_zone.id
    )
    db_session.add(stone_medium_farm_mode)

    stone_hard_farm_mode = FarmMode(
        mode="hard", total_minutes=10, total_energy=50, total_resources=100, resource_zone_id=stone_resource_zone.id
    )
    db_session.add(stone_hard_farm_mode)

    # add building costs
    building_cost = BuildingCost(type="base", resource_id=wood.id, resource_quantity=10)
    db_session.add(building_cost)
    building_cost = BuildingCost(type="base", resource_id=stone.id, resource_quantity=20)
    db_session.add(building_cost)

    await db_session.commit()
