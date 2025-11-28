import os
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///tests.sqlite3'
from twisterlab.database.session import Base, engine
print('engine type:', type(engine))
print('Base tables:', list(Base.metadata.tables.keys()))
# Import models
import twisterlab.database.models.agent
print('Base tables after import:', list(Base.metadata.tables.keys()))
# Try to create tables
if hasattr(engine, 'begin'):
    import asyncio
    print('engine has begin, creating tables async')
    async def _init():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(_init())
else:
    print('engine sync, creating tables sync')
    Base.metadata.create_all(bind=getattr(engine, 'sync_engine', engine))
print('Done. Tables:', list(Base.metadata.tables.keys()))
