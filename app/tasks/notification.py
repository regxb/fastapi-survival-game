from datetime import datetime

from app.app_celery import celery_app


@celery_app.task(name='notification')
def notification():
    print('Привет '+datetime.now().strftime('%Y-%m-%d %H:%M:%S'))