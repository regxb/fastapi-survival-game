import datetime
from typing import Optional

from app.schemas import FarmSessionSchema


def serialize_farm_session(farm_session) -> Optional[FarmSessionSchema]:
    if not farm_session:
        return None
    total_seconds = int((farm_session.end_time - farm_session.start_time).total_seconds())
    seconds_pass = int((datetime.datetime.now() - farm_session.start_time).total_seconds())
    return FarmSessionSchema(total_seconds=total_seconds, seconds_pass=seconds_pass)
