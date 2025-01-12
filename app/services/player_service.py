from aiogram.utils.web_app import WebAppUser
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.gameplay_model import BuildingCost
from app.models.player_model import Player, PlayerResources
from app.repository.player_repository import repository_player
from app.schemas.gameplay import PlayerMoveResponseSchema, PlayerMoveSchema
from app.schemas.players import (BasePlayerSchema, PlayerCreateSchema,
                                 PlayerDBCreateSchema, PlayerResponseSchema,
                                 PlayerSchema)
from app.services.validation_service import ValidationService


class PlayerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_player(self, user: WebAppUser, player_data: PlayerCreateSchema):
        obj_data = PlayerDBCreateSchema(player_id=user.id, name=user.username, map_id=player_data.map_id)
        player = await repository_player.create(self.session, obj_data)
        return PlayerResponseSchema(resources={}, base=None, in_base=False, **player.__dict__)

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
                joinedload(Player.base)
            ],
            map_id=map_id,
            player_id=telegram_id
        )
        if player is None:
            raise HTTPException(status_code=404, detail="The player does not exist")
        in_base = player.map_object_id == player.base.map_object_id if player.base else False
        player_data = PlayerSchema(in_base=in_base, **player.__dict__)
        resources = {resource.resource.name: resource.count for resource in player.resources}
        response = PlayerResponseSchema(resources=resources, **player_data.model_dump())
        return response

    async def move_player(self, telegram_id: int, player_data: PlayerMoveSchema):
        player = await repository_player.get(self.session, map_id=player_data.map_id, player_id=telegram_id)
        ValidationService.can_player_do_something(player)
        if player.map_object_id == player_data.map_object_id:
            raise HTTPException(status_code=409, detail="The user is already at this place")

        new_player_position = await repository_player.update(
            self.session, player_data, player_id=telegram_id, map_id=player_data.map_id
        )
        return PlayerMoveResponseSchema(new_map_object_id=new_player_position.map_object_id, player_id=player.id)

    @staticmethod
    def update_player_resources(
            player_resources: list[PlayerResources], building_costs: list[BuildingCost]
    ) -> None:
        costs = {cost.resource_id: cost.quantity for cost in building_costs}
        for resource in player_resources:
            if resource.resource_id in costs:
                resource.count -= costs[resource.resource_id]
