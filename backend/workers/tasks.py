"""Celery workers — orchestration only; calls existing AI/services unchanged."""

import asyncio
import uuid
from datetime import datetime
from backend.celery_app import celery_app
from backend.services.progress_service import update_progress


def _run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(coro)
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


@celery_app.task(bind=True, name="backend.workers.tasks.parse_resume_batch", max_retries=3)
def parse_resume_batch(self, batch_id: str, job_id: str, file_data: list):
    task_id = self.request.id
    try:
        update_progress(task_id, "batch_parse", "processing", "parsing", 5, "Starting batch parse", job_id=job_id)
        from backend.services.batch_service import process_batch_resumes

        async def _run():
            await process_batch_resumes(uuid.UUID(batch_id), uuid.UUID(job_id), file_data, task_id)

        _run_async(_run())
        update_progress(task_id, "batch_parse", "completed", "done", 100, "Batch complete", job_id=job_id)
        return {"batch_id": batch_id, "status": "completed"}
    except Exception as exc:
        update_progress(task_id, "batch_parse", "failed", "error", 0, error=str(exc), job_id=job_id)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, name="backend.workers.tasks.run_ranking_task", max_retries=2)
def run_ranking_task(self, job_id: str, user_id: str, run_id: str):
    task_id = self.request.id
    try:
        update_progress(task_id, "ranking", "processing", "loading", 10, "Loading candidates", job_id=job_id)
        from backend.services.ranking_service import execute_ranking_run

        async def _run():
            await execute_ranking_run(uuid.UUID(job_id), uuid.UUID(user_id), uuid.UUID(run_id), task_id)

        _run_async(_run())
        update_progress(task_id, "ranking", "completed", "done", 100, "Ranking complete", job_id=job_id)
        return {"run_id": run_id, "status": "completed"}
    except Exception as exc:
        update_progress(task_id, "ranking", "failed", "error", 0, error=str(exc), job_id=job_id)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, name="backend.workers.tasks.generate_interview_pack_task", max_retries=2)
def generate_interview_pack_task(self, job_id: str, candidate_id: str):
    task_id = self.request.id
    try:
        update_progress(task_id, "interview_pack", "processing", "generating", 20, "Generating interview pack", job_id=job_id)
        from backend.services.interview_pack_service import create_pack_for_candidate

        async def _run():
            return await create_pack_for_candidate(uuid.UUID(job_id), uuid.UUID(candidate_id))

        pack_id = _run_async(_run())
        update_progress(task_id, "interview_pack", "completed", "done", 100, "Pack ready", job_id=job_id, meta={"pack_id": str(pack_id)})
        return {"pack_id": str(pack_id)}
    except Exception as exc:
        update_progress(task_id, "interview_pack", "failed", "error", 0, error=str(exc), job_id=job_id)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, name="backend.workers.tasks.generate_screening_test_task", max_retries=2)
def generate_screening_test_task(self, job_id: str, candidate_id: str):
    task_id = self.request.id
    try:
        update_progress(task_id, "screening_test", "processing", "generating", 20, "Generating test", job_id=job_id)
        from backend.services.screening_service import create_test_for_candidate

        async def _run():
            return await create_test_for_candidate(uuid.UUID(job_id), uuid.UUID(candidate_id))

        test_id = _run_async(_run())
        update_progress(task_id, "screening_test", "completed", "done", 100, "Test ready", job_id=job_id, meta={"test_id": str(test_id)})
        return {"test_id": str(test_id)}
    except Exception as exc:
        update_progress(task_id, "screening_test", "failed", "error", 0, error=str(exc), job_id=job_id)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, name="backend.workers.tasks.export_shortlist_task", max_retries=2)
def export_shortlist_task(self, job_id: str, export_format: str, user_id: str):
    task_id = self.request.id
    try:
        update_progress(task_id, "export", "processing", "exporting", 30, f"Exporting {export_format}", job_id=job_id)
        from backend.services.export_task_service import run_export

        async def _run():
            return await run_export(uuid.UUID(job_id), export_format)

        result = _run_async(_run())
        update_progress(task_id, "export", "completed", "done", 100, "Export ready", job_id=job_id, meta=result)
        return result
    except Exception as exc:
        update_progress(task_id, "export", "failed", "error", 0, error=str(exc), job_id=job_id)
        raise self.retry(exc=exc)
