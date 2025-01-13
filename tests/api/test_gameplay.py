import pytest

from app.models import Player, PlayerResources
from app.schemas.gameplay import BuildingType


@pytest.mark.asyncio
async def test_get_cost_building_cost(client, db_session):
    player = Player(map_id=1, player_id=1, name="test_name")
    db_session.add(player)
    await db_session.commit()

    response = await client.get(
        "/gameplay/cost-of-building-base/",
        params={
            "building_type": BuildingType.BASE.value
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
    player = Player(map_id=1, player_id=1, name="test_name")
    db_session.add(player)
    await db_session.flush()
    player_resources = PlayerResources(player_id=player.id, resource_id=1, count=10)
    db_session.add(player_resources)
    player_resources = PlayerResources(player_id=player.id, resource_id=2, count=20)
    db_session.add(player_resources)
    await db_session.commit()

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
async def test_build_base(client, db_session):
    player = Player(map_id=1, player_id=1, name="test_name", map_object_id=2)
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
    response_json = response.json()
    # assert response_json["name"] == "test_name base"
