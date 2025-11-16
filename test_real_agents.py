import asyncio
import json
import sys
from pathlib import Path

# Add agents directory
sys.path.insert(0, str(Path(__file__).parent / "agents"))

from real.real_backup_agent import RealBackupAgent
from real.real_monitoring_agent import RealMonitoringAgent
from real.real_sync_agent import RealSyncAgent


async def test_monitoring_agent():
    """Test REAL monitoring with system metrics."""
    print("\n" + "=" * 60)
    print("TEST 1: MonitoringAgent - REAL System Scan")
    print("=" * 60)

    agent = RealMonitoringAgent()

    # Test 1: Health check
    print("\nðŸ” Running REAL health check...")
    result = await agent.execute({"operation": "health_check"})

    print(f"\nStatus: {result['status']}")
    print(f"CPU: {result['metrics']['cpu']['percent']}%")
    print(
        f"Memory: {result['metrics']['memory']['percent']}% ({result['metrics']['memory']['used_gb']} GB / {result['metrics']['memory']['total_gb']} GB)"
    )
    print(
        f"Disk: {result['metrics']['disk']['percent']}% ({result['metrics']['disk']['used_gb']} GB / {result['metrics']['disk']['total_gb']} GB)"
    )
    print(f"Processes: {result['metrics']['processes']}")

    if result["issues"]:
        print(f"\nâš ï¸ Issues detected:")
        for issue in result["issues"]:
            print(f"  - {issue}")
    else:
        print(f"\nâœ… System healthy - no issues")

    # Test 2: Check Docker services
    print("\n\nðŸ³ Checking Docker services...")
    result = await agent.execute({"operation": "check_services"})

    print(f"\nTotal services: {result['total_services']}")
    print(f"Running: {result['running_services']}")
    print(f"Degraded: {result['degraded_services']}")
    print(f"Missing: {result['missing_services']}")

    # Test 3: Check GPU
    print("\n\nðŸŽ® Checking NVIDIA GPU...")
    result = await agent.execute({"operation": "check_gpu"})

    if result["status"] == "available":
        print(f"\nâœ… GPU Found: {result['gpu_name']}")
        print(f"  Memory: {result['memory_used_mb']} MB / {result['memory_total_mb']} MB")
        print(f"  Utilization: {result['gpu_utilization_percent']}%")
        print(f"  Temperature: {result['temperature_celsius']}Â°C")
    else:
        print(f"\nâš ï¸ GPU not available: {result.get('error', 'Unknown')}")

    return True


async def test_backup_agent():
    """Test REAL backup creation."""
    print("\n\n" + "=" * 60)
    print("TEST 2: BackupAgent - REAL Backup Creation")
    print("=" * 60)

    agent = RealBackupAgent(backup_dir="C:/TwisterLab/backups")

    # Test 1: Create backup
    print("\nðŸ“¦ Creating REAL backup...")
    result = await agent.execute({"operation": "create_backup"})

    if result["status"] == "success":
        print(f"\nâœ… Backup created successfully!")
        print(f"  Backup ID: {result['backup_id']}")
        print(f"  File: {result['backup_file']}")
        print(f"  Size: {result['size_mb']} MB")
        print(f"  Checksum: {result['checksum'][:16]}...")
        print(f"  Components: {', '.join(result['components'])}")
        print(f"  Time: {result['execution_time']:.2f}s")
    else:
        print(f"\nâŒ Backup failed: {result.get('error')}")
        return False

    # Test 2: List backups
    print("\n\nðŸ“‹ Listing backups...")
    result = await agent.execute({"operation": "list_backups"})

    print(f"\nTotal backups: {result['total_backups']}")
    for backup in result["backups"][-3:]:  # Last 3
        print(f"  - {backup['backup_name']} ({backup.get('size_mb', 'N/A')} MB)")

    return True


async def test_sync_agent():
    """Test REAL sync operations."""
    print("\n\n" + "=" * 60)
    print("TEST 3: SyncAgent - REAL Redis â†” PostgreSQL Sync")
    print("=" * 60)

    agent = RealSyncAgent()

    # Test 1: Sync all
    print("\nðŸ”„ Syncing Redis â†” PostgreSQL...")
    result = await agent.execute({"operation": "sync_all"})

    print(f"\nStatus: {result['status']}")
    print(f"Total keys: {result['total_keys']}")
    print(f"Synced: {result['synced_keys']}")
    print(f"Skipped: {result['skipped_keys']}")

    # Test 2: Verify consistency
    print("\n\nðŸ” Verifying cache consistency...")
    result = await agent.execute({"operation": "verify_consistency"})

    print(f"\nConsistency: {result['consistency_percent']}%")
    print(f"Checked: {result['total_checked']} keys")
    print(f"Consistent: {result['consistent']}")
    print(f"Inconsistent: {result['inconsistent']}")

    # Test 3: Warm cache
    print("\n\nðŸ”¥ Warming cache...")
    result = await agent.execute({"operation": "warm_cache"})

    print(f"\nLoaded: {result['loaded_keys']} keys")
    print(f"Categories:")
    for category, count in result["categories"].items():
        print(f"  - {category}: {count}")

    return True


async def main():
    """Run all tests."""
    print("\nðŸš€ Starting REAL agent tests...")

    success_count = 0
    total_tests = 3

    try:
        if await test_monitoring_agent():
            success_count += 1
    except Exception as e:
        print(f"\nâŒ MonitoringAgent test failed: {e}")

    try:
        if await test_backup_agent():
            success_count += 1
    except Exception as e:
        print(f"\nâŒ BackupAgent test failed: {e}")

    try:
        if await test_sync_agent():
            success_count += 1
    except Exception as e:
        print(f"\nâŒ SyncAgent test failed: {e}")

    # Summary
    print("\n\n" + "=" * 60)
    print(f"TEST SUMMARY: {success_count}/{total_tests} agents working")
    print("=" * 60)

    if success_count == total_tests:
        print("\nâœ… ALL AGENTS WORKING - 100% REAL!")
        return 0
    else:
        print(f"\nâš ï¸ {total_tests - success_count} agent(s) failed")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
