from app.models import Inventory, Player, PlayerBase, PlayerResources
from app.models.player_model import PlayerResourcesStorage, PlayerItemStorage
from app.repository.base_repository import BaseRepository

RepositoryPlayer = BaseRepository[Player]
repository_player = RepositoryPlayer(Player)

RepositoryPlayerBase = BaseRepository[PlayerBase]
repository_player_base = RepositoryPlayerBase(PlayerBase)

RepositoryPlayerResources = BaseRepository[PlayerResources]
repository_player_resource = RepositoryPlayerResources(PlayerResources)

RepositoryPlayerResourcesStorage = BaseRepository[PlayerResourcesStorage]
repository_player_resources_storage = RepositoryPlayerResourcesStorage(PlayerResourcesStorage)

RepositoryPlayerItemStorage = BaseRepository[PlayerItemStorage]
repository_player_item_storage = RepositoryPlayerItemStorage(PlayerItemStorage)

RepositoryInventory = BaseRepository[Inventory]
repository_inventory = RepositoryInventory(Inventory)
