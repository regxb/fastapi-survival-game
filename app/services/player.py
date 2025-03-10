import datetime
from typing import List, Optional

from aiogram.utils.web_app import WebAppUser
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import (Inventory, Player, PlayerBase, PlayerItemStorage,
                        PlayerResources, Item)
from app.repository import farm_session_repository, player_repository
from app.schemas import (BasePlayerSchema, FarmSessionSchema, ItemSchema,
                         ItemSchemaResponse, PlayerBaseSchema,
                         PlayerCreateSchema, PlayerDBCreateSchema,
                         PlayerMoveResponseSchema, PlayerMoveSchema,
                         PlayerSchema, ResourceCountSchema)
from app.services.validation import ValidationService


class PlayerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: WebAppUser, player_data: PlayerCreateSchema) -> PlayerSchema:
        obj_data = PlayerDBCreateSchema(player_id=user.id, name=user.username, map_id=player_data.map_id)
        player = await player_repository.create(self.session, obj_data)
        return PlayerSchema(in_base=False, **player.__dict__)

    async def get_players(self, telegram_id: int) -> list[BasePlayerSchema]:
        players = await player_repository.get_multi(
            self.session,
            options=[joinedload(Player.base)],
            player_id=telegram_id
        )
        return [BasePlayerSchema.model_validate(player) for player in players]

    async def get(self, map_id: int, telegram_id: int) -> PlayerSchema:
        player = await player_repository.get(
            self.session,
            options=[
                joinedload(Player.resources).joinedload(PlayerResources.resource),
                joinedload(Player.base).joinedload(PlayerBase.resources),
                joinedload(Player.base).joinedload(PlayerBase.items).joinedload(PlayerItemStorage.item).joinedload(Item.type),
                joinedload(Player.inventory).joinedload(Inventory.item).joinedload(Item.type)
            ],
            map_id=map_id,
            player_id=telegram_id
        )
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        farm_session = await farm_session_repository.get(
            self.session,
            player_id=player.id,
            map_id=map_id,
            status="in_progress"
        )
        return PlayerResponseService.get_player_response(player, farm_session)

    async def move(self, telegram_id: int, player_data: PlayerMoveSchema) -> PlayerMoveResponseSchema:
        player = await player_repository.get(self.session, map_id=player_data.map_id, player_id=telegram_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        ValidationService.can_player_do_something(player)
        if player.map_object_id == player_data.map_object_id:
            raise HTTPException(status_code=409, detail="The user is already at this place")

        new_player_position = await player_repository.update(
            self.session, player_data, player_id=telegram_id, map_id=player_data.map_id
        )
        return PlayerMoveResponseSchema(new_map_object_id=new_player_position.map_object_id, player_id=player.id)

    async def update_energy(self):
        where_clause = {"energy": ("<", 100)}

        update_data = {"energy": Player.energy + 1}

        updated_count = await player_repository.update_multiple(
            session=self.session,
            model=Player,
            obj_in=update_data,
            where_clause=where_clause,
        )
        print(f"Updated {updated_count} rows")

    async def update_health(self):
        where_clause = {"health": ("<", 100)}

        update_data = {"health": Player.health + 1}

        updated_count = await player_repository.update_multiple(
            session=self.session,
            model=Player,
            obj_in=update_data,
            where_clause=where_clause,
        )
        print(f"Updated {updated_count} rows")

    @staticmethod
    def update_resources(
            player_resources: list[PlayerResources], resource_id: int, quantity: int, action: str
    ) -> None:
        for resource in player_resources:
            if resource.resource_id == resource_id:
                if action == "decrease":
                    resource.resource_quantity -= quantity
                if action == "increase":
                    resource.resource_quantity += quantity


class PlayerResponseService:
    @staticmethod
    def serialize_farm_session(farm_session) -> Optional[FarmSessionSchema]:
        if not farm_session:
            return None
        total_seconds = int((farm_session.end_time - farm_session.start_time).total_seconds())
        seconds_pass = int((datetime.datetime.now() - farm_session.start_time).total_seconds())
        return FarmSessionSchema(total_seconds=total_seconds, seconds_pass=seconds_pass)

    @staticmethod
    def serialize_resources(resources) -> Optional[List[ResourceCountSchema]]:
        filtered_resources = [
            ResourceCountSchema(id=resource.resource.id,
                                name=resource.resource.name,
                                icon=resource.resource.icon,
                                count=resource.resource_quantity)
            for resource in resources
            if resource.resource_quantity > 0
        ]
        return filtered_resources or None

    @staticmethod
    def serialize_base(base: PlayerBase) -> Optional[PlayerBaseSchema]:
        if not base:
            return None

        resources = PlayerResponseService.serialize_resources(base.resources)
        items = PlayerResponseService.serialize_storage_items(base.items)
        return PlayerBaseSchema(map_object_id=base.map_object_id, items=items, resources=resources)

    @staticmethod
    def serialize_storage_items(items: list[PlayerItemStorage]):
        items =[
            ItemSchema(
                id=item.id,
                name=item.item.name,
                tier=item.tier,
                icon=item.item.icon,
                type=item.item.type.name,
            ) for item in items]
        return items or None

    @staticmethod
    def serialize_inventory(inventory) -> Optional[List[ItemSchemaResponse]]:
        items = [
            ItemSchemaResponse(
                id=item.id,
                name=item.item.name,
                tier=item.tier,
                icon=item.item.icon,
                active_item=item.active,
                type=item.item.type.name
            )
            for item in inventory]
        return items or None

    @staticmethod
    def get_player_response(player, farm_session) -> PlayerSchema:
        farm_session_schema = PlayerResponseService.serialize_farm_session(farm_session)
        in_base = player.map_object_id == player.base.map_object_id if player.base else False
        resources = PlayerResponseService.serialize_resources(player.resources)
        base = PlayerResponseService.serialize_base(player.base)
        inventory = PlayerResponseService.serialize_inventory(player.inventory)
        player_data = {key: value for key, value in player.__dict__.items()
                       if key not in ["base", "resources", "inventory"]}

        return PlayerSchema(
            in_base=in_base,
            base=base,
            farm_sessions=farm_session_schema,
            resources=resources,
            items=inventory,
            **player_data
        )
