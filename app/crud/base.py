from typing import TypeVar, Generic, Type, Sequence

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.players import Player

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]) -> None:
        self._model = model

    async def create(self, session: AsyncSession, obj_data: CreateSchemaType) -> ModelType:
        db_obj = self._model(**obj_data.model_dump())
        session.add(db_obj)
        await session.commit()
        return db_obj

    async def get_multi(self, session: AsyncSession, *args, **kwargs) -> Sequence[ModelType]:
        stmt = select(self._model).filter(*args).filter_by(**kwargs)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get(self, session: AsyncSession, *args, **kwargs) -> ModelType:
        stmt = select(self._model).filter(*args).filter_by(**kwargs)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_by_id(self, session: AsyncSession, id: int) -> ModelType:
        db_obj = await session.get(self._model, id)
        return db_obj

    async def update(self, session: AsyncSession, obj_in: UpdateSchemaType, **kwargs):
        db_obj = await self.get(session,**kwargs)
        if db_obj is not None:
            obj_data = db_obj.__dict__
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)
            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            session.add(db_obj)
            await session.commit()
        return db_obj
