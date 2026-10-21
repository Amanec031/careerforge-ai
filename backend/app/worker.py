from celery import Celery

from app.config import get_settings

celery_app = Celery("careerforge", broker=get_settings().redis_url,
                    backend=get_settings().redis_url)
celery_app.conf.update(task_acks_late=True, task_time_limit=300, task_soft_time_limit=240,
                       timezone="UTC", broker_connection_retry_on_startup=True)


@celery_app.task(name="careerforge.ping")
def ping() -> str:
    return "pong"
