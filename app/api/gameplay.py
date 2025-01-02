from aiogram.utils.web_app import WebAppInitData
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from watchfiles import awatch

from app.core.database import get_async_session
from app.depends.auth import get_user_data_from_request
from app.schemas.gameplay import PlayerMoveSchema
from app.schemas.players import PlayerResponseSchema
from app.services.gameplay import GameplayService
from app.services.players import PlayerService

router = APIRouter(prefix="/gameplay", tags=["gameplay"])


@router.patch("/move-player", response_model=PlayerResponseSchema)
async def move_player(
        player_data: PlayerMoveSchema,
        user: WebAppInitData = Depends(get_user_data_from_request),
        session:AsyncSession = Depends(get_async_session)
):
    return await PlayerService(session).move_player(user.user.id, player_data)


@router.patch("/farm-resources")
async def farm_resources(
        map_id: int,
        session:AsyncSession = Depends(get_async_session),
        user: WebAppInitData = Depends(get_user_data_from_request),
):
    return await GameplayService(session).farm_resource(map_id, user.user.id)
