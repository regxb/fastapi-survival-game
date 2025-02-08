from abc import ABC, abstractmethod
from typing import TypeVar

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseService:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    async def commit_or_rollback(session: AsyncSession) -> None:
        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e.orig))


class BaseTransferService(ABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def transfer(self, *args, **kwargs):
        pass
