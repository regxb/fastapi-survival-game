from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.resource import Resource


class Item(Base):
    __tablename__ = 'items'
    __table_args__ = (
        CheckConstraint("max_count >= 0", name="ck_max_count_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    icon: Mapped[str]
    max_count: Mapped[int]
    type: Mapped[str]
    can_equip: Mapped[bool]

    recipe: Mapped[list["ItemRecipe"]] = relationship("ItemRecipe", uselist=True)
    stats: Mapped["ItemStat"] = relationship("ItemStat")


class ItemStat(Base):
    __tablename__ = 'item_stats'

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    damage: Mapped[int] = mapped_column(default=0)
    armor: Mapped[int] = mapped_column(default=0)


class ItemRecipe(Base):
    __tablename__ = 'recipe_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    resource_quantity: Mapped[int]
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"))

    resource: Mapped["Resource"] = relationship("Resource")


class EquipItem(Base):
    __tablename__ = 'equip_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    tier: Mapped[int]
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    player_id: Mapped[int] = mapped_column(ForeignKey('players.id'))

    item: Mapped["Item"] = relationship("Item")
