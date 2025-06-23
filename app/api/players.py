from typing import Annotated

from aiogram.utils.web_app import WebAppUser
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.depends.deps import get_user_data_from_request
from app.schemas.player import (BasePlayerSchema, PlayerCreateSchema,
                                PlayerMoveResponseSchema, PlayerMoveSchema,
                                PlayerSchema)
from app.services.player import PlayerService

router = APIRouter(prefix="/players", tags=["Players"])


@router.post("/")
async def create_player(
        player_data: PlayerCreateSchema,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await PlayerService(session).create_player(user, player_data)


@router.get("/", response_model=list[BasePlayerSchema])
async def get_players(
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
) -> list[BasePlayerSchema]:
    return await PlayerService(session).get_players(user.id)


@router.get("/{map_id}/", response_model=PlayerSchema)
async def get_player(
        map_id: int,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
) -> PlayerSchema:
    return await PlayerService(session).get(map_id, user.id)


@router.patch("/move/", response_model=PlayerMoveResponseSchema)
async def move_player(
        player_data: PlayerMoveSchema,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
) -> PlayerMoveResponseSchema:
    return await PlayerService(session).move(user.id, player_data)
