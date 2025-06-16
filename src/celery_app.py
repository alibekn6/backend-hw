from celery import Celery
from src.config import settings
from celery.schedules import crontab

celery_app = Celery(
    "project",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "src.celery_tasks",    # базовые демонстрационные таски
        "src.tasks.tasks",      # «бизнес-таски» (add_random_task и т.п.)
        "src.tasks.data_fetch",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
)

# Пример периодики (Celery Beat)
celery_app.conf.beat_schedule = {
    "cleanup-every-5-min": {
        "task": "src.celery_tasks.cleanup_old_data",
        "schedule": 300.0,
    },
    "auto-random-task-daily": {
        "task": "src.tasks.tasks.periodic_add_random_task",
        "schedule": 86400.0,
    },
    
    "fetch-cat-fact-every-minute": {
        "task": "tasks.data_fetch.fetch_and_save_data",
        "schedule": 86400.0,
        # "options": {"queue": "data_fetch_queue"},
    },
}

if __name__ == "__main__":
    celery_app.start()
