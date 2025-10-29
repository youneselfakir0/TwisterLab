#!/usr/bin/env python3
"""
Script de démarrage de l'API TwisterLab avec gestion d'erreurs détaillée
"""

import asyncio
import sys
import traceback
import logging
import os
from pathlib import Path

# Configuration du logging détaillé
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

logger = logging.getLogger(__name__)

async def test_database():
    """Test de connexion à la base de données"""
    try:
        logger.info("�️ Test de connexion à la base de données...")
        from agents.database.config import get_db
        from sqlalchemy import text

        async for session in get_db():
            result = await session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            logger.info(f"✅ Base de données OK: {row[0]}")
            break
        return True
    except Exception as e:
        logger.error(f"❌ Erreur base de données: {e}")
        traceback.print_exc()
        return False

def main():
    """Fonction principale avec gestion d'erreurs"""
    try:
        logger.info("🚀 Démarrage de TwisterLab API avec diagnostic détaillé...")

        # Import de l'application
        logger.info("📦 Import de l'application...")
        from agents.api.main import app
        logger.info(f"✅ Application importée: {len(app.routes)} routes")

        # Test de la base de données
        if not asyncio.run(test_database()):
            logger.error("❌ Échec du test de base de données - arrêt")
            return

        # Démarrage du serveur
        logger.info("🌐 Démarrage du serveur uvicorn...")
        import uvicorn

        # Utiliser uvicorn.run() au lieu de Server() pour éviter les conflits d'event loop
        logger.info("✅ Démarrage du serveur avec uvicorn.run()...")
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            access_log=True,
            reload=False
        )

    except KeyboardInterrupt:
        logger.info("🛑 Interruption par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        logger.error("📋 Traceback complet:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()