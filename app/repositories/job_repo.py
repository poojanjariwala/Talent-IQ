import uuid
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.job import Job
from app.models.candidate import Candidate
from app.schemas.job import JobCreate, JobUpdate


class JobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, job_id: uuid.UUID) -> Optional[Job]:
        result = await self.db.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()

    async def list_by_recruiter(self, recruiter_id: uuid.UUID) -> List[Job]:
        result = await self.db.execute(
            select(Job).where(Job.recruiter_id == recruiter_id).order_by(Job.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, recruiter_id: uuid.UUID, data: JobCreate) -> Job:
        job = Job(
            recruiter_id=recruiter_id,
            **data.model_dump()
        )
        self.db.add(job)
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def update(self, job: Job, data: JobUpdate) -> Job:
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(job, field, value)
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def delete(self, job: Job) -> None:
        await self.db.delete(job)
        await self.db.flush()

    async def get_candidate_count(self, job_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count()).where(Candidate.job_id == job_id)
        )
        return result.scalar_one() or 0
