from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Player, PlayerResources


async def create_player(session: AsyncSession):
    player = Player(map_id=1, player_id=1, name="test_name")
    session.add(player)
    await session.commit()


async def create_players_with_resources(session: AsyncSession):
    player = Player(map_id=1, player_id=1, name="test_name")
    session.add(player)
    await session.flush()
    player_resources = PlayerResources(player_id=player.id, resource_id=1, count=10)
    session.add(player_resources)
    player_resources = PlayerResources(player_id=player.id, resource_id=2, count=20)
    session.add(player_resources)
    await session.commit()
