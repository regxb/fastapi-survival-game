from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.resource import Resource


class BuildingCost(Base):
    __tablename__ = 'building_costs'

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]
    resource_id: Mapped[int] = mapped_column(ForeignKey('resources.id'))
    resource_quantity: Mapped[int]

    resource: Mapped["Resource"] = relationship("Resource")
