from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Player, PlayerResources


async def create_player(session: AsyncSession):
    player = Player(map_id=1, player_id=111, name="test_name")
    session.add(player)
    await session.commit()


async def create_players_with_resources(session: AsyncSession):
    player = Player(map_id=1, player_id=111, name="test_name")
    session.add(player)
    await session.flush()
    player_resources = PlayerResources(player_id=player.id, resource_id=1, resource_quantity=10)
    session.add(player_resources)
    player_resources = PlayerResources(player_id=player.id, resource_id=2, resource_quantity=20)
    session.add(player_resources)
    await session.commit()
