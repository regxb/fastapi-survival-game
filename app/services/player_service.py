import datetime

from aiogram.utils.web_app import WebAppUser
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import FarmSession, Inventory
from app.models.player_model import Player, PlayerResources, PlayerBase
from app.repository import repository_farm_session
from app.repository.player_repository import repository_player
from app.schemas.gameplay import PlayerMoveResponseSchema, PlayerMoveSchema, FarmSessionSchema
from app.schemas.players import (BasePlayerSchema, PlayerCreateSchema,
                                 PlayerDBCreateSchema, PlayerSchema, PlayerBaseSchema)
from app.services.validation_service import ValidationService


class PlayerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_player(self, user: WebAppUser, player_data: PlayerCreateSchema) -> PlayerSchema:
        obj_data = PlayerDBCreateSchema(player_id=user.id, name=user.username, map_id=player_data.map_id)
        player = await repository_player.create(self.session, obj_data)
        return PlayerSchema(in_base=False, **player.__dict__)

    async def get_players(self, telegram_id: int) -> list[BasePlayerSchema]:
        players = await repository_player.get_multi(
            self.session,
            options=[joinedload(Player.base)],
            player_id=telegram_id
        )
        return [BasePlayerSchema.model_validate(player) for player in players]

    async def get_player(self, map_id: int, telegram_id: int) -> PlayerSchema:
        player = await repository_player.get(
            self.session,
            options=[
                joinedload(Player.resources).joinedload(PlayerResources.resource),
                joinedload(Player.base).joinedload(PlayerBase.storage),
                joinedload(Player.inventory).joinedload(Inventory.item)
            ],
            map_id=map_id,
            player_id=telegram_id
        )
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        farm_session = await repository_farm_session.get(
            self.session,
            player_id=player.id,
            map_id=map_id,
            status="in_progress"
        )

        return PlayerResponseService.get_player_response(player, farm_session)

    async def move_player(self, telegram_id: int, player_data: PlayerMoveSchema) -> PlayerMoveResponseSchema:
        player = await repository_player.get(self.session, map_id=player_data.map_id, player_id=telegram_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        ValidationService.can_player_do_something(player)
        if player.map_object_id == player_data.map_object_id:
            raise HTTPException(status_code=409, detail="The user is already at this place")

        new_player_position = await repository_player.update(
            self.session, player_data, player_id=telegram_id, map_id=player_data.map_id
        )
        return PlayerMoveResponseSchema(new_map_object_id=new_player_position.map_object_id, player_id=player.id)

    async def update_energy(self):
        where_clause = {"energy": ("<", 100)}

        update_data = {"energy": Player.energy + 1}

        updated_count = await repository_player.update_multiple(
            session=self.session,
            model=Player,
            obj_in=update_data,
            where_clause=where_clause,
        )
        print(f"Updated {updated_count} rows")

    @staticmethod
    def update_player_resources(
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
    def get_player_response(player: Player, farm_session: FarmSession) -> PlayerSchema:
        if farm_session:
            total_seconds = int((farm_session.end_time - farm_session.start_time).total_seconds())
            seconds_pass = int((datetime.datetime.now() - farm_session.start_time).total_seconds())
            farm_session_schema = FarmSessionSchema(total_seconds=total_seconds, seconds_pass=seconds_pass)

        else:
            farm_session_schema = None

        in_base = player.map_object_id == player.base.map_object_id if player.base else False
        resources = {
            resource.resource.name: resource.resource_quantity for resource in player.resources if
            resource.resource_quantity > 0
        }
        resources = None if not resources else resources

        if player.base:
            storage_resources = {resource.resource.name: resource.resource_quantity for resource in player.base.storage
                                 if resource.resource_quantity > 0}
            storage_resources = None if not storage_resources else storage_resources
            base = PlayerBaseSchema(map_object_id=player.base.map_object_id, resources=storage_resources)
        else:
            base = None

        player_data = {key: value for key, value in player.__dict__.items() if key != "base" and key != "resources"}
        inventory = [{
            "id": item.item.id,
            "name": item.item.name,
            "tier": item.item.tier,
            "active_item": False
        } for item in player.inventory]

        player_schema = PlayerSchema(
            in_base=in_base,
            base=base,
            farm_sessions=farm_session_schema,
            resources=resources,
            items=inventory,
            **player_data
        )

        return player_schema
