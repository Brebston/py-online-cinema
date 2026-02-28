from celery import Celery
from celery.schedules import crontab

from config import get_settings


settings = get_settings()

celery_app = Celery(
    "online_cinema",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.beat_schedule = {
    "cleanup-expired-tokens-every-hour": {
        "task": "tasks.cleanup.cleanup_expired_tokens",
        "schedule": crontab(minute=0, hour="*/1"),
    }
}

celery_app.autodiscover_tasks(["tasks"])