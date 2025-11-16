"""Celery application configuration."""
from celery import Celery
from celery.schedules import crontab
from ..config import settings

celery_app = Celery(
    "mood_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    'reset-monthly-quotas': {
        'task': 'app.tasks.quota_tasks.reset_monthly_quotas',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight UTC
    },
    'check-quota-warnings': {
        'task': 'app.tasks.quota_tasks.check_quota_warnings',
        'schedule': crontab(hour=12, minute=0),  # Daily at noon UTC
    },
}

# Import tasks
from ..services import dataset_service, training_service, analysis_service
from . import quota_tasks

celery_app.task(dataset_service.generate_dataset_task)
celery_app.task(training_service.train_models_task)
celery_app.task(analysis_service.analyze_batch_task)
celery_app.task(quota_tasks.reset_monthly_quotas)
celery_app.task(quota_tasks.check_quota_warnings)
