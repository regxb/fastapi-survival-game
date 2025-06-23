import asyncio
import json
from datetime import datetime

from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.broker.scheduler_tasks.regenerate_energy import regenerate
from app.broker.task import start_farm_session
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

scheduler.add_job(regenerate, 'interval', seconds=60, id='regenerate_energy', replace_existing=True)


async def process_tasks():
    while True:
        task_data_json = redis_client.lpop('task_queue')
        if task_data_json:
            task_data = json.loads(task_data_json)

            scheduler.add_job(start_farm_session, 'date',
                              run_date=datetime.now(),
                              args=[
                                  task_data['total_minutes'],
                                  task_data['farm_session_id'],
                                  task_data['resource_id'],
                                  task_data['player_id'],
                                  task_data["resources_before_farming"],
                              ],
                              misfire_grace_time=None)

        await asyncio.sleep(1)


async def run_scheduler():
    scheduler.start()
    await process_tasks()


if __name__ == "__main__":
    asyncio.run(run_scheduler())
