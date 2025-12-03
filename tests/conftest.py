import sys
from pathlib import Path

import pytest

# Ensure the 'src' directory is on sys.path so tests can import the package 'twisterlab'
ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


@pytest.fixture(scope="session", autouse=True)
def ensure_db_tables():
    # Import the session & models and create tables to ensure a consistent test DB
    from twisterlab.database.session import Base, engine
    # engine may be an AsyncEngine; handle both sync and async engines
    try:
        from sqlalchemy.ext.asyncio import AsyncEngine
        import asyncio

        if isinstance(engine, AsyncEngine):
            async def _create_all():
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
            asyncio.get_event_loop().run_until_complete(_create_all())
        else:
            Base.metadata.create_all(bind=engine)
    except Exception:
        # Fallback to synchronous create_all when detection fails
        Base.metadata.create_all(bind=engine)
    yield
    # Optionally tear down: drop all tables if the DB is file-based
    try:
        from sqlalchemy.ext.asyncio import AsyncEngine
        import asyncio

        if isinstance(engine, AsyncEngine):
            async def _drop_all():
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.drop_all)
            asyncio.get_event_loop().run_until_complete(_drop_all())
        else:
            Base.metadata.drop_all(bind=engine)
    except Exception:
        pass
