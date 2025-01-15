import pytest

from app.models import Player
from app.schemas.gameplay import BuildingType
from tests.utils import create_players_with_resources, create_player, create_player_base, \
    create_low_cost_item_with_recipe, create_high_cost_item_with_recipe, create_player_outside_base, add_item_to_player, \
    add_item_to_player_storage


@pytest.mark.asyncio
async def test_get_building_cost(client, db_session):
    await create_player(db_session)

    response = await client.get(
        "/gameplay/cost-of-building-base/",
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
async def test_build_base(client, db_session):
    await create_players_with_resources(db_session)

    response = await client.post(
        "/gameplay/build-base/",
        json={
            "x1": 1,
            "y1": 1,
            "map_id": 1,
        }
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["name"] == "test_name base"


@pytest.mark.asyncio
async def test_start_farm(client, db_session, test_broker):
    player = Player(map_id=1, player_id=111, name="test_name", map_object_id=2)
    db_session.add(player)
    await db_session.flush()
    await db_session.commit()

    response = await client.patch(
        "/gameplay/farm-resources/",
        json={
            "map_id": 1,
            "mode": "easy",
        }
    )

    assert response.status_code == 200
    await db_session.refresh(player)
    assert player.status == "farming"


@pytest.mark.asyncio
async def test_transfer_resources(client, db_session):
    await create_players_with_resources(db_session)
    await create_player_base(db_session)
    response = await client.patch("/gameplay/transfer-resources/", json={
        "map_id": 1,
        "resource": "wood",
        "count": 8,
        "direction": "to_storage"
    })
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["player_resources"]["wood"] == 2
    assert response_json["storage_resources"]["wood"] == 8


@pytest.mark.asyncio
async def test_not_enough_resources_to_transfer(client, db_session):
    await create_players_with_resources(db_session)
    await create_player_base(db_session)
    response = await client.patch("/gameplay/transfer-resources/", json={
        "map_id": 1,
        "resource": "wood",
        "count": 11,
        "direction": "to_storage"
    })
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"] == "Not enough resources"


@pytest.mark.asyncio
async def test_get_items_recipe(client, db_session):
    await create_players_with_resources(db_session)
    await create_low_cost_item_with_recipe(db_session)
    response = await client.get("/gameplay/get-items-recipe/", params={"map_id": 1})
    assert response.status_code == 200
    response_json = response.json()
    assert response_json[0]["name"] == "test_name"
    assert response_json[0]["can_craft"] == True
    assert response_json[0]["recipe"]["resources"]["wood"] == 5


@pytest.mark.asyncio
async def test_craft_item(client, db_session):
    await create_players_with_resources(db_session)
    await create_low_cost_item_with_recipe(db_session)
    await create_player_base(db_session)
    response = await client.patch("/gameplay/craft-item/", json={
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
async def test_craft_item_not_enough_resources(client, db_session):
    await create_players_with_resources(db_session)
    await create_high_cost_item_with_recipe(db_session)
    await create_player_base(db_session)
    response = await client.patch("/gameplay/craft-item/", json={
        "map_id": 1,
        "item_id": 1,
    })
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"] == "Not enough resources"


@pytest.mark.asyncio
async def test_craft_item_outside_base(client, db_session):
    await create_players_with_resources(db_session)
    await create_player_outside_base(db_session)
    response = await client.patch("/gameplay/craft-item/", json={
        "map_id": 1,
        "item_id": 1,
    })
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"] == "The player is not at the base"


@pytest.mark.asyncio
async def test_craft_item_not_exist_item(client, db_session):
    await create_players_with_resources(db_session)
    await create_player_base(db_session)
    response = await client.patch("/gameplay/craft-item/", json={
        "map_id": 1,
        "item_id": 11,
    })
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Item not found"


@pytest.mark.asyncio
async def test_transfer_resources_without_base(client, db_session):
    await create_players_with_resources(db_session)
    response = await client.patch("/gameplay/transfer-resources/", json={
        "map_id": 1,
        "resource": "wood",
        "count": 10,
        "direction": "to_storage"
    })
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Player has no base"


@pytest.mark.asyncio
async def test_transfer_item_to_storage(client, db_session):
    await create_player(db_session)
    await create_player_base(db_session)
    await create_low_cost_item_with_recipe(db_session)
    await add_item_to_player(db_session)

    response = await client.post("/gameplay/transfer-items/", json={
        "map_id": 1,
        "item_id": 1,
        "direction": "to_storage"
    })
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json["inventory_items"]) == 0
    assert len(response_json["storage_items"]) == 1
    assert response_json["storage_items"][0]["name"] == "test_name"
    assert response_json["storage_items"][0]["tier"] == 1


@pytest.mark.asyncio
async def test_transfer_item_from_storage(client, db_session):
    await create_player(db_session)
    await create_player_base(db_session)
    await create_low_cost_item_with_recipe(db_session)
    await add_item_to_player_storage(db_session)

    response = await client.post("/gameplay/transfer-items/", json={
        "map_id": 1,
        "item_id": 1,
        "direction": "from_storage"
    })
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json["inventory_items"]) == 1
    assert len(response_json["storage_items"]) == 0
    assert response_json["inventory_items"][0]["name"] == "test_name"
    assert response_json["inventory_items"][0]["tier"] == 1


@pytest.mark.asyncio
async def test_transfer_non_exist_item_to_storage(client, db_session):
    await create_player(db_session)
    await create_player_base(db_session)
    await create_low_cost_item_with_recipe(db_session)
    response = await client.post("/gameplay/transfer-items/", json={
        "map_id": 1,
        "item_id": 11,
        "direction": "from_storage"
    })
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Item not found"


@pytest.mark.asyncio
async def test_get_non_exist_building_cost(client, db_session):
    await create_player(db_session)

    response = await client.get(
        "/gameplay/cost-of-building-base/",
        params={
            "building_type": "test mode"
        }
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_build_base_in_busy_area(client, db_session):
    await create_players_with_resources(db_session)

    response = await client.post(
        "/gameplay/build-base/",
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
async def test_build_base_without_resources(client, db_session):
    await create_player(db_session)
    response = await client.post(
        "/gameplay/build-base/",
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
async def test_build_base_on_non_exist_map(client, db_session):
    await create_players_with_resources(db_session)
    response = await client.post(
        "/gameplay/build-base/",
        json={
            "x1": 11,
            "y1": 11,
            "map_id": 10,
        }
    )
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Player not found"
