from faststream import FastStream
from faststream.redis import RedisBroker

from app.faststream.task import router

broker = RedisBroker("redis://localhost:6379")
broker.include_router(router)
app = FastStream(broker)
