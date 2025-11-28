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

    Base.metadata.create_all(bind=engine)
    yield
    # Optionally tear down: drop all tables if the DB is file-based
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception:
        pass
