from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.players import base_crud_player
from app.crud.users import base_crud_user
from app.models.players import Player
from app.schemas.gameplay import PlayerMoveSchema
from app.schemas.players import PlayerCreateSchema, PlayerDBSchema


class PlayerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_player(self, player_data: PlayerCreateSchema):
        user = await base_crud_user.get(self.session, telegram_id=player_data.telegram_id)
        update_player_data = PlayerDBSchema(username=player_data.username, user_id=user.id)
        return await base_crud_player.create(self.session, update_player_data)

    async def get_players(self):
        players = await base_crud_player.get_multi(self.session)
        return players

    async def get_player(self, player_id: int):
        player = await base_crud_player.get_by_id(self.session, player_id)
        return player

    async def move_player(self, player_data: PlayerMoveSchema):
        user = await base_crud_user.get(self.session, telegram_id=player_data.telegram_id)
        result = await base_crud_player.update(self.session, player_data, user_id=user.id)
