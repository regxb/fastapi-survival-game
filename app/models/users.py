from datetime import datetime

from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    photo_url: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    players: Mapped[list["Player"]] = relationship(back_populates="user", uselist=True)