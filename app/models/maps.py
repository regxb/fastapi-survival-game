from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property

from app.models.base import Base


class Map(Base):
    __tablename__ = 'maps'

    id: Mapped[int] = mapped_column(primary_key=True)
    height: Mapped[int] = mapped_column(nullable=True)
    width: Mapped[int] = mapped_column(nullable=True)

    map_objects: Mapped[list["MapObject"]] = relationship("MapObject", back_populates="map", uselist=True)


class MapObject(Base):
    __tablename__ = 'map_objects'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    map_id: Mapped[int] = mapped_column(ForeignKey('maps.id'))
    type: Mapped[str] = mapped_column(nullable=True)
    is_farmable: Mapped[bool]

    map: Mapped["Map"] = relationship("Map", back_populates="map_objects")
    position: Mapped["MapObjectPosition"] = relationship("MapObjectPosition", back_populates="map_object")
    players: Mapped[list["Player"]] = relationship("Player", back_populates="map_object", uselist=True)
    resource_zone: Mapped["ResourcesZone"] = relationship("ResourcesZone", back_populates="map_object")


class MapObjectPosition(Base):
    __tablename__ = 'map_objects_position'

    id: Mapped[int] = mapped_column(primary_key=True)
    x1: Mapped[int]
    y1: Mapped[int]
    x2: Mapped[int]
    y2: Mapped[int]
    map_object_id: Mapped[int] = mapped_column(ForeignKey('map_objects.id'))

    map_object: Mapped["MapObject"] = relationship("MapObject", back_populates="position")


class PlayerBase(Base):
    __tablename__ = 'players_bases'

    id: Mapped[int] = mapped_column(primary_key=True)
    defense_level: Mapped[int] = mapped_column(default=1)
    map_object_id: Mapped[int] = mapped_column(ForeignKey('map_objects.id'))
    map_id: Mapped[int] = mapped_column(ForeignKey('maps.id'))
    owner_id: Mapped[int] = mapped_column(ForeignKey('players.id'))

    map_object: Mapped["MapObject"] = relationship("MapObject")
    player: Mapped["Player"] = relationship("Player", back_populates="base")


class ResourcesZone(Base):
    __tablename__ = 'resources_zones'

    id: Mapped[int] = mapped_column(primary_key=True)
    map_object_id: Mapped[int] = mapped_column(ForeignKey('map_objects.id'))
    resource_id: Mapped[int] = mapped_column(ForeignKey('resources.id'))
    map_id: Mapped[int] = mapped_column(ForeignKey('maps.id'))

    map_object: Mapped["MapObject"] = relationship("MapObject", back_populates="resource_zone")
    resource: Mapped["Resource"] = relationship("Resource", back_populates="resource_zone")
    farm_modes: Mapped[list["FarmMode"]] = relationship("FarmMode", uselist=True)


class FarmMode(Base):
    __tablename__ = 'farm_modes'

    id: Mapped[int] = mapped_column(primary_key=True)
    mode: Mapped[str]
    total_minutes: Mapped[int]
    total_energy: Mapped[int]
    total_resources: Mapped[int]
    resource_zone_id: Mapped["ResourcesZone"] = mapped_column(ForeignKey("resources_zones.id"))
