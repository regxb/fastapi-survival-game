from fastapi import HTTPException

from app.models import FarmSession


def validate_farm_session(farm_session: FarmSession):
    if not farm_session:
        raise HTTPException(status_code=404, detail="Farm session not found")
