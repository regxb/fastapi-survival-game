import pytest


@pytest.mark.asyncio
async def test_create_player(client, db_session, map_with_objects):
    response = await client.post("/players/", json={"map_id": 1})
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["map_object_id"] == 1
    assert response_json["in_base"] == False
    assert not response_json["resources"]


@pytest.mark.asyncio
async def test_get_player(client, db_session, player):
    response = await client.get("/players/1/")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["map_object_id"] == 1
    assert response_json["in_base"] == False
    assert not response_json["resources"]


@pytest.mark.asyncio
async def test_get_players(client, db_session, player):
    response = await client.get("/players/")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 1


@pytest.mark.asyncio
async def test_move_player(client, db_session, map_with_objects, player):
    response = await client.patch("/players/move/", json={"map_id": 1, "map_object_id": 2})
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["new_map_object_id"] == 2


@pytest.mark.asyncio
async def test_create_player_on_non_exist_map(client, map_with_objects, player):
    response = await client.post("/players/", json={"map_id": 10})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_move_player_on_non_exist_object(client, db_session, map_with_objects, player):
    response = await client.patch("/players/move/", json={"map_id": 1, "map_object_id": 22})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_move_player_on_non_exist_map(client, db_session, map_with_objects, player):
    response = await client.patch("/players/move/", json={"map_id": 11, "map_object_id": 2})
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Player not found"
