from fastapi import APIRouter
from app.app_celery import celery_app

router = APIRouter(prefix="/test", tags=["test"])

@router.post("/")
async def test():
    celery_app.send_task('notification',countdown=60)
