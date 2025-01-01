from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.maps import base_crud_map_object


class GameplayService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def farm_resource(self, map_id: int, object_id: int, player_id: int):
        map_object = base_crud_map_object.get_by_id(object_id)