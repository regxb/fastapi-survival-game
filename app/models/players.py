from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.gameplay import FarmSession
from app.models.maps import MapObject
from app.models.maps import PlayerBase
from app.models.users import User


class Player(Base):
    __tablename__ = 'players'

    id: Mapped[int] = mapped_column(primary_key=True)
    health: Mapped[int] = mapped_column(default=100)
    energy: Mapped[int] = mapped_column(default=100)
    resource_multiplier: Mapped[int] = mapped_column(default=1)
    energy_multiplier: Mapped[int] = mapped_column(default=1)
    status: Mapped[str] = mapped_column(default="waiting")
    map_id: Mapped[int] = mapped_column(ForeignKey('maps.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.telegram_id'))
    map_object_id: Mapped[int] = mapped_column(ForeignKey('map_objects.id'), default=1)

    map_object: Mapped["MapObject"] = relationship("MapObject", back_populates="players")
    user: Mapped["User"] = relationship("User", back_populates="players")
    resources: Mapped[list["PlayerResources"]] = relationship("PlayerResources", uselist=True)
    farm_sessions: Mapped[list["FarmSession"]] = relationship("FarmSession", uselist=True)
    base: Mapped["PlayerBase"] = relationship("PlayerBase", back_populates="player")


class PlayerResources(Base):
    __tablename__ = 'players_resources'

    id: Mapped[int] = mapped_column(primary_key=True)
    count: Mapped[int] = mapped_column(default=0)
    player_id: Mapped[int] = mapped_column(ForeignKey('players.id'))
    resource_id: Mapped[int] = mapped_column(ForeignKey('resources.id'))

    player: Mapped["Player"] = relationship("Player", back_populates="resources")


class Inventory(Base):
    __tablename__ = 'inventories'

    id: Mapped[int] = mapped_column(primary_key=True)
    slots: Mapped[int] = mapped_column(default=5)
    player_id: Mapped[int] = mapped_column(ForeignKey('players.id'))
    resource_id: Mapped[int] = mapped_column(ForeignKey('resources.id'), nullable=True)
