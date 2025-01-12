from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gameplay_model import BuildingCost, FarmMode
from app.models.player_model import Player, PlayerResources
from app.services.map_service import MapService


class ValidationService:

    @staticmethod
    def can_user_build(building_costs: list[BuildingCost], player_resources: list[PlayerResources]):
        player_resource_dict = {res.resource_id: res.count for res in player_resources}
        for cost in building_costs:
            if player_resource_dict.get(cost.resource_id, 0) < cost.quantity:
                return False
        return True

    @staticmethod
    def can_player_do_something(player: Player):
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        if player.status != "waiting":
            raise HTTPException(status_code=400, detail="The player is currently doing some action")
        if not player or player.map_id is None:
            raise HTTPException(status_code=404, detail="Player is not on the map")

    @staticmethod
    async def validate_area_and_resources_for_building(
            session: AsyncSession, map_id: int, x1: int, y1: int, x2: int, y2: int, building_costs, player_resources
    ):
        if not await MapService(session).area_is_free(map_id, x1, y1, x2, y2):
            raise HTTPException(status_code=409, detail="The place is already taken")
        ValidationService.can_user_build(building_costs, player_resources)

    @staticmethod
    def is_farmable_area(map_object) -> None:
        if not map_object.is_farmable:
            raise HTTPException(status_code=400, detail="Can't farm in this area")

    @staticmethod
    def can_player_start_farming(player_energy: int, farm_mode: FarmMode):
        player_energy -= farm_mode.total_energy
        if player_energy < 0:
            raise HTTPException(status_code=400, detail="Not enough energy to start farming")
