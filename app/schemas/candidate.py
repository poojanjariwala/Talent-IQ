import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class SkillEntry(BaseModel):
    raw: str
    canonical: Optional[str] = None
    status: str = "explicit"  # explicit, normalized, inferred, ambiguous, review_needed
    confidence: float = 1.0


class ScoreBreakdown(BaseModel):
    skill_match: float = 0.0
    experience_match: float = 0.0
    education_match: float = 0.0
    project_match: float = 0.0
    total: float = 0.0


class AuditEntryOut(BaseModel):
    id: uuid.UUID
    step: str
    status: str
    message: Optional[str] = None
    detail: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CandidateOut(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    recruiter_id: uuid.UUID
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    total_experience_years: Optional[float] = None
    education: List[Dict[str, Any]] = []
    work_experience: List[Dict[str, Any]] = []
    certifications: List[str] = []
    projects: List[Dict[str, Any]] = []
    languages: List[str] = []
    raw_skills: List[str] = []
    normalized_skills: List[str] = []
    inferred_skills: List[str] = []
    ambiguous_skills: List[str] = []
    match_score: Optional[float] = None
    missing_skills: List[str] = []
    matched_skills: List[str] = []
    score_breakdown: Optional[Dict[str, float]] = None
    bucket: str = "new"
    stage: str = "applied"
    notes: Optional[str] = None
    email_sent: bool = False
    email_sent_at: Optional[datetime] = None
    interview_scheduled_at: Optional[datetime] = None
    interview_calendar_link: Optional[str] = None
    raw_resume_text: Optional[str] = None
    source_filename: Optional[str] = None
    resume_mime: Optional[str] = None
    parse_status: str = "pending"
    parse_error: Optional[str] = None
    created_at: datetime
    audit_entries: List[AuditEntryOut] = []

    class Config:
        from_attributes = True


class CandidateUpdate(BaseModel):
    bucket: Optional[str] = None
    stage: Optional[str] = None
    notes: Optional[str] = None
    email_sent: Optional[bool] = None
    interview_scheduled_at: Optional[datetime] = None
    interview_calendar_link: Optional[str] = None


class BulkUploadRequest(BaseModel):
    job_id: uuid.UUID
    resumes: List[str]  # list of raw resume texts


class ParseJobStatus(BaseModel):
    task_id: str
    status: str  # pending, processing, done, failed
    result: Optional[Any] = None
    error: Optional[str] = None
