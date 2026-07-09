from celery import Celery

from src.config import settings


celery_app = Celery(
    "file_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.autodiscover_tasks(["src.tasks.handlers"], force=True)