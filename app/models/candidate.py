import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, Float, Integer, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recruiter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("recruiters.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Identity
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Parsed data (JSONB)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_experience_years: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    education: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    work_experience: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    certifications: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    projects: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    languages: Mapped[Optional[list]] = mapped_column(JSON, default=list)

    # Skills
    raw_skills: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    normalized_skills: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    inferred_skills: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    ambiguous_skills: Mapped[Optional[list]] = mapped_column(JSON, default=list)

    # Matching
    match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    missing_skills: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    matched_skills: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    score_breakdown: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    # Workflow
    bucket: Mapped[str] = mapped_column(String(50), default="new")  # new, shortlist, hold, reject
    stage: Mapped[str] = mapped_column(String(100), default="applied")  # applied, screening, interview, offer, hired, rejected
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Email / Interview
    email_sent: Mapped[bool] = mapped_column(default=False)
    email_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    interview_scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    interview_calendar_link: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Source
    raw_resume_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resume_bytes: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    resume_mime: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_filename: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    parse_status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, done, failed
    parse_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="candidates")
    audit_entries: Mapped[list["AuditEntry"]] = relationship("AuditEntry", back_populates="candidate", cascade="all, delete-orphan")
