from aiogram.utils.web_app import WebAppUser
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.depends.deps import get_user_data_from_request
from app.schemas.gameplay import PlayerMoveResponseSchema, PlayerMoveSchema
from app.schemas.players import BasePlayerSchema, PlayerCreateSchema, PlayerSchema
from app.services.player_service import PlayerService

router = APIRouter(prefix="/player", tags=["player"])


@router.post("/", response_model=PlayerSchema)
async def create_player(
        player_data: PlayerCreateSchema,
        user: WebAppUser = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session)
):
    return await PlayerService(session).create_player(user, player_data)


@router.get("/", response_model=list[BasePlayerSchema])
async def get_players(
        user: WebAppUser = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session)
):
    return await PlayerService(session).get_players(user.id)


@router.patch("/move-player/", response_model=PlayerMoveResponseSchema)
async def move_player(
        player_data: PlayerMoveSchema,
        user: WebAppUser = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session)
):
    return await PlayerService(session).move_player(user.id, player_data)


@router.get("/{map_id}/", response_model=PlayerSchema)
async def get_player(
        map_id: int,
        user: WebAppUser = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session)
):
    return await PlayerService(session).get_player(map_id, user.id)
