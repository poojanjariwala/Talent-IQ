import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class JobCreate(BaseModel):
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_min_years: Optional[int] = None
    experience_max_years: Optional[int] = None
    description: Optional[str] = None
    required_skills: List[str] = []
    nice_to_have_skills: List[str] = []
    tech_stack: List[str] = []
    required_projects: List[str] = []
    communication_expectations: Optional[str] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_min_years: Optional[int] = None
    experience_max_years: Optional[int] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    nice_to_have_skills: Optional[List[str]] = None
    tech_stack: Optional[List[str]] = None
    required_projects: Optional[List[str]] = None
    communication_expectations: Optional[str] = None
    status: Optional[str] = None


class JobOut(BaseModel):
    id: uuid.UUID
    recruiter_id: uuid.UUID
    title: str
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_min_years: Optional[int] = None
    experience_max_years: Optional[int] = None
    description: Optional[str] = None
    required_skills: List[str] = []
    nice_to_have_skills: List[str] = []
    tech_stack: List[str] = []
    required_projects: List[str] = []
    communication_expectations: Optional[str] = None
    status: str
    created_at: datetime
    candidate_count: Optional[int] = 0

    class Config:
        from_attributes = True
