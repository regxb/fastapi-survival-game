import pytest

from app.schemas import BuildingType


@pytest.mark.asyncio
async def test_get_building_cost(client, db_session, player, building_cost):
    response = await client.get(
        "/bases/cost/",
        params={
            "building_type": BuildingType.BASE.value,
            "map_id": 1
        }
    )

    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json["resources"]) == 2
    assert response_json["resources"][0]["resource_quantity"] == 10
    assert response_json["resources"][1]["resource_quantity"] == 20
    assert response_json["can_build"] == False


@pytest.mark.asyncio
async def test_build_base(client, db_session, player_resources):
    response = await client.post(
        "/bases/",
        json={
            "x1": 1,
            "y1": 1,
            "map_id": 1,
        }
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["map_object_id"] == 3


@pytest.mark.asyncio
async def test_get_non_exist_building_cost(client, db_session, player, building_cost):
    response = await client.get(
        "/bases/cost/",
        params={
            "building_type": "test mode"
        }
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_build_base_in_busy_area(client, db_session, map_with_objects, player_with_resources):
    response = await client.post(
        "/bases/",
        json={
            "x1": 11,
            "y1": 11,
            "map_id": 1,
        }
    )

    assert response.status_code == 409
    response_json = response.json()
    assert response_json["detail"] == "The place is already taken"


@pytest.mark.asyncio
async def test_build_base_without_resources(client, db_session, map_with_objects, player, building_cost):
    response = await client.post(
        "/bases/",
        json={
            "x1": 11,
            "y1": 11,
            "map_id": 1,
        }
    )
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"] == "Not enough resources"


@pytest.mark.asyncio
async def test_build_base_on_non_exist_map(client, db_session, map_with_objects, player_with_resources):
    response = await client.post(
        "/bases/",
        json={
            "x1": 11,
            "y1": 11,
            "map_id": 10,
        }
    )
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Player not found"
