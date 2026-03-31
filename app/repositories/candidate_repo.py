import uuid
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateUpdate


class CandidateRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, candidate_id: uuid.UUID, with_audit: bool = False) -> Optional[Candidate]:
        query = select(Candidate).where(Candidate.id == candidate_id)
        if with_audit:
            query = query.options(selectinload(Candidate.audit_entries))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_by_job(self, job_id: uuid.UUID, with_audit: bool = False) -> List[Candidate]:
        query = select(Candidate).where(Candidate.job_id == job_id).order_by(Candidate.match_score.desc().nullslast())
        if with_audit:
            query = query.options(selectinload(Candidate.audit_entries))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_by_recruiter(self, recruiter_id: uuid.UUID) -> List[Candidate]:
        result = await self.db.execute(
            select(Candidate)
            .where(Candidate.recruiter_id == recruiter_id)
            .order_by(Candidate.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, candidate_data: dict) -> Candidate:
        candidate = Candidate(**candidate_data)
        self.db.add(candidate)
        await self.db.flush()
        await self.db.refresh(candidate)
        return candidate

    async def update(self, candidate: Candidate, data: CandidateUpdate) -> Candidate:
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(candidate, field, value)
        await self.db.flush()
        await self.db.refresh(candidate)
        return candidate

    async def update_parsed_data(self, candidate: Candidate, parsed: dict) -> Candidate:
        # Securely update only valid model columns
        allowed_keys = {c.key for c in Candidate.__table__.columns}
        for field, value in parsed.items():
            if field in allowed_keys and value is not None:
                setattr(candidate, field, value)
        
        await self.db.flush()
        await self.db.refresh(candidate)
        return candidate

    async def delete(self, candidate: Candidate) -> None:
        await self.db.delete(candidate)
        await self.db.flush()
