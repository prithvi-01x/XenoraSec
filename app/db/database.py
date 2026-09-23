# app/db/database.py

from sqlalchemy import event
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

# SQLite-specific configuration with concurrency hardening
if IS_SQLITE:
    engine_kwargs.update({
        "connect_args": {
            "check_same_thread": False,
            "timeout": 30.0,  # 30s connection acquisition timeout to prevent "database is locked"
        },
        "poolclass": NullPool,  # SQLite with aiosqlite works best with fresh connections per task
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

# Concurrency tuning for SQLite: Enable WAL mode, synchronous=NORMAL, and busy timeout
if IS_SQLITE:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA busy_timeout=30000")  # 30,000ms (30s) busy handler
            cursor.close()
        except Exception as e:
            logger.debug(f"Failed to set SQLite concurrency PRAGMAs: {e}")

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


from sqlalchemy import text

async def init_db() -> None:
    """
    Initialize database tables and run automatic migrations.
    Called on application startup.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
            # Lightweight SQLite migration for added columns
            if IS_SQLITE:
                res = await conn.execute(text("PRAGMA table_info(scan_results)"))
                existing_cols = {row[1] for row in res.fetchall()}
                if existing_cols:
                    if "scan_profile" not in existing_cols:
                        await conn.execute(text("ALTER TABLE scan_results ADD COLUMN scan_profile VARCHAR(50) DEFAULT 'quick'"))
                    if "scan_options" not in existing_cols:
                        await conn.execute(text("ALTER TABLE scan_results ADD COLUMN scan_options JSON"))
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