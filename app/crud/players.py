from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.players import Player
from app.schemas.gameplay import PlayerMoveSchema
from app.schemas.players import PlayerCreateSchema

CRUDPlayers = CRUDBase[Player, PlayerCreateSchema]
base_crud_player = CRUDPlayers(Player)

async def move_player(session: AsyncSession, player_data: PlayerMoveSchema):
    user = await base_crud_player.get_by_id(session, player_data.id)
