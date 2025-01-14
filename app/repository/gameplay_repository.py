from app.models.gameplay_model import BuildingCost, FarmMode, FarmSession, Item
from app.repository.base_repository import BaseRepository

RepositoryFarmMode = BaseRepository[FarmMode]
repository_farm_mode = RepositoryFarmMode(FarmMode)

RepositoryFarmSession = BaseRepository[FarmSession]
repository_farm_session = RepositoryFarmSession(FarmSession)

RepositoryBuildingCost = BaseRepository[BuildingCost]
repository_building_cost = RepositoryBuildingCost(BuildingCost)

RepositoryItem = BaseRepository[Item]
repository_item = RepositoryItem(Item)
