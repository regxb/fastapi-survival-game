from typing import Any, Dict, Generic, Optional, Sequence, Type, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import and_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]) -> None:
        self._model = model

    async def create(self, session: AsyncSession, obj_data: CreateSchemaType) -> ModelType:
        db_obj = self._model(**obj_data.model_dump())
        try:
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
        except IntegrityError as e:
            raise HTTPException(status_code=500, detail=str(e.orig))
        return db_obj

    async def delete(self, session: AsyncSession, obj_data: CreateSchemaType) -> None:
        db_obj = self._model(**obj_data.model_dump())
        try:
            await session.delete(db_obj)
        except IntegrityError as e:
            raise HTTPException(status_code=500, detail=str(e.orig))

    async def get_multi(
            self,
            session: AsyncSession,
            *args,
            offset: int = 0,
            limit: int = 100,
            options: Optional[Sequence] = None,
            **kwargs
    ) -> Sequence[ModelType]:
        stmt = select(self._model).filter(*args).filter_by(**kwargs).offset(offset).limit(limit)
        if options:
            stmt = stmt.options(*options)

        result = await session.execute(stmt)
        scalars = result.scalars()

        return scalars.unique().all() if options else scalars.all()

    async def get(
            self,
            session: AsyncSession,
            options: Sequence | None = None,
            *args,
            **kwargs
    ) -> ModelType:
        stmt = select(self._model).filter(*args).filter_by(**kwargs)
        if options:
            stmt = stmt.options(*options)
        result = await session.execute(stmt)
        # if result is None:
        #     raise HTTPException(status_code=404, detail=f"{self._model.__name__} Not found")
        return result.unique().scalar_one_or_none()

    async def get_by_id(self, session: AsyncSession, id: int) -> ModelType:
        db_obj = await session.get(self._model, id)
        # if db_obj is None:
        #     raise HTTPException(status_code=404, detail=f"{self._model.__name__} Not found")
        return db_obj

    async def update(
            self,
            session: AsyncSession,
            obj_in: UpdateSchemaType,
            db_obj: Optional[ModelType] = None,
            **kwargs):
        db_obj = db_obj or await self.get(session, **kwargs)
        if db_obj is not None:
            obj_data = db_obj.__dict__
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)
            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            try:
                session.add(db_obj)
                await session.commit()
            except IntegrityError as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=str(e.orig))
        await session.refresh(db_obj)
        return db_obj

    @staticmethod
    async def update_multiple(
            session: AsyncSession,
            model: Type[ModelType],
            obj_in: UpdateSchemaType,
            where_clause: Optional[Dict[str, Any]] = None,
    ) -> int:
        try:
            if isinstance(obj_in, BaseModel):
                update_data = obj_in.model_dump(exclude_unset=True)
            else:
                update_data = obj_in

            stmt = update(model).values(**update_data)

            if where_clause:
                conditions = []
                for key, value in where_clause.items():
                    if isinstance(value, tuple):
                        operator, val = value
                        if operator == ">":
                            conditions.append(getattr(model, key) > val)
                        elif operator == "<":
                            conditions.append(getattr(model, key) < val)
                        elif operator == ">=":
                            conditions.append(getattr(model, key) >= val)
                        elif operator == "<=":
                            conditions.append(getattr(model, key) <= val)
                        elif operator == "==" or operator == "=":
                            conditions.append(getattr(model, key) == val)
                        elif operator == "!=":
                            conditions.append(getattr(model, key) != val)
                        else:
                            raise ValueError(f"Unsupported operator: {operator}")
                    else:
                        conditions.append(getattr(model, key) == value)

                stmt = stmt.where(and_(*conditions))

            result = await session.execute(stmt)
            await session.commit()

            return result.rowcount

        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=400)
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
