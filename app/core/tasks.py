import asyncio

from .celery import celery_app
from .shedule_scripts import check_user_quizzes


@celery_app.task()
def check_user_quizzes_sync():
    asyncio.run(check_user_quizzes())
