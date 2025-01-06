from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.gameplay import get_active_farm_session
from app.crud.players import base_crud_player, get_player_with_position, create_player, get_player as crud_get_player
from app.schemas.gameplay import PlayerMoveSchema, PlayerMoveResponseSchema
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
        return BasePlayerSchema.model_validate(player)

    async def get_players(self, telegram_id: int):
        players = await base_crud_player.get_multi(self.session, user_id=telegram_id)
        return [BasePlayerSchema.model_validate(player) for player in players]

    async def get_player(self, map_id: int, telegram_id: int):
        player = await crud_get_player(self.session, map_id, telegram_id)
        if player is None:
            raise HTTPException(status_code=404, detail="The player does not exist")

        response = PlayerResponseSchema.model_validate(player)
        return response

    async def move_player(self, telegram_id:int, player_data: PlayerMoveSchema):
        if await self.check_player_map(player_data.map_object_id, player_data.map_id, telegram_id):
            player = await base_crud_player.update(
                self.session, player_data, user_id=telegram_id, map_id=player_data.map_id
            )
            return PlayerMoveResponseSchema(new_map_object_id=player.map_object_id, player_id=player.id)


    async def check_player_map(self, map_object_id: int, map_id:int, telegram_id: int):
        player = await base_crud_player.get(self.session, map_id=map_id, user_id=telegram_id)
        player_farm_session = await get_active_farm_session(self.session, telegram_id, map_id)
        if player_farm_session:
            raise HTTPException(status_code=400, detail="User is farming, movement is impossible")
        if not player or player.map_id is None:
            raise HTTPException(status_code=422, detail="Player is not on the map")
        if player.map_object_id == map_object_id:
            raise HTTPException(status_code=409, detail="The user is already at this place")
        return True
