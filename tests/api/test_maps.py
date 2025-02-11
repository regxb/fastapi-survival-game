import pytest


@pytest.mark.asyncio
async def test_get_maps(client, db_session, map_with_objects):
    response = await client.get("/maps/")
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 1
    assert response_json[0]["height"] == 111
    assert response_json[0]["width"] == 222


@pytest.mark.asyncio
async def test_get_map(client, db_session, map_with_objects):
    response = await client.get(
        "/maps/1/"
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["id"] == 1
    assert len(response_json["map_objects"]) == 2
