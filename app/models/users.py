from datetime import datetime

from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int]
    username: Mapped[str]
    photo_url: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
