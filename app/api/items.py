from typing import Annotated

from aiogram.utils.web_app import WebAppUser
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.depends.deps import get_user_data_from_request
from app.schemas.item import ItemSchemaResponse, CraftItemSchema, ItemResponseSchema
from app.services.item import ItemService

router = APIRouter(prefix="/items",tags=["Items"])


@router.get("/recipes/", response_model=list[ItemResponseSchema])
async def get_items_recipe(
        map_id: int,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await ItemService(session).get_items(map_id, user.id)


@router.patch("/craft/", response_model=list[ItemSchemaResponse])
async def craft_item(
        craft_data: CraftItemSchema,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await ItemService(session).craft(user.id, craft_data)
