#!/usr/bin/env python3
"""
Script d'installation des dépendances pour les tests de charge
"""

import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def install_package(package_name: str, description: str = "") -> bool:
    """Installe un package pip"""
    try:
        logger.info(f"📦 Installation de {package_name}... {description}")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", package_name
        ])
        logger.info(f"✅ {package_name} installé avec succès")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Échec de l'installation de {package_name}: {e}")
        return False


def main() -> int:
    """Installation des dépendances de test de charge"""
    logger.info("🚀 Installation des dépendances pour tests de charge")

    packages = [
        ("locust", "pour les tests de charge"),
        ("requests", "pour les appels HTTP"),
        ("matplotlib", "pour graphiques (optionnel)"),
        ("pandas", "pour analyse données (optionnel)"),
    ]

    success_count = 0

    for package, description in packages:
        if install_package(package, description):
            success_count += 1

    logger.info(f"📊 {success_count}/{len(packages)} packages installés")

    if success_count == len(packages):
        logger.info("🎉 Toutes les dépendances sont installées!")
        logger.info("\nPour lancer les tests de charge:")
        logger.info("  python run_load_test.py")
        return 0
    else:
        logger.error("❌ Certaines dépendances n'ont pas pu être installées")
        return 1


if __name__ == "__main__":
    sys.exit(main())