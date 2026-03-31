"""
Celery application and async resume parsing tasks.
"""
import uuid
import asyncio
from celery import Celery
from app.config import settings

celery_app = Celery(
    "talent_iq",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
)


def run_async(coro):
    """Run an async coroutine in a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, name="tasks.parse_resume_task")
def parse_resume_task(self, raw_text: str, job_id: str, recruiter_id: str, source_filename: str = None):
    """Background task for parsing a single resume."""
    from app.database import AsyncSessionLocal
    from app.services.pipeline import process_resume

    async def _run():
        async with AsyncSessionLocal() as db:
            return await process_resume(
                db,
                raw_text,
                uuid.UUID(job_id),
                uuid.UUID(recruiter_id),
                source_filename,
            )

    try:
        return run_async(_run())
    except Exception as exc:
        self.retry(exc=exc, countdown=10, max_retries=2)


@celery_app.task(bind=True, name="tasks.bulk_parse_task")
def bulk_parse_task(self, texts: list, job_id: str, recruiter_id: str):
    """Process multiple resumes in bulk."""
    results = []
    for i, text in enumerate(texts):
        result = parse_resume_task.delay(text, job_id, recruiter_id, f"bulk_{i+1}.txt")
        results.append(result.id)
    return {"task_ids": results, "count": len(results)}
