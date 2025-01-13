from faststream import FastStream
from faststream.redis import RedisBroker

from app.broker.task import router
from app.broker.scheduler_tasks.regenerate_energy import router as regenerate_energy_router
from app.core.config import REDIS_URL

broker = RedisBroker(REDIS_URL)
broker.include_router(router)
broker.include_router(regenerate_energy_router)
app = FastStream(broker)


from taskiq_faststream import BrokerWrapper

taskiq_broker = BrokerWrapper(broker)


from taskiq_faststream import StreamScheduler
from taskiq.schedule_sources import LabelScheduleSource

taskiq_broker.task(
    message={},
    channel="regenerate_energy",
    schedule=[{
        "cron": "* * * * *",
    }],
)

scheduler = StreamScheduler(
    broker=taskiq_broker,
    sources=[LabelScheduleSource(taskiq_broker)],
)