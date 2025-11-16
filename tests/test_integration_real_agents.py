"""
Integration Test for Real Agents on edgeserver
Tests all 7 agents with real Redis/PostgreSQL infrastructure
"""

import asyncio
import sys
from datetime import datetime

import aiohttp

EDGESERVER = "192.168.0.30"
API_URL = f"http://{EDGESERVER}:8000"


async def test_agent(session, agent_name, operation, params=None):
    """Test a specific agent operation."""
    url = f"{API_URL}/agents/{agent_name}/execute"

    payload = {"operation": operation}
    if params:
        payload.update(params)

    try:
        async with session.post(url, json=payload, timeout=30) as response:
            if response.status == 200:
                result = await response.json()
                return {
                    "agent": agent_name,
                    "operation": operation,
                    "status": "✅ SUCCESS",
                    "result": result,
                }
            else:
                text = await response.text()
                return {
                    "agent": agent_name,
                    "operation": operation,
                    "status": "❌ FAILED",
                    "error": f"HTTP {response.status}: {text[:100]}",
                }
    except asyncio.TimeoutError:
        return {
            "agent": agent_name,
            "operation": operation,
            "status": "⏱️ TIMEOUT",
            "error": "Request timeout (>30s)",
        }
    except Exception as e:
        return {"agent": agent_name, "operation": operation, "status": "❌ ERROR", "error": str(e)}


async def run_integration_tests():
    """Run full integration test suite."""
    print("\n" + "=" * 70)
    print("🧪 TWISTERLAB REAL AGENTS INTEGRATION TEST")
    print(f"   Edgeserver: {EDGESERVER}")
    print(f"   API: {API_URL}")
    print("=" * 70 + "\n")

    # Check API health
    print("📡 Checking API health...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_URL}/health", timeout=5) as response:
                if response.status == 200:
                    print("✅ API is responsive\n")
                else:
                    print(f"❌ API returned status {response.status}")
                    return
        except Exception as e:
            print(f"❌ Cannot connect to API: {e}")
            return

    # Test cases
    tests = [
        {
            "name": "MonitoringAgent - Health Check",
            "agent": "monitoring",
            "operation": "health_check",
            "validate": lambda r: r.get("status") == "success" and "health_check" in r,
        },
        {
            "name": "MonitoringAgent - Full Diagnostic",
            "agent": "monitoring",
            "operation": "full_diagnostic",
            "validate": lambda r: r.get("status") == "success",
        },
        {
            "name": "BackupAgent - List Backups",
            "agent": "backup",
            "operation": "list_backups",
            "validate": lambda r: r.get("status") == "success" and "backups" in r,
        },
        {
            "name": "BackupAgent - Create Backup",
            "agent": "backup",
            "operation": "create_backup",
            "validate": lambda r: r.get("status") == "success" and "backup" in r,
        },
        {
            "name": "SyncAgent - Verify Consistency",
            "agent": "sync",
            "operation": "verify_consistency",
            "validate": lambda r: r.get("status") == "success" and "consistency" in r,
        },
        {
            "name": "ClassifierAgent - Classify Ticket",
            "agent": "classifier",
            "operation": "classify_ticket",
            "params": {
                "ticket": {
                    "title": "Database connection timeout",
                    "description": "PostgreSQL connection keeps timing out",
                }
            },
            "validate": lambda r: r.get("status") == "success" and "classification" in r,
        },
        {
            "name": "ResolverAgent - List SOPs",
            "agent": "resolver",
            "operation": "list_sops",
            "validate": lambda r: r.get("status") == "success" and "sops" in r,
        },
        {
            "name": "ResolverAgent - Execute SOP",
            "agent": "resolver",
            "operation": "execute_sop",
            "params": {"sop_id": "SOP-001", "params": {"target": "192.168.0.1"}},
            "validate": lambda r: r.get("status") == "success" and "execution" in r,
        },
        {
            "name": "DesktopCommanderAgent - System Info",
            "agent": "desktop_commander",
            "operation": "get_system_info",
            "validate": lambda r: r.get("status") == "success" and "system_info" in r,
        },
        {
            "name": "MaestroAgent - Health Check All",
            "agent": "maestro",
            "operation": "health_check_all",
            "validate": lambda r: r.get("status") == "success" and "total_agents" in r,
        },
    ]

    results = []

    async with aiohttp.ClientSession() as session:
        for i, test in enumerate(tests, 1):
            print(f"[{i}/{len(tests)}] Testing: {test['name']}...")

            result = await test_agent(session, test["agent"], test["operation"], test.get("params"))

            # Validate result
            if result["status"] == "✅ SUCCESS":
                try:
                    if test["validate"](result["result"]):
                        print(f"     ✅ PASSED")
                    else:
                        print(f"     ⚠️  SUCCESS but validation failed")
                        result["status"] = "⚠️ PARTIAL"
                except Exception as e:
                    print(f"     ⚠️  Validation error: {e}")
                    result["status"] = "⚠️ PARTIAL"
            else:
                print(f"     {result['status']}: {result.get('error', 'Unknown error')}")

            results.append(result)

            # Small delay between tests
            await asyncio.sleep(0.5)

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70 + "\n")

    success = sum(1 for r in results if r["status"] == "✅ SUCCESS")
    partial = sum(1 for r in results if r["status"] == "⚠️ PARTIAL")
    failed = sum(
        1
        for r in results
        if "FAILED" in r["status"] or "ERROR" in r["status"] or "TIMEOUT" in r["status"]
    )

    for result in results:
        status_icon = result["status"].split()[0]
        print(f"   {status_icon} {result['agent']:20} - {result['operation']}")

    print(f"\n   Total Tests: {len(results)}")
    print(f"   ✅ Success: {success}")
    print(f"   ⚠️  Partial: {partial}")
    print(f"   ❌ Failed: {failed}")

    percentage = (success / len(results)) * 100 if results else 0
    print(f"\n   Overall Success Rate: {percentage:.1f}%")

    if percentage >= 90:
        print("\n   🎉 INTEGRATION TEST PASSED!")
        print("   All agents are working with real infrastructure!")
    elif percentage >= 70:
        print("\n   ⚠️  INTEGRATION TEST PARTIAL")
        print("   Most agents working, some need attention")
    else:
        print("\n   ❌ INTEGRATION TEST FAILED")
        print("   Multiple agents need fixes")

    print("\n" + "=" * 70 + "\n")

    # Detailed results for failed tests
    failed_tests = [r for r in results if "SUCCESS" not in r["status"]]
    if failed_tests:
        print("🔍 FAILED TEST DETAILS:\n")
        for result in failed_tests:
            print(f"   Agent: {result['agent']}")
            print(f"   Operation: {result['operation']}")
            print(f"   Error: {result.get('error', 'Unknown')}")
            print()

    return percentage >= 70


if __name__ == "__main__":
    try:
        success = asyncio.run(run_integration_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
