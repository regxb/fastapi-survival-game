from app.models import Inventory, Player, PlayerBase, PlayerResources
from app.models.player import PlayerResourcesStorage, PlayerItemStorage
from app.repository.base import BaseRepository

PlayerRepository = BaseRepository[Player]
player_repository = PlayerRepository(Player)

PlayerBaseRepository = BaseRepository[PlayerBase]
player_base_repository = PlayerBaseRepository(PlayerBase)

PlayerResourcesRepository = BaseRepository[PlayerResources]
player_resource_repository = PlayerResourcesRepository(PlayerResources)

PlayerResourcesStorageRepository = BaseRepository[PlayerResourcesStorage]
player_resources_storage_repository = PlayerResourcesStorageRepository(PlayerResourcesStorage)

PlayerItemStorageRepository = BaseRepository[PlayerItemStorage]
player_item_storage_repository = PlayerItemStorageRepository(PlayerItemStorage)

InventoryRepository = BaseRepository[Inventory]
inventory_repository = InventoryRepository(Inventory)
