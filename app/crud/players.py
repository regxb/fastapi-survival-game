from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.crud.base import CRUDBase
from app.models.maps import MapObject
from app.models.players import Player
from app.schemas.players import PlayerCreateSchema

CRUDPlayers = CRUDBase[Player, PlayerCreateSchema]
base_crud_player = CRUDPlayers(Player)

async def get_player_with_position(session: AsyncSession, player_id: int):
    stmt = (
        select(Player)
        .options(
            joinedload(Player.map_object).joinedload(MapObject.position)
        )
        .where(Player.id == player_id)
    )

    result = await session.execute(stmt)
    return result.scalar_one_or_none()
