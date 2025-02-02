from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Resource(Base):
    __tablename__ = 'resources'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    icon: Mapped[str]

    resource_zone: Mapped["ResourcesZone"] = relationship("ResourcesZone", back_populates="resource")
