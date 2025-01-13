from aiogram.utils.web_app import WebAppUser
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import FarmSession
from app.models.player_model import Player, PlayerResources, PlayerBase
from app.repository import repository_farm_session
from app.repository.player_repository import repository_player
from app.schemas.gameplay import PlayerMoveResponseSchema, PlayerMoveSchema, FarmSessionSchema
from app.schemas.players import (BasePlayerSchema, PlayerCreateSchema,
                                 PlayerDBCreateSchema, PlayerSchema, PlayerBaseSchema)
from app.services import FarmingService
from app.services.validation_service import ValidationService


class PlayerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_player(self, user: WebAppUser, player_data: PlayerCreateSchema):
        obj_data = PlayerDBCreateSchema(player_id=user.id, name=user.username, map_id=player_data.map_id)
        player = await repository_player.create(self.session, obj_data)
        return PlayerSchema(resources={}, farm_sessions=None, base=None, in_base=False, **player.__dict__)

    async def get_players(self, telegram_id: int):
        players = await repository_player.get_multi(
            self.session,
            options=[joinedload(Player.base)],
            player_id=telegram_id
        )
        return [BasePlayerSchema.model_validate(player) for player in players]

    async def get_player(self, map_id: int, telegram_id: int):
        player = await repository_player.get(
            self.session,
            options=[
                joinedload(Player.resources).joinedload(PlayerResources.resource),
                joinedload(Player.base).joinedload(PlayerBase.resources)
            ],
            map_id=map_id,
            player_id=telegram_id
        )
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        farm_session = await repository_farm_session.get(
            self.session,
            player_id=telegram_id,
            map_id=map_id,
            status="in_progress"
        )

        return PlayerResponseService.get_player_response(player, farm_session, self.session)

    async def move_player(self, telegram_id: int, player_data: PlayerMoveSchema):
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

    @staticmethod
    def update_player_resources(
            player_resources: list[PlayerResources], resource_id: int, cost: int, action: str
    ) -> None:
        for resource in player_resources:
            if resource.resource_id == resource_id:
                if action == "decrease":
                    resource.count -= cost
                if action == "increase":
                    resource.count += cost


class PlayerResponseService:

    @staticmethod
    def get_player_response(player: Player, farm_session: FarmSession, session: AsyncSession):
        if farm_session:
            time_left = FarmingService(session).get_time_left(farm_session.end_time)
            farm_session_schema = FarmSessionSchema(time_left=time_left, **farm_session.__dict__)

        else:
            farm_session_schema = None
        in_base = player.map_object_id == player.base.map_object_id if player.base else False
        resources = {resource.resource.name: resource.count for resource in player.resources}
        if player.base:
            base_storage_resources = {resource.resource.name: resource.count for resource in player.base.resources}
            base = PlayerBaseSchema(map_object_id=player.base.map_object_id, resources=base_storage_resources)
        else:
            base = None
        player_data = {key: value for key, value in player.__dict__.items() if key != "base" and key != "resources"}
        player_schema = PlayerSchema(
            in_base=in_base,
            base=base,
            farm_sessions=farm_session_schema,
            resources=resources,
            **player_data
        )

        return player_schema

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