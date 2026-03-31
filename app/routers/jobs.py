import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.job import JobCreate, JobUpdate, JobOut
from app.repositories.job_repo import JobRepository
from app.routers.auth import get_current_recruiter

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=List[JobOut])
async def list_jobs(
    recruiter=Depends(get_current_recruiter),
    db: AsyncSession = Depends(get_db),
):
    repo = JobRepository(db)
    jobs = await repo.list_by_recruiter(recruiter.id)
    result = []
    for job in jobs:
        count = await repo.get_candidate_count(job.id)
        job_out = JobOut.model_validate(job)
        job_out.candidate_count = count
        result.append(job_out)
    return result


@router.post("/", response_model=JobOut, status_code=201)
async def create_job(
    data: JobCreate,
    recruiter=Depends(get_current_recruiter),
    db: AsyncSession = Depends(get_db),
):
    repo = JobRepository(db)
    job = await repo.create(recruiter.id, data)
    return JobOut.model_validate(job)


@router.get("/{job_id}", response_model=JobOut)
async def get_job(
    job_id: uuid.UUID,
    recruiter=Depends(get_current_recruiter),
    db: AsyncSession = Depends(get_db),
):
    repo = JobRepository(db)
    job = await repo.get_by_id(job_id)
    if not job or job.recruiter_id != recruiter.id:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobOut.model_validate(job)


@router.put("/{job_id}", response_model=JobOut)
async def update_job(
    job_id: uuid.UUID,
    data: JobUpdate,
    recruiter=Depends(get_current_recruiter),
    db: AsyncSession = Depends(get_db),
):
    repo = JobRepository(db)
    job = await repo.get_by_id(job_id)
    if not job or job.recruiter_id != recruiter.id:
        raise HTTPException(status_code=404, detail="Job not found")
    updated = await repo.update(job, data)
    return JobOut.model_validate(updated)


@router.delete("/{job_id}", status_code=204)
async def delete_job(
    job_id: uuid.UUID,
    recruiter=Depends(get_current_recruiter),
    db: AsyncSession = Depends(get_db),
):
    repo = JobRepository(db)
    job = await repo.get_by_id(job_id)
    if not job or job.recruiter_id != recruiter.id:
        raise HTTPException(status_code=404, detail="Job not found")
    await repo.delete(job)
