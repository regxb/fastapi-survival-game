from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.schemas.map import BaseMapSchema, MapResponseSchema
from app.services.map import MapService

router = APIRouter(prefix="/maps", tags=["Maps"])


@router.get("/", response_model=list[BaseMapSchema])
async def get_maps(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        offset: int = Query(0, ge=0),
        limit: int = Query(100, ge=0, le=100)
):
    return await MapService(session).get_maps(offset, limit)


@router.get("/{map_id}/", response_model=MapResponseSchema)
async def get_map(
        map_id: int,
        session: Annotated[AsyncSession, Depends(get_async_session)]
) -> MapResponseSchema:
    return await MapService(session).get_map_with_objects(map_id)
