#!/usr/bin/env python3
"""
Script d'exécution automatique des tests de charge TwisterLab
"""

import subprocess
import sys
import time
import json
import os
from pathlib import Path
import requests
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/load_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LoadTester:
    """Classe pour exécuter et analyser les tests de charge"""

    def __init__(self, api_url="http://127.0.0.1:8000", locustfile="load_test.py"):
        self.api_url = api_url
        self.locustfile = locustfile
        self.results = {}

    def check_api_availability(self):
        """Vérifie que l'API est disponible"""
        logger.info("🔍 Vérification de la disponibilité de l'API...")
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ API disponible")
                return True
            else:
                logger.error(f"❌ API répond avec le code {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Impossible de contacter l'API: {e}")
            return False

    def run_load_test(self, users=10, spawn_rate=2, duration="30s"):
        """Exécute un test de charge avec les paramètres spécifiés"""
        logger.info(f"🚀 Démarrage du test de charge: {users} utilisateurs, {spawn_rate} spawn/s, durée {duration}")

        cmd = [
            sys.executable, "-m", "locust",
            "--locustfile", self.locustfile,
            "--host", self.api_url,
            "--users", str(users),
            "--spawn-rate", str(spawn_rate),
            "--run-time", duration,
            "--headless",  # Mode sans interface graphique
            "--csv", "logs/load_test_results",  # Sauvegarde des résultats
            "--loglevel", "INFO"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # Timeout de 5 minutes
            )

            logger.info("📊 Test de charge terminé")
            logger.info(f"Return code: {result.returncode}")

            if result.stdout:
                logger.info("Output stdout:")
                logger.info(result.stdout)

            if result.stderr:
                logger.warning("Output stderr:")
                logger.warning(result.stderr)

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            logger.error("❌ Test de charge timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur lors du test de charge: {e}")
            return False

    def analyze_results(self):
        """Analyse les résultats du test de charge"""
        logger.info("📈 Analyse des résultats...")

        results_file = Path("logs/load_test_results_stats.csv")
        if results_file.exists():
            logger.info("✅ Fichier de résultats trouvé")
            # Ici on pourrait analyser le CSV pour des métriques détaillées
            return True
        else:
            logger.warning("⚠️ Fichier de résultats non trouvé")
            return False

    def run_comprehensive_test(self):
        """Exécute une batterie complète de tests"""
        logger.info("🧪 Démarrage de la batterie de tests complète")

        if not self.check_api_availability():
            logger.error("❌ API non disponible - arrêt des tests")
            return False

        test_scenarios = [
            {"users": 5, "spawn_rate": 1, "duration": "20s", "name": "Test léger"},
            {"users": 20, "spawn_rate": 2, "duration": "30s", "name": "Test moyen"},
            {"users": 50, "spawn_rate": 5, "duration": "45s", "name": "Test intensif"},
        ]

        all_passed = True

        for scenario in test_scenarios:
            logger.info(f"🎯 Exécution du scénario: {scenario['name']}")

            success = self.run_load_test(
                users=scenario["users"],
                spawn_rate=scenario["spawn_rate"],
                duration=scenario["duration"]
            )

            if success:
                logger.info(f"✅ Scénario {scenario['name']} réussi")
            else:
                logger.error(f"❌ Scénario {scenario['name']} échoué")
                all_passed = False

            # Pause entre les tests
            time.sleep(5)

        # Analyse finale
        self.analyze_results()

        if all_passed:
            logger.info("🎉 Tous les tests de charge réussis!")
            return True
        else:
            logger.error("❌ Certains tests de charge ont échoué")
            return False

def main():
    """Fonction principale"""
    # Créer le dossier logs s'il n'existe pas
    os.makedirs("logs", exist_ok=True)

    # Initialiser le testeur
    tester = LoadTester()

    # Exécuter les tests
    success = tester.run_comprehensive_test()

    # Résumé final
    if success:
        print("\n🎉 VALIDATION LOAD TESTING RÉUSSIE")
        print("✅ L'API TwisterLab supporte la charge attendue")
        return 0
    else:
        print("\n❌ VALIDATION LOAD TESTING ÉCHOUÉE")
        print("⚠️ L'API nécessite des optimisations avant production")
        return 1

if __name__ == "__main__":
    sys.exit(main())