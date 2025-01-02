from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.players import base_crud_player, get_player_with_position, create_player
from app.schemas.gameplay import PlayerMoveSchema
from app.schemas.players import PlayerCreateSchema, BasePlayerSchema, PlayerResponseSchema


class PlayerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_player(self, telegram_id: int, player_data: PlayerCreateSchema):
        player = await base_crud_player.get(
            self.session,
            map_id=player_data.map_id,
            user_id=telegram_id
        )
        if player:
            raise HTTPException(status_code=409, detail="The user already has a character on this map")
        player = await create_player(self.session, player_data.map_id, telegram_id)
        return player

    async def get_players(self):
        players = await base_crud_player.get_multi(self.session)
        return players

    async def get_player(self, player_id: int):
        player = await get_player_with_position(self.session, player_id)
        if player is None:
            raise HTTPException(status_code=404, detail="The player does not exist")

        response = PlayerResponseSchema(
            id=player_id,
            user_id=player.user_id,
            map_id=player.map_id,
            health=player.health,
            map_object_name=player.map_object.name,
            map_object_id=player.map_object_id
        )
        return response

    async def move_player(self, telegram_id:int, player_data: PlayerMoveSchema):
        if await self.check_player_map(player_data.map_object_id, player_data.map_id, telegram_id):
            return await base_crud_player.update(self.session, player_data, user_id=telegram_id)

    async def check_player_map(self, map_object_id: int, map_id:int, telegram_id: int):
        player = await base_crud_player.get(self.session, map_id=map_id, user_id=telegram_id)
        if not player or player.map_id is None:
            raise HTTPException(status_code=422, detail="Player is not on the map")
        if player.map_object_id == map_object_id:
            raise HTTPException(status_code=409, detail="The user is already at this place")
        return True
