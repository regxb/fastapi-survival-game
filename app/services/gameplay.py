from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.maps import base_crud_map_object, get_farm_zone
from app.crud.players import base_crud_player, get_player_with_map_object


class GameplayService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def farm_resource(self, map_id: int, telegram_id: int):
        player = await get_player_with_map_object(self.session, map_id, telegram_id)
        if not player.map_object.is_farmable:
            raise HTTPException(status_code=400, detail="Can't farm in this area")
        farm_zone = await get_farm_zone(self.session, map_id, player.map_object_id)
        print(farm_zone)
        print(player.map_object.is_farmable)