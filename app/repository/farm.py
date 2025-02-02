from app.models import FarmMode, FarmSession
from app.repository import BaseRepository

FarmModeRepository = BaseRepository[FarmMode]
farm_mode_repository = FarmModeRepository(FarmMode)

FarmSessionRepository = BaseRepository[FarmSession]
farm_session_repository = FarmSessionRepository(FarmSession)
