import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.depends.auth import get_user_data_from_request
from app.schemas.maps import MapResponseSchema, MapObjectResponseSchema, MapObjectCreateSchema
from app.services.maps import MapService

router = APIRouter(prefix="/map", tags=["Map"])


@router.get("/")
async def get_maps(
        offset: int = Query(ge=0, default=0),
        limit: int = Query(ge=0, le=100, default=100),
        session: AsyncSession = Depends(get_async_session)):
    return await MapService(session).get_maps(offset, limit)


@router.post("/add-player-base")
async def add_player_base_on_map(
        object_data: MapObjectCreateSchema,
        user: dict = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session)
):
    return await MapService(session).add_player_base_on_map(user["id"], object_data)


@router.get("/{map_id}")
async def get_map(map_id: int, session: AsyncSession = Depends(get_async_session)):
    return await MapService(session).get_map_with_objects(map_id)
