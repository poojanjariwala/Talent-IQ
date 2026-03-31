import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.candidate import CandidateOut, CandidateUpdate, ParseJobStatus
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.job_repo import JobRepository
from app.services.file_extractor import extract_text, clean_text
from app.services.pipeline import process_resume
from app.routers.auth import get_current_recruiter

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/job/{job_id}", response_model=List[CandidateOut])
async def list_candidates(
    job_id: uuid.UUID,
    recruiter=Depends(get_current_recruiter),
    db: AsyncSession = Depends(get_db),
):
    # Verify job ownership
    from app.repositories.job_repo import JobRepository
    job_repo = JobRepository(db)
    job = await job_repo.get_by_id(job_id)
    if not job or job.recruiter_id != recruiter.id:
        raise HTTPException(status_code=404, detail="Job not found")
    repo = CandidateRepository(db)
    candidates = await repo.list_by_job(job_id, with_audit=True)
    return [CandidateOut.model_validate(c) for c in candidates]


@router.get("/{candidate_id}", response_model=CandidateOut)
async def get_candidate(
    candidate_id: uuid.UUID,
    recruiter=Depends(get_current_recruiter),
    db: AsyncSession = Depends(get_db),
):
    repo = CandidateRepository(db)
    candidate = await repo.get_by_id(candidate_id, with_audit=True)
    if not candidate or candidate.recruiter_id != recruiter.id:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return CandidateOut.model_validate(candidate)


@router.post("/upload", status_code=202)
async def upload_resumes(
    job_id: uuid.UUID = Form(...),
    files: List[UploadFile] = File(...),
    recruiter=Depends(get_current_recruiter),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """Upload one or more resume files for a given job."""
    job_repo = JobRepository(db)
    job = await job_repo.get_by_id(job_id)
    if not job or job.recruiter_id != recruiter.id:
        raise HTTPException(status_code=404, detail="Job not found")

    results = []
    for f in files:
        try:
            content = await f.read()
            raw_text = clean_text(extract_text(f.filename, content))
            result = await process_resume(
                db, 
                raw_text, 
                job_id, 
                recruiter.id, 
                f.filename,
                resume_bytes=content,
                resume_mime=f.content_type
            )
            results.append({"filename": f.filename, **result})
        except Exception as e:
            results.append({"filename": f.filename, "status": "failed", "error": str(e)})

    return {"processed": len(results), "results": results}


@router.get("/{candidate_id}/download")
async def download_resume(
    candidate_id: uuid.UUID,
    recruiter=Depends(get_current_recruiter),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories.candidate_repo import CandidateRepository
    repo = CandidateRepository(db)
    candidate = await repo.get_by_id(candidate_id)
    if not candidate or candidate.recruiter_id != recruiter.id:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if not candidate.resume_bytes:
        raise HTTPException(status_code=404, detail="Original resume not found")
    
    from fastapi import Response
    return Response(
        content=candidate.resume_bytes,
        media_type=candidate.resume_mime or "application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={candidate.source_filename or 'resume'}"
        }
    )


@router.post("/paste", status_code=202)
async def paste_resumes(
    job_id: uuid.UUID,
    texts: List[str],
    recruiter=Depends(get_current_recruiter),
    db: AsyncSession = Depends(get_db),
):
    """Accept pasted resume texts for processing."""
    job_repo = JobRepository(db)
    job = await job_repo.get_by_id(job_id)
    if not job or job.recruiter_id != recruiter.id:
        raise HTTPException(status_code=404, detail="Job not found")

    results = []
    for i, text in enumerate(texts):
        try:
            raw_text = clean_text(text)
            result = await process_resume(db, raw_text, job_id, recruiter.id, f"paste_{i+1}.txt")
            results.append(result)
        except Exception as e:
            results.append({"status": "failed", "error": str(e)})
    return {"processed": len(results), "results": results}


@router.put("/{candidate_id}", response_model=CandidateOut)
async def update_candidate(
    candidate_id: uuid.UUID,
    data: CandidateUpdate,
    recruiter=Depends(get_current_recruiter),
    db: AsyncSession = Depends(get_db),
):
    repo = CandidateRepository(db)
    candidate = await repo.get_by_id(candidate_id, with_audit=True)
    if not candidate or candidate.recruiter_id != recruiter.id:
        raise HTTPException(status_code=404, detail="Candidate not found")
    updated = await repo.update(candidate, data)
    return CandidateOut.model_validate(updated)


@router.delete("/{candidate_id}", status_code=204)
async def delete_candidate(
    candidate_id: uuid.UUID,
    recruiter=Depends(get_current_recruiter),
    db: AsyncSession = Depends(get_db),
):
    repo = CandidateRepository(db)
    candidate = await repo.get_by_id(candidate_id)
    if not candidate or candidate.recruiter_id != recruiter.id:
        raise HTTPException(status_code=404, detail="Candidate not found")
    await repo.delete(candidate)
