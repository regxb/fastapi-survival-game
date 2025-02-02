import pytest
from sqlalchemy import select

from app.models import PlayerBase, PlayerItemStorage
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
    assert response_json["resources"]["wood"] == 10
    assert response_json["resources"]["stone"] == 20
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
async def test_transfer_resources_to_storage(client, db_session, player_resources, player_base):
    response = await client.patch("/bases/transfer/resources/", json={
        "map_id": 1,
        "resource_id": 1,
        "count": 8,
        "direction": "to_storage"
    })
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json["player_resources"]) == 2
    assert response_json["player_resources"][0]["name"] == "wood"


@pytest.mark.asyncio
async def test_not_enough_resources_to_transfer(client, db_session, player_resources, player_base):
    response = await client.patch("/bases/transfer/resources/", json={
        "map_id": 1,
        "resource_id": 1,
        "count": 11,
        "direction": "to_storage"
    })
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"] == "Not enough resources"


@pytest.mark.asyncio
async def test_transfer_resources_without_base(client, db_session, player_resources):
    response = await client.patch("/bases/transfer/resources/", json={
        "map_id": 1,
        "resource_id": 1,
        "count": 10,
        "direction": "to_storage"
    })
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Player has no base"


@pytest.mark.asyncio
async def test_transfer_item_to_storage(client, db_session, player_with_items, player_base):
    response = await client.patch("/bases/transfer/items/", json={
        "map_id": 1,
        "item_id": 1,
        "direction": "to_storage"
    })
    assert response.status_code == 200
    response_json = response.json()
    # assert response_json["inventory_items"] is None
    assert len(response_json["storage_items"]) == 1
    assert response_json["storage_items"][0]["name"] == "test_name"
    assert response_json["storage_items"][0]["tier"] == 1


@pytest.mark.asyncio
async def test_transfer_item_from_storage(client, db_session, player_base_storage_with_items):
    response = await client.patch("/bases/transfer/items/", json={
        "map_id": 1,
        "item_id": 1,
        "direction": "from_storage"
    })
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json["inventory_items"]) == 1
    # assert response_json["storage_items"] is None
    assert response_json["inventory_items"][0]["name"] == "test_name"
    assert response_json["inventory_items"][0]["tier"] == 1


@pytest.mark.asyncio
async def test_transfer_non_exist_item_to_storage(client, db_session, player_with_items, player_base):
    response = await client.patch("/bases/transfer/items/", json={
        "map_id": 1,
        "item_id": 11,
        "direction": "from_storage"
    })
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Item not found"


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
