from app.models import BuildingCost
from app.repository import BaseRepository

BuildingCostRepository = BaseRepository[BuildingCost]
building_cost_repository = BuildingCostRepository(BuildingCost)
