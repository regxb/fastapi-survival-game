import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_async_session
from app.crud import map_objects
from app.schemas.map_objects import MapResponseSchema, MapObjectResponseSchema, MapObjectCreateSchema
from app.services.map_objects import MapObjectResponseService, MapObjectService

router = APIRouter(prefix="/map", tags=["Map"])


@router.get("/")
async def get_map(map_id: int, session:AsyncSession = Depends(get_async_session)):
    return await MapObjectResponseService(map_id, session).make_map_data_response()


@router.post("/add-object")
async def add_object_on_map(object_data: MapObjectCreateSchema, session:AsyncSession = Depends(get_async_session)):
    return await MapObjectService(object_data.map_id, session).add_object_on_map(object_data)
