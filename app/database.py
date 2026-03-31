from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    from sqlalchemy import text
    async with engine.begin() as conn:
        # Standard table creation
        await conn.run_sync(Base.metadata.create_all)
        
        # Manual Migrations for existing deployments
        try:
            await conn.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS resume_bytes bytea;"))
            await conn.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS resume_mime varchar(100);"))
            await conn.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS raw_resume_text text;"))
        except Exception:
            # Table might not exist yet or other issue, ignore during metadata creation
            pass
