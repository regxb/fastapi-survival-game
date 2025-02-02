import pytest

from app.models import Player


@pytest.mark.asyncio
async def test_start_farm(client, db_session, test_broker, map_with_objects, farming_mode):
    player = Player(map_id=1, player_id=111, name="test_name", map_object_id=2)
    db_session.add(player)
    await db_session.flush()
    await db_session.commit()

    response = await client.patch(
        "/resources/farm/",
        json={
            "map_id": 1,
            "mode": "easy",
        }
    )

    assert response.status_code == 200
    await db_session.refresh(player)
    assert player.status == "farming"
