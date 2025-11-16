"""
API TwisterLab simplifiée pour debug
"""

import logging

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("🚀 Création de l'API TwisterLab simplifiée...")

# Créer l'application FastAPI
app = FastAPI(
    title="TwisterLab API (Debug)",
    description="Version simplifiée pour debug",
    version="1.0.0-debug",
)

logger.info("✅ Application FastAPI créée")


@app.get("/")
async def root():
    """Endpoint racine."""
    logger.info("📍 Endpoint root appelé")
    return {"message": "TwisterLab API (Debug)", "status": "running", "version": "1.0.0-debug"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.info("💚 Health check appelé")
    return {
        "status": "healthy",
        "version": "1.0.0-debug",
    }


@app.get("/test-db")
async def test_database():
    """Test de connexion à la base de données."""
    try:
        from sqlalchemy import text

        from agents.database.config import async_session

        async with async_session() as session:
            result = await session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            return {"db_status": "connected", "test_result": row[0]}
    except Exception as e:
        logger.error(f"Erreur DB: {e}")
        return {"db_status": "error", "error": str(e)}


logger.info("✅ Routes enregistrées")
