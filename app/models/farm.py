from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FarmSession(Base):
    __tablename__ = 'farm_sessions'

    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(default="in_progress")
    map_id: Mapped[int] = mapped_column(ForeignKey('maps.id'))
    resource_id: Mapped[int] = mapped_column(ForeignKey('resources.id'))
    player_id: Mapped[int] = mapped_column(ForeignKey('players.id'))


class FarmMode(Base):
    __tablename__ = 'farm_modes'

    id: Mapped[int] = mapped_column(primary_key=True)
    mode: Mapped[str]
    total_minutes: Mapped[int]
    total_energy: Mapped[int]
    total_resources: Mapped[int]
    resource_zone_id: Mapped[int] = mapped_column(ForeignKey("resources_zones.id"))
