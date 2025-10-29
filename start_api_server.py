#!/usr/bin/env python3
"""
Script pour démarrer l'API TwisterLab en continu
"""

import time
import signal
import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def signal_handler(signum, frame):
    print("\n🛑 Signal d'arrêt reçu, fermeture...")
    sys.exit(0)

# Gestionnaire de signaux
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

print("🚀 Démarrage de l'API TwisterLab...")

try:
    import uvicorn
    from agents.api.main import app

    print("✅ Application chargée, démarrage du serveur...")
    print("🌐 L'API sera disponible sur http://127.0.0.1:8009")
    print("🛑 Appuyez sur Ctrl+C pour arrêter")

    # Démarrer uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8009,
        log_level="info",
        access_log=True,
        reload=False
    )

except Exception as e:
    print(f"❌ Erreur lors du démarrage: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)