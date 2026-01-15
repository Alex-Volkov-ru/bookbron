from celery import Celery
from app.config import settings
from app.celery_beat_schedule import beat_schedule

celery_app = Celery(
    "booking_app",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.notifications", "app.tasks.reminders"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    beat_schedule=beat_schedule,
)

