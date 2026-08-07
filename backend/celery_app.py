from celery import Celery
from backend.config import get_settings

settings = get_settings()

celery_app = Celery(
    "shortlister",
    broker=settings.broker_url,
    backend=settings.result_backend,
    include=["backend.workers.tasks"],
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
    task_default_retry_delay=30,
    task_max_retries=3,
    task_routes={
        "backend.workers.tasks.parse_resume_batch": {"queue": "parse"},
        "backend.workers.tasks.run_ranking_task": {"queue": "rank"},
        "backend.workers.tasks.generate_interview_pack_task": {"queue": "generate"},
        "backend.workers.tasks.generate_screening_test_task": {"queue": "generate"},
        "backend.workers.tasks.export_shortlist_task": {"queue": "export"},
    },
    task_annotations={
        "*": {"rate_limit": "100/m"},
    },
)
