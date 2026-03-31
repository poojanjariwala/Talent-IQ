from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_tables
from app.routers import auth, jobs, candidates, export
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(jobs.router)
    app.include_router(candidates.router)
    app.include_router(export.router)

    @app.get("/health")
    async def health():
        return {"status": "ok", "version": settings.APP_VERSION}

    @app.get("/config")
    async def get_config():
        return {
            "enable_gemini": settings.ENABLE_GEMINI,
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION
        }

    return app


app = create_app()
