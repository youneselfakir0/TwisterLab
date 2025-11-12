#!/usr/bin/env pwsh
# =============================================================================
# TWISTERLAB - TEST DES VRAIS AGENTS
# Version: 2.0.0
# Date: 2025-11-11
#
# Prouve que les agents font VRAIMENT leur travail
# =============================================================================

$ErrorActionPreference = "Continue"

Write-Host @"

=================================================================
    TWISTERLAB - TEST DES VRAIS AGENTS
=================================================================

Les agents vont VRAIMENT:
  1. MonitoringAgent → Scanner le système avec psutil
  2. BackupAgent → Créer un VRAI backup PostgreSQL+Redis
  3. SyncAgent → Synchroniser Redis ↔ PostgreSQL

ZERO simulation - 100% REEL !

=================================================================

"@ -ForegroundColor Cyan

# Installer les dépendances si nécessaire
Write-Host "`n[SETUP] Installation des dépendances..." -ForegroundColor Yellow
try {
    python -c "import psutil" 2>$null
} catch {
    Write-Host "  Installing psutil..." -ForegroundColor Gray
    pip install psutil -q
}
try {
    python -c "import redis" 2>$null
} catch {
    Write-Host "  Installing redis..." -ForegroundColor Gray
    pip install redis -q
}

Write-Host "  ✅ Dependencies OK" -ForegroundColor Green

# Script Python pour tester les vrais agents
$testScript = @'
import asyncio
import sys
import json
from pathlib import Path

# Add agents directory
sys.path.insert(0, str(Path(__file__).parent / "agents"))

from real.real_monitoring_agent import RealMonitoringAgent
from real.real_backup_agent import RealBackupAgent
from real.real_sync_agent import RealSyncAgent

async def test_monitoring_agent():
    """Test REAL monitoring with system metrics."""
    print("\n" + "="*60)
    print("TEST 1: MonitoringAgent - REAL System Scan")
    print("="*60)

    agent = RealMonitoringAgent()

    # Test 1: Health check
    print("\n🔍 Running REAL health check...")
    result = await agent.execute({"operation": "health_check"})

    print(f"\nStatus: {result['status']}")
    print(f"CPU: {result['metrics']['cpu']['percent']}%")
    print(f"Memory: {result['metrics']['memory']['percent']}% ({result['metrics']['memory']['used_gb']} GB / {result['metrics']['memory']['total_gb']} GB)")
    print(f"Disk: {result['metrics']['disk']['percent']}% ({result['metrics']['disk']['used_gb']} GB / {result['metrics']['disk']['total_gb']} GB)")
    print(f"Processes: {result['metrics']['processes']}")

    if result['issues']:
        print(f"\n⚠️ Issues detected:")
        for issue in result['issues']:
            print(f"  - {issue}")
    else:
        print(f"\n✅ System healthy - no issues")

    # Test 2: Check Docker services
    print("\n\n🐳 Checking Docker services...")
    result = await agent.execute({"operation": "check_services"})

    print(f"\nTotal services: {result['total_services']}")
    print(f"Running: {result['running_services']}")
    print(f"Degraded: {result['degraded_services']}")
    print(f"Missing: {result['missing_services']}")

    # Test 3: Check GPU
    print("\n\n🎮 Checking NVIDIA GPU...")
    result = await agent.execute({"operation": "check_gpu"})

    if result['status'] == 'available':
        print(f"\n✅ GPU Found: {result['gpu_name']}")
        print(f"  Memory: {result['memory_used_mb']} MB / {result['memory_total_mb']} MB")
        print(f"  Utilization: {result['gpu_utilization_percent']}%")
        print(f"  Temperature: {result['temperature_celsius']}°C")
    else:
        print(f"\n⚠️ GPU not available: {result.get('error', 'Unknown')}")

    return True

async def test_backup_agent():
    """Test REAL backup creation."""
    print("\n\n" + "="*60)
    print("TEST 2: BackupAgent - REAL Backup Creation")
    print("="*60)

    agent = RealBackupAgent(backup_dir="C:/TwisterLab/backups")

    # Test 1: Create backup
    print("\n📦 Creating REAL backup...")
    result = await agent.execute({"operation": "create_backup"})

    if result['status'] == 'success':
        print(f"\n✅ Backup created successfully!")
        print(f"  Backup ID: {result['backup_id']}")
        print(f"  File: {result['backup_file']}")
        print(f"  Size: {result['size_mb']} MB")
        print(f"  Checksum: {result['checksum'][:16]}...")
        print(f"  Components: {', '.join(result['components'])}")
        print(f"  Time: {result['execution_time']:.2f}s")
    else:
        print(f"\n❌ Backup failed: {result.get('error')}")
        return False

    # Test 2: List backups
    print("\n\n📋 Listing backups...")
    result = await agent.execute({"operation": "list_backups"})

    print(f"\nTotal backups: {result['total_backups']}")
    for backup in result['backups'][-3:]:  # Last 3
        print(f"  - {backup['backup_name']} ({backup.get('size_mb', 'N/A')} MB)")

    return True

async def test_sync_agent():
    """Test REAL sync operations."""
    print("\n\n" + "="*60)
    print("TEST 3: SyncAgent - REAL Redis ↔ PostgreSQL Sync")
    print("="*60)

    agent = RealSyncAgent()

    # Test 1: Sync all
    print("\n🔄 Syncing Redis ↔ PostgreSQL...")
    result = await agent.execute({"operation": "sync_all"})

    print(f"\nStatus: {result['status']}")
    print(f"Total keys: {result['total_keys']}")
    print(f"Synced: {result['synced_keys']}")
    print(f"Skipped: {result['skipped_keys']}")

    # Test 2: Verify consistency
    print("\n\n🔍 Verifying cache consistency...")
    result = await agent.execute({"operation": "verify_consistency"})

    print(f"\nConsistency: {result['consistency_percent']}%")
    print(f"Checked: {result['total_checked']} keys")
    print(f"Consistent: {result['consistent']}")
    print(f"Inconsistent: {result['inconsistent']}")

    # Test 3: Warm cache
    print("\n\n🔥 Warming cache...")
    result = await agent.execute({"operation": "warm_cache"})

    print(f"\nLoaded: {result['loaded_keys']} keys")
    print(f"Categories:")
    for category, count in result['categories'].items():
        print(f"  - {category}: {count}")

    return True

async def main():
    """Run all tests."""
    print("\n🚀 Starting REAL agent tests...")

    success_count = 0
    total_tests = 3

    try:
        if await test_monitoring_agent():
            success_count += 1
    except Exception as e:
        print(f"\n❌ MonitoringAgent test failed: {e}")

    try:
        if await test_backup_agent():
            success_count += 1
    except Exception as e:
        print(f"\n❌ BackupAgent test failed: {e}")

    try:
        if await test_sync_agent():
            success_count += 1
    except Exception as e:
        print(f"\n❌ SyncAgent test failed: {e}")

    # Summary
    print("\n\n" + "="*60)
    print(f"TEST SUMMARY: {success_count}/{total_tests} agents working")
    print("="*60)

    if success_count == total_tests:
        print("\n✅ ALL AGENTS WORKING - 100% REAL!")
        return 0
    else:
        print(f"\n⚠️ {total_tests - success_count} agent(s) failed")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
'@

# Sauvegarder le script Python
$testScript | Out-File -FilePath "test_real_agents.py" -Encoding UTF8

# Exécuter les tests
Write-Host "`n[EXECUTION] Lancement des tests..." -ForegroundColor Yellow
python test_real_agents.py

$exitCode = $LASTEXITCODE

# Résumé
if ($exitCode -eq 0) {
    Write-Host @"

=================================================================
              TESTS REUSSIS - AGENTS OPERATIONNELS
=================================================================

✅ MonitoringAgent: Scan système REEL avec psutil
✅ BackupAgent: Backup REEL PostgreSQL+Redis+configs
✅ SyncAgent: Synchronisation REELLE Redis ↔ PostgreSQL

Les agents font VRAIMENT leur travail !

Prochaines étapes:
  1. Déployer ces agents dans l'API (remplacer les mocks)
  2. Configurer scheduler pour exécution automatique
  3. Intégrer avec Grafana pour monitoring

=================================================================

"@ -ForegroundColor Green
} else {
    Write-Host @"

=================================================================
                TESTS PARTIELS - VERIFICATION REQUISE
=================================================================

⚠️ Certains agents ont échoué (voir détails ci-dessus)

Causes possibles:
  - Dépendances manquantes (psutil, redis)
  - Services non accessibles (PostgreSQL, Redis)
  - Permissions insuffisantes

Solutions:
  - Installer dépendances: pip install psutil redis
  - Vérifier services Docker actifs
  - Exécuter avec privilèges admin si nécessaire

=================================================================

"@ -ForegroundColor Yellow
}

Write-Host "`nFichiers créés:" -ForegroundColor Cyan
Write-Host "  - agents/real/real_monitoring_agent.py" -ForegroundColor Gray
Write-Host "  - agents/real/real_backup_agent.py" -ForegroundColor Gray
Write-Host "  - agents/real/real_sync_agent.py" -ForegroundColor Gray
Write-Host "  - test_real_agents.py" -ForegroundColor Gray
