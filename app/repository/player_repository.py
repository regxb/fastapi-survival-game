from app.models.player_model import Player, PlayerBase, PlayerResources, PlayerBaseStorage
from app.repository.base_repository import BaseRepository

RepositoryPlayer = BaseRepository[Player]
repository_player = RepositoryPlayer(Player)

RepositoryPlayerBase = BaseRepository[PlayerBase]
repository_player_base = RepositoryPlayerBase(PlayerBase)

RepositoryPlayerResources = BaseRepository[PlayerResources]
repository_player_resource = RepositoryPlayerBase(PlayerResources)

RepositoryPlayerBaseStorage = BaseRepository(PlayerBaseStorage)
repository_player_base_storage = RepositoryPlayerBase(PlayerBaseStorage)
