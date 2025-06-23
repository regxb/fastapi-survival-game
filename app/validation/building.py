from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Player
from app.validation.map import validate_map_area
from app.validation.player import does_player_have_enough_resources


async def validate_before_building(
        session: AsyncSession,
        building_costs,
        player: Player,
        x1: int,
        y1: int,
        map_id: int
):
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    if player.base:
        raise HTTPException(status_code=400, detail="Player already has a base on this map")
    if not does_player_have_enough_resources(building_costs, player.resources):
        raise HTTPException(status_code=400, detail="Not enough resources")
    await validate_map_area(session, x1, y1, map_id)
