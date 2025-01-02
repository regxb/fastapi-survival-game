from celery import Celery
from app.core.config import REDIS_URL


celery_app = Celery(
    "tasks",
    broker=str(REDIS_URL),
    backend=str(REDIS_URL),
    include=[
        "app.tasks.notification",
    ],
    timezone="Europe/Moscow",
)

celery_app.conf.beat_schedule = {
    'notification': {
        'task': 'notification',
        'schedule': 5.0
    },
}