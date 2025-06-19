from typing import Annotated

from aiogram.utils.web_app import WebAppUser
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.depends.deps import get_user_data_from_request
from app.schemas import ItemResponseSchema, ItemSchemaResponse, CraftItemSchema, PlayerItemsSchema, \
    TransferItemSchema, EquipItemSchema, ItemLocation
from app.services.item import ItemService, ItemTransferService, ItemEquipService

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("/recipes/", response_model=list[ItemResponseSchema])
async def get_items_recipe(
        map_id: int,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await ItemService(session).get_items(map_id, user.id)


@router.patch("/craft/", response_model=list[ItemSchemaResponse] | None)
async def craft_item(
        craft_data: CraftItemSchema,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await ItemService(session).craft(user.id, craft_data)


@router.patch("/transfer/")
async def transfer_item(
        transfer_data: TransferItemSchema,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await ItemTransferService(session).transfer(user.id, transfer_data)


@router.patch("/equip/")
async def equip_item(
        equip_data: EquipItemSchema,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await ItemEquipService(session).equip(user.id, equip_data)


@router.delete("/{item_id}/")
async def delete_item(
        item_id: int,
        count: int,
        map_id: int,
        item_location: ItemLocation,
        user: Annotated[WebAppUser, Depends(get_user_data_from_request)],
        session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await ItemService(session).delete(user.id, map_id, item_id, count, item_location)


