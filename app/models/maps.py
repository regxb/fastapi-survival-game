import enum

from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models.base import Base


class Map(Base):
    __tablename__ = 'maps'

    id: Mapped[int] = mapped_column(primary_key=True)
    height: Mapped[int] = mapped_column(nullable=True)
    width: Mapped[int] = mapped_column(nullable=True)

    map_objects: Mapped["MapObject"] = relationship(back_populates="map")


class MapObjectPosition(Base):
    __tablename__ = 'map_objects_position'

    id: Mapped[int] = mapped_column(primary_key=True)
    x1: Mapped[int]
    y1: Mapped[int]
    x2: Mapped[int]
    y2: Mapped[int]
    map_object_id: Mapped[int] = mapped_column(ForeignKey('map_objects.id'))

    map_object: Mapped["MapObject"] = relationship(back_populates="position")


class MapObject(Base):
    __tablename__ = 'map_objects'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    map_id: Mapped[int] = mapped_column(ForeignKey('maps.id'))
    type: Mapped[str] = mapped_column(nullable=True)
    is_farmable: Mapped[bool]

    map: Mapped["Map"] = relationship(back_populates="map_objects")
    position: Mapped["MapObjectPosition"] = relationship(back_populates="map_object")
    player: Mapped["Player"] = relationship(back_populates="map_object")


class PlayerBase(Base):
    __tablename__ = 'players_bases'

    id: Mapped[int] = mapped_column(primary_key=True)
    defense_level: Mapped[int] = mapped_column(default=1)
    map_object_id: Mapped[int] = mapped_column(ForeignKey('map_objects.id'))
    map_id: Mapped[int] = mapped_column(ForeignKey('maps.id'))
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.telegram_id'))


class ResourcesZone(Base):
    __tablename__ = 'resources_zones'

    id: Mapped[int] = mapped_column(primary_key=True)
    curren_resource_amount: Mapped[int] = mapped_column(default=0)
    regeneration_rate: Mapped[int] = mapped_column(default=10)
    map_object_id: Mapped[int] = mapped_column(ForeignKey('map_objects.id'))
    resource_id: Mapped[int] = mapped_column(ForeignKey('resources.id'))
    map_id: Mapped[int] = mapped_column(ForeignKey('maps.id'))
