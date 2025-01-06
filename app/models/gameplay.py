from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.maps import ResourcesZone


class FarmSession(Base):
    __tablename__ = 'farm_sessions'

    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[str] = mapped_column(default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    end_time: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(default="in_progress")
    map_id: Mapped[int] = mapped_column(ForeignKey('maps.id'))
    resource_id: Mapped[int] = mapped_column(ForeignKey('resources.id'))
    player_id: Mapped[int] = mapped_column(ForeignKey('players.id'))


class Resource(Base):
    __tablename__ = 'resources'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    resource_zone: Mapped["ResourcesZone"] = relationship("ResourcesZone", back_populates="resource")


class BuildingCost(Base):
    __tablename__ = 'building_costs'

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]
    resource_id: Mapped[int] = mapped_column(ForeignKey('resources.id'))
    quantity: Mapped[int]

    resource: Mapped["Resource"] = relationship("Resource")
