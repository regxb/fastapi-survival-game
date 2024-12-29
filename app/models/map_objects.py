from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models.base import Base


class Map(Base):
    __tablename__ = 'maps'

    id: Mapped[int] = mapped_column(primary_key=True)
    size: Mapped[int]

    map_objects: Mapped["MapObject"] = relationship(back_populates="map")


class TypeMapObject(Base):
    __tablename__ = 'type_map_objects'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    map_object: Mapped["MapObject"] = relationship(back_populates="type")


class MapObject(Base):
    __tablename__ = 'map_objects'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    x: Mapped[int]
    y: Mapped[int]
    height: Mapped[int]
    width: Mapped[int]
    map_id: Mapped[int] = mapped_column(ForeignKey('maps.id'))
    type_id: Mapped[int] = mapped_column(ForeignKey("type_map_objects.id"))

    map: Mapped["Map"] = relationship(back_populates="map_objects")
    type: Mapped["TypeMapObject"] = relationship(back_populates="map_object")
