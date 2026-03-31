import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.recruiter import RecruiterCreate, RecruiterOut, LoginRequest, TokenResponse, RecruiterUpdate
from app.repositories.recruiter_repo import RecruiterRepository
from app.services.auth_service import hash_password, verify_password, create_access_token, decode_access_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_recruiter(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    recruiter_id = decode_access_token(token)
    if not recruiter_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    repo = RecruiterRepository(db)
    recruiter = await repo.get_by_id(uuid.UUID(recruiter_id))
    if not recruiter or not recruiter.is_active:
        raise HTTPException(status_code=401, detail="Recruiter not found or inactive")
    return recruiter


@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(data: RecruiterCreate, db: AsyncSession = Depends(get_db)):
    repo = RecruiterRepository(db)
    existing = await repo.get_by_email(data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(data.password)
    recruiter = await repo.create(data, hashed)
    token = create_access_token(recruiter.id)
    return TokenResponse(access_token=token, recruiter=RecruiterOut.model_validate(recruiter))


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    repo = RecruiterRepository(db)
    recruiter = await repo.get_by_email(data.email)
    if not recruiter or not verify_password(data.password, recruiter.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(recruiter.id)
    return TokenResponse(access_token=token, recruiter=RecruiterOut.model_validate(recruiter))


@router.post("/demo", response_model=TokenResponse)
async def demo_login(db: AsyncSession = Depends(get_db)):
    """Log in as the demo user (creates one if not exists)."""
    repo = RecruiterRepository(db)
    recruiter = await repo.get_by_email("demo@talentiq.ai")
    if not recruiter:
        recruiter = await repo.create_demo()
    token = create_access_token(recruiter.id)
    return TokenResponse(access_token=token, recruiter=RecruiterOut.model_validate(recruiter))


@router.get("/me", response_model=RecruiterOut)
async def get_me(recruiter=Depends(get_current_recruiter)):
    return RecruiterOut.model_validate(recruiter)


@router.put("/me", response_model=RecruiterOut)
async def update_me(
    data: RecruiterUpdate,
    recruiter=Depends(get_current_recruiter),
    db: AsyncSession = Depends(get_db),
):
    repo = RecruiterRepository(db)
    updated = await repo.update(recruiter, data)
    return RecruiterOut.model_validate(updated)
