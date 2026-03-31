import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.recruiter import Recruiter
from app.schemas.recruiter import RecruiterCreate, RecruiterUpdate


class RecruiterRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, recruiter_id: uuid.UUID) -> Optional[Recruiter]:
        result = await self.db.execute(select(Recruiter).where(Recruiter.id == recruiter_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Recruiter]:
        result = await self.db.execute(select(Recruiter).where(Recruiter.email == email))
        return result.scalar_one_or_none()

    async def create(self, data: RecruiterCreate, hashed_password: str) -> Recruiter:
        recruiter = Recruiter(
            email=data.email,
            hashed_password=hashed_password,
            full_name=data.full_name,
            title=data.title,
            phone=data.phone,
            company_name=data.company_name,
            company_website=data.company_website,
            company_industry=data.company_industry,
            company_size=data.company_size,
            company_description=data.company_description,
        )
        self.db.add(recruiter)
        await self.db.flush()
        await self.db.refresh(recruiter)
        return recruiter

    async def update(self, recruiter: Recruiter, data: RecruiterUpdate) -> Recruiter:
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(recruiter, field, value)
        await self.db.flush()
        await self.db.refresh(recruiter)
        return recruiter

    async def create_demo(self) -> Recruiter:
        recruiter = Recruiter(
            email="demo@talentiq.ai",
            hashed_password="pbkdf2_sha256$260000$demo_dummy_salt$demo_dummy_hash",
            full_name="Demo Recruiter",
            title="Senior Talent Acquisition",
            company_name="TalentIQ Demo Corp",
            company_industry="Technology",
            company_size="51-200",
            is_demo=True,
        )
        self.db.add(recruiter)
        await self.db.flush()
        await self.db.refresh(recruiter)
        return recruiter
