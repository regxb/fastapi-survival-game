from aiogram.utils.web_app import WebAppUser
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.depends.deps import get_user_data_from_request
from app.repository import repository_farm_session
from app.schemas.gameplay import BuildingType, FarmResourcesSchema, CraftItemSchema, BuildingCostSchema, \
    FarmSessionSchema, ItemResponseSchema, ItemSchemaResponse
from app.schemas.players import PlayerBaseCreateSchema, PlayerTransferResourceSchema, PlayerResourcesSchema, \
    PlayerInventoryResponseSchema, PlayerTransferItemSchema, PlayerItemsSchema
from app.services.gameplay_service import FarmingService, ItemService
from app.services.player_base_service import PlayerBaseService

router = APIRouter(prefix="/gameplay", tags=["gameplay"])


@router.get("/test/")
async def test(session: AsyncSession = Depends(get_async_session)):
    player = await repository_farm_session.get(session, id=13)


@router.get("/cost-of-building-base/", response_model=BuildingCostSchema)
async def get_cost_building_base(
        map_id: int,
        building_type: BuildingType,
        user: WebAppUser = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session)
):
    return await PlayerBaseService(session).get_cost_building_base(building_type.value, user.id, map_id)


@router.post("/build-base/")
async def build_base(
        object_data: PlayerBaseCreateSchema,
        user: WebAppUser = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session)
):
    return await PlayerBaseService(session).create_player_base(user.id, object_data)


@router.patch("/farm-resources/", response_model=FarmSessionSchema)
async def farm_resources(
        farm_data: FarmResourcesSchema,
        user: WebAppUser = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session),

):
    return await FarmingService(session).start_farming(farm_data, user.id)


@router.patch("/transfer-resources/", response_model=PlayerResourcesSchema)
async def transfer_resources(
        transfer_data: PlayerTransferResourceSchema,
        user: WebAppUser = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session),
):
    return await PlayerBaseService(session).transfer_resources(user.id, transfer_data)


@router.post("/transfer-items/", response_model=PlayerItemsSchema)
async def transfer_item(
        transfer_data: PlayerTransferItemSchema,
        user: WebAppUser = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session),
):
    return await PlayerBaseService(session).transfer_items(user.id, transfer_data)


@router.get("/get-items-recipe/", response_model=list[ItemResponseSchema])
async def get_items_recipe(
        map_id: int,
        user: WebAppUser = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session)
):
    return await ItemService(session).get_items(map_id, user.id)


@router.patch("/craft-item/", response_model=list[ItemSchemaResponse])
async def craft_item(
        craft_data: CraftItemSchema,
        user: WebAppUser = Depends(get_user_data_from_request),
        session: AsyncSession = Depends(get_async_session)
):
    return await ItemService(session).craft_item(user.id, craft_data)
