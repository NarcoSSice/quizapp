from celery import Celery
from .settings import settings

celery_app = Celery(
    "app.core.celery",
    broker=f"redis://{settings.redis.HOST}:{settings.redis.PORT}/1",
    include=["app.core.tasks"],
)

celery_app.conf.beat_schedule = {
    "check-quizzes-daily": {
        "task": "app.core.tasks.check_user_quizzes_sync",
        "schedule": 24 * 60 * 60,
    },
}
