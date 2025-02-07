from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import BIGINT

from app.models.base import Base
from app.models.farm import FarmSession
from app.models.item import Item
from app.models.map import MapObject
from app.models.resource import Resource


class Player(Base):
    __tablename__ = 'players'

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(BIGINT)
    name: Mapped[str] = mapped_column(default='Player')
    health: Mapped[int] = mapped_column(default=100)
    energy: Mapped[int] = mapped_column(default=100)
    resource_multiplier: Mapped[int] = mapped_column(default=1)
    energy_multiplier: Mapped[int] = mapped_column(default=1)
    inventory_slots: Mapped[int] = mapped_column(default=10)
    status: Mapped[str] = mapped_column(default="waiting")
    map_id: Mapped[int] = mapped_column(ForeignKey('maps.id'))
    map_object_id: Mapped[int] = mapped_column(ForeignKey('map_objects.id'), default=1)

    map_object: Mapped["MapObject"] = relationship("MapObject", back_populates="players")
    resources: Mapped[list["PlayerResources"]] = relationship("PlayerResources", uselist=True)
    farm_sessions: Mapped[list["FarmSession"]] = relationship("FarmSession", uselist=True)
    base: Mapped["PlayerBase"] = relationship("PlayerBase", back_populates="player")
    inventory: Mapped[list["Inventory"]] = relationship("Inventory", uselist=True)

    __table_args__ = (UniqueConstraint('player_id', 'map_id', name='idx_uniq_player_id'),)


class PlayerResources(Base):
    __tablename__ = 'players_resources'

    id: Mapped[int] = mapped_column(primary_key=True)
    resource_quantity: Mapped[int] = mapped_column(default=0)
    player_id: Mapped[int] = mapped_column(ForeignKey('players.id'))
    resource_id: Mapped[int] = mapped_column(ForeignKey('resources.id'))

    player: Mapped["Player"] = relationship("Player", back_populates="resources")
    resource: Mapped["Resource"] = relationship("Resource")


class Inventory(Base):
    __tablename__ = 'inventories'

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey('players.id'))
    item_id: Mapped[int] = mapped_column(ForeignKey('items.id'))
    tier: Mapped[int] = mapped_column(default=1)
    count: Mapped[int] = mapped_column(default=1)
    active: Mapped[bool] = mapped_column(default=False)

    item: Mapped["Item"] = relationship("Item")


class PlayerBase(Base):
    __tablename__ = 'players_bases'

    id: Mapped[int] = mapped_column(primary_key=True)
    defense_level: Mapped[int] = mapped_column(default=1)
    map_object_id: Mapped[int] = mapped_column(ForeignKey('map_objects.id'))
    map_id: Mapped[int] = mapped_column(ForeignKey('maps.id'))
    owner_id: Mapped[int] = mapped_column(ForeignKey('players.id'))

    map_object: Mapped["MapObject"] = relationship("MapObject")
    player: Mapped["Player"] = relationship("Player", back_populates="base")
    resources: Mapped[list["PlayerResourcesStorage"]] = relationship("PlayerResourcesStorage", uselist=True)
    items: Mapped[list["PlayerItemStorage"]] = relationship("PlayerItemStorage", uselist=True)


class PlayerResourcesStorage(Base):
    __tablename__ = 'players_resources_storage'

    id: Mapped[int] = mapped_column(primary_key=True)
    resource_quantity: Mapped[int] = mapped_column(default=0)
    resource_id: Mapped[int] = mapped_column(ForeignKey('resources.id'))
    player_base_id: Mapped[int] = mapped_column(ForeignKey('players_bases.id'))
    player_id: Mapped[int] = mapped_column(ForeignKey('players.id'))

    resource: Mapped["Resource"] = relationship("Resource")


class PlayerItemStorage(Base):
    __tablename__ = 'players_items_storage'

    id: Mapped[int] = mapped_column(primary_key=True)
    tier: Mapped[int] = mapped_column(default=1)
    item_id: Mapped[int] = mapped_column(ForeignKey('items.id'))
    player_base_id: Mapped[int] = mapped_column(ForeignKey('players_bases.id'))
    player_id: Mapped[int] = mapped_column(ForeignKey('players.id'))
    count: Mapped[int] = mapped_column(default=1)

    item: Mapped["Item"] = relationship("Item")
