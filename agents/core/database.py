"""
TwisterLab Database Access Layer
Async PostgreSQL connection management using asyncpg driver
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from agents.core.models import Base
import os
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# Database URL with asyncpg driver (required for async operations)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://twisterlab:your_secure_password@192.168.0.30:5432/twisterlab"
)

# Override with specific components if provided
DB_USER = os.getenv("POSTGRES_USER", "twisterlab")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "your_secure_password")
DB_HOST = os.getenv("POSTGRES_HOST", "192.168.0.30")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "twisterlab")

# Construct URL if individual components provided
if all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

logger.info(f"Database URL configured: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging (development only)
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,  # Max concurrent connections
    max_overflow=20,  # Additional connections when pool exhausted
)

# Async session factory
AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.
    
    Usage:
        async with get_session() as session:
            # perform database operations
            pass
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    
    Creates all tables defined in models.py if they don't exist.
    Safe to call multiple times (idempotent).
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def close_db() -> None:
    """
    Close database connection pool.
    
    Call this during application shutdown to gracefully close connections.
    """
    try:
        await engine.dispose()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}")


# FastAPI dependency for route handlers
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for injecting database sessions.
    
    Usage in route:
        @app.post("/tickets")
        async def create_ticket(session: AsyncSession = Depends(get_db_session)):
            # session available here
            pass
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Database transaction error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
