import pytest

from app.repository import player_item_storage_repository


@pytest.mark.asyncio
async def test_get_items_recipe(client, db_session, player_with_resources, items_recipe):
    response = await client.get("/items/recipes/", params={"map_id": 1})
    assert response.status_code == 200
    response_json = response.json()
    print(response_json)
    assert response_json[0]["name"] == "test_name"
    assert response_json[0]["can_craft"] == True
    assert len(response_json[0]["recipe"]["resources"]) == 1
    assert response_json[0]["recipe"]["resources"][0]["name"] == "wood"


@pytest.mark.asyncio
async def test_craft_item(client, db_session, items_recipe, player_with_resources, player_base, item):
    response = await client.patch("/items/craft/", json={
        "map_id": 1,
        "item_id": 1,
    })
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 1
    assert response_json[0]["name"] == "test_name"
    assert response_json[0]["tier"] == 1
    assert response_json[0]["active_item"] == False


@pytest.mark.asyncio
async def test_craft_item_not_enough_resources(client, db_session, items_recipe, player_base):
    response = await client.patch("/items/craft/", json={
        "map_id": 1,
        "item_id": 1,
    })
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"] == "Not enough resources"


@pytest.mark.asyncio
async def test_craft_item_outside_base(client, db_session, player_outside_base, player_with_resources, items_recipe):
    response = await client.patch("/items/craft/", json={
        "map_id": 1,
        "item_id": 1,
    })
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"] == "The player is not at the base"


@pytest.mark.asyncio
async def test_craft_item_not_exist_item(client, db_session, player_with_resources, player_base, items_recipe):
    response = await client.patch("/items/craft/", json={
        "map_id": 1,
        "item_id": 11,
    })
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Item not found"


@pytest.mark.asyncio
async def test_transfer_item_to_storage(client, db_session, player_with_items, player_base):
    response = await client.patch("/items/transfer/", json={
        "map_id": 1,
        "item_id": 1,
        "count": 1,
        "direction": "to_storage"
    })
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["inventory_items"] is None
    assert len(response_json["storage_items"]) == 1
    assert response_json["storage_items"][0]["name"] == "test_name"
    assert response_json["storage_items"][0]["tier"] == 1


@pytest.mark.asyncio
async def test_transfer_item_from_storage(client, db_session, player_base_storage_with_items):
    response = await client.patch("/items/transfer/", json={
        "map_id": 1,
        "item_id": 1,
        "count": 1,
        "direction": "from_storage"
    })
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json["inventory_items"]) == 1
    assert response_json["storage_items"] is None
    assert response_json["inventory_items"][0]["name"] == "test_name"
    assert response_json["inventory_items"][0]["tier"] == 1


@pytest.mark.asyncio
async def test_transfer_non_exist_item_to_storage(client, db_session, player_with_items, player_base):
    response = await client.patch("/items/transfer/", json={
        "map_id": 1,
        "item_id": 11,
        "count": 1,
        "direction": "from_storage"
    })
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Player has no item"
