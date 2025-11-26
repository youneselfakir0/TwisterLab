from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

# Default to a shared in-memory SQLite database (safe for tests) unless overridden
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///:memory:")

engine_kwargs: dict = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs.setdefault("connect_args", {})
    engine_kwargs["connect_args"]["check_same_thread"] = False
    # Use StaticPool for in-memory DBs so a single connection is reused and tables persist across sessions
    if DATABASE_URL == "sqlite:///:memory:":
        engine_kwargs["poolclass"] = StaticPool

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Ensure models are imported and tables created at module import time to support test clients
try:
    # Import model modules so they register with Base
    from twisterlab.database.models import agent as _agent_model  # noqa: F401

    Base.metadata.create_all(bind=engine)
except Exception:
    # If import fails during startup or missing files, do not crash import
    pass
