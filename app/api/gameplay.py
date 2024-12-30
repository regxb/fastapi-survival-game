from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_async_session
from app.schemas.gameplay import PlayerMoveSchema
from app.services.players import PlayerService

router = APIRouter(prefix="/gameplay", tags=["gameplay"])


@router.patch("/move-player")
async def move_player(player_data: PlayerMoveSchema, session:AsyncSession = Depends(get_async_session)):
    return await PlayerService(session).move_player(player_data)
