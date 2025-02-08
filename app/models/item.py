from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.resource import Resource


class Item(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    icon: Mapped[str]
    type_id: Mapped[int] = mapped_column(ForeignKey('item_types.id'))

    recipe: Mapped[list["ItemRecipe"]] = relationship("ItemRecipe", uselist=True)
    type: Mapped["ItemType"] = relationship("ItemType")


class ItemType(Base):
    __tablename__ = 'item_types'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class ItemRecipe(Base):
    __tablename__ = 'recipe_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    resource_quantity: Mapped[int]
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"))

    resource: Mapped["Resource"] = relationship("Resource")
