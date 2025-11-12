"""
Test MCP Real API Endpoints Locally
Quick validation script before deployment
"""
import asyncio
import json
from agents.real.real_classifier_agent import RealClassifierAgent
from agents.real.real_resolver_agent import RealResolverAgent
from agents.real.real_monitoring_agent import RealMonitoringAgent
from agents.real.real_backup_agent import RealBackupAgent


async def test_classify():
    """Test classifier agent."""
    print("\n=== TEST 1: Classify Ticket ===")
    agent = RealClassifierAgent()
    result = await agent.execute({
        "operation": "classify_ticket",
        "ticket": {
            "description": "WiFi connection keeps dropping every few minutes",
            "title": "WiFi issues"
        }
    })
    print(json.dumps(result, indent=2))
    return result.get("status") == "success"


async def test_resolve():
    """Test resolver agent."""
    print("\n=== TEST 2: Resolve Ticket ===")
    agent = RealResolverAgent()
    result = await agent.execute({
        "operation": "resolve_ticket",
        "ticket": {
            "category": "network",
            "description": "WiFi not working"
        }
    })
    print(json.dumps(result, indent=2))
    return result.get("status") == "success"


async def test_monitor():
    """Test monitoring agent."""
    print("\n=== TEST 3: Monitor System Health ===")
    agent = RealMonitoringAgent()
    result = await agent.execute({
        "operation": "health_check",
        "detailed": False
    })
    print(json.dumps(result, indent=2))
    return result.get("status") == "success"


async def test_backup():
    """Test backup agent."""
    print("\n=== TEST 4: Create Backup ===")
    agent = RealBackupAgent(backup_dir="test_backups")
    result = await agent.execute({
        "operation": "create_backup",
        "backup_type": "config"  # Fast test - config only
    })
    print(json.dumps(result, indent=2))
    return result.get("status") in ["success", "completed"]


async def main():
    """Run all tests."""
    print("=" * 60)
    print("MCP REAL AGENTS - DIRECT TEST")
    print("=" * 60)
    
    results = {
        "classify_ticket": await test_classify(),
        "resolve_ticket": await test_resolve(),
        "monitor_system_health": await test_monitor(),
        "create_backup": await test_backup()
    }
    
    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print("=" * 60)
    for tool, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {tool}")
    
    total = sum(results.values())
    print(f"\n{total}/4 tests passed")
    
    if total == 4:
        print("\n🚀 ALL TESTS PASSED - Ready for API integration!")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED - Check errors above")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
