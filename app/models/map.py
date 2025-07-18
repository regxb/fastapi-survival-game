from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.resource import Resource


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
    type: Mapped[str]
    is_farmable: Mapped[bool]

    map: Mapped["Map"] = relationship("Map", back_populates="map_objects")
    position: Mapped["MapObjectPosition"] = relationship("MapObjectPosition", back_populates="map_object")
    players: Mapped[list["Player"]] = relationship("Player", back_populates="map_object", uselist=True, lazy="joined")  # type: ignore
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


class ResourcesZone(Base):
    __tablename__ = 'resources_zones'

    id: Mapped[int] = mapped_column(primary_key=True)
    map_object_id: Mapped[int] = mapped_column(ForeignKey('map_objects.id'))
    resource_id: Mapped[int] = mapped_column(ForeignKey('resources.id'))
    map_id: Mapped[int] = mapped_column(ForeignKey('maps.id'))

    map_object: Mapped["MapObject"] = relationship("MapObject", back_populates="resource_zone")
    resource: Mapped["Resource"] = relationship("Resource", back_populates="resource_zone")
