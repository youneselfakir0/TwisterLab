#!/usr/bin/env python3
"""
Script de diagnostic pour TwisterLab API
Teste chaque composant pour identifier les erreurs
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

async def test_database():
    """Test de connexion à la base de données"""
    print("🔍 Test de la base de données...")
    try:
        from agents.database.config import get_db
        from sqlalchemy import text
        async for session in get_db():
            result = await session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ Base de données OK: {row[0]}")
            break
    except Exception as e:
        print(f"❌ Erreur base de données: {e}")
        traceback.print_exc()
        return False
    return True

def test_imports():
    """Test des imports principaux"""
    print("🔍 Test des imports...")
    try:
        from agents.api.main import app
        print(f"✅ Import API OK: {len(app.routes)} routes")
        return True
    except Exception as e:
        print(f"❌ Erreur import API: {e}")
        traceback.print_exc()
        return False

async def test_startup_events():
    """Test des événements de démarrage"""
    print("🔍 Test des événements de démarrage...")
    try:
        from agents.api.main import app
        # Simuler les startup events
        for event in app.router.on_startup:
            if asyncio.iscoroutinefunction(event):
                await event()
            else:
                event()
        print("✅ Événements de démarrage OK")
        return True
    except Exception as e:
        print(f"❌ Erreur événements de démarrage: {e}")
        traceback.print_exc()
        return False

async def main():
    """Fonction principale de diagnostic"""
    print("🚀 Diagnostic TwisterLab API")
    print("=" * 50)

    # Test 1: Imports
    if not test_imports():
        print("❌ Arrêt du diagnostic - problème d'import")
        return

    # Test 2: Base de données
    if not await test_database():
        print("❌ Arrêt du diagnostic - problème de base de données")
        return

    # Test 3: Événements de démarrage
    if not await test_startup_events():
        print("❌ Arrêt du diagnostic - problème d'initialisation")
        return

    print("✅ Tous les tests de diagnostic réussis!")
    print("\n🔧 L'API devrait pouvoir démarrer normalement.")
    print("💡 Si elle s'arrête toujours, vérifiez les logs détaillés.")

if __name__ == "__main__":
    asyncio.run(main())