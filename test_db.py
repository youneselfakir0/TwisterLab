import asyncio
import sys

sys.path.insert(0, ".")
from sqlalchemy import text

from agents.database.config import get_db


async def test_db():
    try:
        async for session in get_db():
            result = await session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ Connexion DB réussie: {row[0]}")
            break
    except Exception as e:
        print(f"❌ Erreur DB: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_db())
