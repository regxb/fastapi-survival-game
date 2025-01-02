from aiogram.utils.web_app import WebAppInitData
from fastapi import APIRouter, Request, Depends
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.depends.auth import get_user_data_from_request
from app.schemas.maps import MapObjectCreateSchema
from app.schemas.players import PlayerCreateSchema, PlayerResponseSchema
from app.services.maps import MapService
from app.services.players import PlayerService

router = APIRouter(prefix="/player", tags=["player"])

@router.post("/")
async def create_player(
        player_data: PlayerCreateSchema,
        user: WebAppInitData = Depends(get_user_data_from_request),
        session:AsyncSession = Depends(get_async_session)
):
    return await PlayerService(session).create_player(user.user.id, player_data)


@router.get("/")
async def get_players(session:AsyncSession = Depends(get_async_session)):
    return await PlayerService(session).get_players()


@router.get("/{player_id}")
async def get_player(player_id:int, session:AsyncSession = Depends(get_async_session)):
    return await PlayerService(session).get_player(player_id)


@router.post("/create-base")
async def create_base(
        object_data: MapObjectCreateSchema,
        user: WebAppInitData = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session)
):
    return await MapService(session).add_player_base_on_map(user.user.id, object_data)
