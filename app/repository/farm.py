from app.models import FarmSession
from app.repository import BaseRepository

FarmSessionRepository = BaseRepository[FarmSession]
farm_session_repository = FarmSessionRepository(FarmSession)
