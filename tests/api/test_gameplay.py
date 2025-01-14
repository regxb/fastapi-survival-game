import pytest

from app.models import Player
from app.schemas.gameplay import BuildingType
from tests.utils import create_players_with_resources, create_player


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


# @pytest.mark.asyncio
# async def test_start_farm(client, db_session, test_broker):
#     player = Player(map_id=1, player_id=1, name="test_name", map_object_id=2)
#     db_session.add(player)
#     await db_session.flush()
#     await db_session.commit()
#
#     response = await client.patch(
#         "/gameplay/farm-resources/",
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
