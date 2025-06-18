import asyncio
import json
from datetime import datetime, timedelta

from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.broker.scheduler_tasks.regenerate_energy import regenerate_energy, farming_resources
from app.broker.task import farm_session_task
from app.core import config
from app.core.database import redis_client

jobstores = {
    'default': RedisJobStore(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
    )
}

scheduler = AsyncIOScheduler(jobstores=jobstores)

scheduler.add_job(regenerate_energy, 'interval', seconds=60, id='regenerate_energy', replace_existing=True)
scheduler.add_job(farming_resources, 'interval', seconds=60, id='farming_resources', replace_existing=True)


async def process_tasks():
    while True:
        task_data_json = redis_client.lpop('task_queue')
        if task_data_json:
            task_data = json.loads(task_data_json)
            scheduler.add_job(farm_session_task, 'date',
                              run_date=datetime.now() + timedelta(minutes=task_data['total_minutes']),
                              kwargs={'task_data': task_data},
                              misfire_grace_time=None)
        await asyncio.sleep(1)


async def run_scheduler():
    scheduler.start()
    await process_tasks()


if __name__ == "__main__":
    asyncio.run(run_scheduler())
