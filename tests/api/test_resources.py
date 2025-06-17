import pytest

from app.models import Player


# @pytest.mark.asyncio
# async def test_start_farm(client, db_session, test_broker, map_with_objects, farming_mode):
#     player = Player(map_id=1, player_id=111, name="test_name", map_object_id=2)
#     db_session.add(player)
#     await db_session.flush()
#     await db_session.commit()
#
#     response = await client.patch(
#         "/resources/farm/",
#         json={
#             "map_id": 1,
#             "mode": "easy",
#         }
#     )
#
#     assert response.status_code == 200
#     await db_session.refresh(player)
#     assert player.status == "farming"


@pytest.mark.asyncio
async def test_transfer_resources_to_storage(client, db_session, player_resources, player_base):
    response = await client.patch("/resources/transfer/", json={
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
    response = await client.patch("/resources/transfer/", json={
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
    response = await client.patch("/resources/transfer/", json={
        "map_id": 1,
        "resource_id": 1,
        "count": 10,
        "direction": "to_storage"
    })
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "Player has no base"
