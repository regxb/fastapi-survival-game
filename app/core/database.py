from typing import AsyncGenerator

from apscheduler.jobstores import redis
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from app.core import config

DATABASE_URL = f"postgresql+asyncpg://{config.DB_USER}:{config.DB_PASS}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
TEST_DATABASE_URL = f"postgresql+asyncpg://{config.TEST_DB_USER}:{config.TEST_DB_PASS}@{config.DB_HOST}:{config.TEST_DB_PORT}/{config.TEST_DB_NAME}"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, password=config.REDIS_PASSWORD)



async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
