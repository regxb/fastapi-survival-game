import pytest

from app.models import Player
from tests.utils import create_player


@pytest.mark.asyncio
async def test_create_player(client, db_session):
    response = await client.post("/player/", json={"map_id": 1})
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["map_object_id"] == 1
    assert response_json["in_base"] == False
    assert not response_json["resources"]


@pytest.mark.asyncio
async def test_get_player(client, db_session):
    await create_player(db_session)
    response = await client.get("/player/1/")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["map_object_id"] == 1
    assert response_json["in_base"] == False
    assert not response_json["resources"]


@pytest.mark.asyncio
async def test_get_players(client, db_session):
    for i in range(1, 3):
        player = Player(map_id=i, player_id=111, name="test_name")
        db_session.add(player)
    await db_session.commit()
    response = await client.get("/player/")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 2


@pytest.mark.asyncio
async def test_move_player(client, db_session):
    await create_player(db_session)
    response = await client.patch("/player/move-player/", json={"map_id": 1, "map_object_id": 2})
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["new_map_object_id"] == 2


@pytest.mark.asyncio
async def test_create_player_on_non_exist_map(client):
    response = await client.post("/player/", json={"map_id": 10})
    assert response.status_code == 500
    response_json = response.json()
    assert "asyncpg.exceptions.ForeignKeyViolationError" in response_json["detail"]


@pytest.mark.asyncio
async def test_move_player_on_non_exist_object(client, db_session):
    await create_player(db_session)
    response = await client.patch("/player/move-player/", json={"map_id": 1, "map_object_id": 22})
    assert response.status_code == 500
    response_json = response.json()
    assert "asyncpg.exceptions.ForeignKeyViolationError" in response_json["detail"]


@pytest.mark.asyncio
async def test_move_player_on_non_exist_map(client, db_session):
    player = Player(map_id=1, player_id=1, name="test_name")
    db_session.add(player)
    await db_session.commit()
    response = await client.patch("/player/move-player/", json={"map_id": 11, "map_object_id": 2})
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Player not found"
