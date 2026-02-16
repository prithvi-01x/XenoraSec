# app/db/database.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Determine if using SQLite or Postgres
IS_SQLITE = settings.DATABASE_URL.startswith("sqlite")

# Engine configuration
engine_kwargs = {
    "echo": settings.DB_ECHO,
    "future": True,
}

# SQLite-specific configuration
if IS_SQLITE:
    engine_kwargs.update({
        "connect_args": {"check_same_thread": False},
        "poolclass": NullPool,  # SQLite doesn't benefit from pooling
    })
else:
    # Postgres/other DB configuration
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "poolclass": QueuePool,
        "pool_pre_ping": True,  # Verify connections before using
    })

# Create async engine
engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Base model for all tables
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    FastAPI dependency to get database session.
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    Called on application startup.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db() -> None:
    """
    Close database connections.
    Called on application shutdown.
    """
    await engine.dispose()
    logger.info("Database connections closed")