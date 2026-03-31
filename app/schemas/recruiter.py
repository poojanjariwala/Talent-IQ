import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class RecruiterCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    title: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_industry: Optional[str] = None
    company_size: Optional[str] = None
    company_description: Optional[str] = None


class RecruiterUpdate(BaseModel):
    full_name: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_industry: Optional[str] = None
    company_size: Optional[str] = None
    company_description: Optional[str] = None


class RecruiterOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    title: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_industry: Optional[str] = None
    company_size: Optional[str] = None
    company_description: Optional[str] = None
    is_active: bool
    is_demo: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    recruiter: RecruiterOut
