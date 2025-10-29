#!/usr/bin/env python3
"""
Script simple pour démarrer l'API TwisterLab
"""

import uvicorn
import logging
import sys
from pathlib import Path

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    from agents.api.main import app
    print("🚀 Démarrage de TwisterLab API...")
    print(f"📊 {len(app.routes)} routes chargées")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        access_log=True,
        reload=False
    )