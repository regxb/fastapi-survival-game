from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Player(Base):
    __tablename__ = 'players'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    health: Mapped[int] = mapped_column(default=100)
    map_id: Mapped[int] = mapped_column(ForeignKey('maps.id'), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    map_object_id: Mapped[int] = mapped_column(ForeignKey('map_objects.id'), nullable=True)


class Resource(Base):
    __tablename__ = 'resources'

    id: Mapped[int] = mapped_column(primary_key=True)
    wood: Mapped[str]
    stone: Mapped[str]


class Inventory(Base):
    __tablename__ = 'inventories'

    id: Mapped[int] = mapped_column(primary_key=True)
    slots: Mapped[int] = mapped_column(default=5)
    player_id: Mapped[int] = mapped_column(ForeignKey('players.id'))
    resource_id: Mapped[int] = mapped_column(ForeignKey('resources.id'), nullable=True)
