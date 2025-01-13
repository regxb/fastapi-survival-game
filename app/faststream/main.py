from faststream import FastStream
from faststream.redis import RedisBroker

from app.faststream.task import router
from app.core.config import REDIS_URL

broker = RedisBroker(REDIS_URL)
broker.include_router(router)
app = FastStream(broker)
