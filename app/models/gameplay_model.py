from datetime import datetime

from sqlalchemy import ForeignKey, DateTime,String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import Base
from app.models.map_model import ResourcesZone


class FarmSession(Base):
    __tablename__ = 'farm_sessions'

    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(default="in_progress")
    map_id: Mapped[int] = mapped_column(ForeignKey('maps.id'))
    resource_id: Mapped[int] = mapped_column(ForeignKey('resources.id'))
    player_id: Mapped[int] = mapped_column(ForeignKey('players.id'))


class Resource(Base):
    __tablename__ = 'resources'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    icon: Mapped[str]

    resource_zone: Mapped["ResourcesZone"] = relationship("ResourcesZone", back_populates="resource")


class BuildingCost(Base):
    __tablename__ = 'building_costs'

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]
    resource_id: Mapped[int] = mapped_column(ForeignKey('resources.id'))
    resource_quantity: Mapped[int]

    resource: Mapped["Resource"] = relationship("Resource")


class FarmMode(Base):
    __tablename__ = 'farm_modes'

    id: Mapped[int] = mapped_column(primary_key=True)
    mode: Mapped[str]
    total_minutes: Mapped[int]
    total_energy: Mapped[int]
    total_resources: Mapped[int]
    resource_zone_id: Mapped[int] = mapped_column(ForeignKey("resources_zones.id"))


class Item(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    icon: Mapped[str]

    recipe: Mapped[list["ItemRecipe"]] = relationship("ItemRecipe", uselist=True)


class ItemRecipe(Base):
    __tablename__ = 'recipe_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    resource_quantity: Mapped[int]
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"))

    resource: Mapped["Resource"] = relationship("Resource")
