from app.models import Inventory, Player, PlayerBase, PlayerResources
from app.models.player_model import PlayerBaseStorage
from app.repository.base_repository import BaseRepository

RepositoryPlayer = BaseRepository[Player]
repository_player = RepositoryPlayer(Player)

RepositoryPlayerBase = BaseRepository[PlayerBase]
repository_player_base = RepositoryPlayerBase(PlayerBase)

RepositoryPlayerResources = BaseRepository[PlayerResources]
repository_player_resource = RepositoryPlayerResources(PlayerResources)

RepositoryPlayerBaseStorage = BaseRepository[PlayerBaseStorage]
repository_player_base_storage = RepositoryPlayerBaseStorage(PlayerBaseStorage)

RepositoryInventory = BaseRepository[Inventory]
repository_inventory = RepositoryInventory(Inventory)
