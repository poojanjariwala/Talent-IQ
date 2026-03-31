import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    recruiter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recruiters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    employment_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    experience_min_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    experience_max_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # JSON arrays stored as JSONB
    required_skills: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    nice_to_have_skills: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    tech_stack: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    required_projects: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    communication_expectations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recruiter: Mapped["Recruiter"] = relationship("Recruiter", back_populates="jobs")
    candidates: Mapped[list["Candidate"]] = relationship("Candidate", back_populates="job", cascade="all, delete-orphan")
