# Test All 7 Real TwisterLab Agents
# Tests each agent with realistic operations

Write-Host "`n🧪 TESTING ALL 7 REAL TWISTERLAB AGENTS`n" -ForegroundColor Cyan

# Auto-install dependencies
Write-Host "📦 Checking dependencies..." -ForegroundColor Yellow
$pythonCmd = "python"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python not found" -ForegroundColor Red
    exit 1
}

# Install required packages
& $pythonCmd -m pip install --quiet psutil redis 2>$null

# Create Python test script
$testScript = @'
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_all_agents():
    print("\n" + "="*60)
    print("TESTING ALL 7 REAL TWISTERLAB AGENTS")
    print("="*60 + "\n")

    results = []

    # TEST 1: MonitoringAgent
    print("1. TESTING MonitoringAgent...")
    try:
        from agents.real.real_monitoring_agent import RealMonitoringAgent
        agent = RealMonitoringAgent()
        result = await agent.execute({"operation": "health_check"})

        if result["status"] == "success":
            hc = result['health_check']
            print(f"   SUCCESS: {result['health_status']}")
            print(f"   - CPU: {hc['cpu_percent']}%")
            print(f"   - Memory: {hc['memory_percent']}% ({hc['memory_used_gb']:.1f}GB / {hc['memory_total_gb']:.1f}GB)")
            print(f"   - Disk: {hc['disk_percent']}% ({hc['disk_used_gb']:.0f}GB / {hc['disk_total_gb']:.0f}GB)")
            results.append(("MonitoringAgent", "SUCCESS"))
        else:
            print(f"   PARTIAL: {result.get('error')}")
            results.append(("MonitoringAgent", "PARTIAL"))
    except Exception as e:
        print(f"   FAILED: {e}")
        results.append(("MonitoringAgent", "FAILED"))

    # TEST 2: BackupAgent
    print("\n2. TESTING BackupAgent...")
    try:
        from agents.real.real_backup_agent import RealBackupAgent
        agent = RealBackupAgent()
        result = await agent.execute({"operation": "create_backup"})

        if result["status"] == "success":
            bk = result['backup']
            print(f"   SUCCESS: Backup created")
            print(f"   - File: {bk['filename']}")
            print(f"   - Components: {len(bk['components'])}")
            print(f"   - Time: {bk['execution_time']:.2f}s")
            results.append(("BackupAgent", "SUCCESS"))
        else:
            print(f"   PARTIAL: {result.get('error')}")
            results.append(("BackupAgent", "PARTIAL"))
    except Exception as e:
        print(f"   FAILED: {e}")
        results.append(("BackupAgent", "FAILED"))

    # TEST 3: SyncAgent
    print("\n3. TESTING SyncAgent...")
    try:
        from agents.real.real_sync_agent import RealSyncAgent
        agent = RealSyncAgent()
        result = await agent.execute({"operation": "verify_consistency"})

        if result["status"] == "success":
            cs = result['consistency']
            print(f"   SUCCESS: {cs['status']}")
            print(f"   - Consistency: {cs['consistency_percentage']:.1f}%")
            print(f"   - Items checked: {cs['items_checked']}")
            results.append(("SyncAgent", "SUCCESS"))
        else:
            print(f"   PARTIAL: {result.get('error')}")
            results.append(("SyncAgent", "PARTIAL"))
    except Exception as e:
        print(f"   FAILED: {e}")
        results.append(("SyncAgent", "FAILED"))

    # TEST 4: ClassifierAgent
    print("\n4. TESTING ClassifierAgent...")
    try:
        from agents.real.real_classifier_agent import RealClassifierAgent
        agent = RealClassifierAgent()

        test_ticket = {
            "ticket_id": "TEST-001",
            "title": "Network connection failed",
            "description": "Cannot connect to WiFi, ping to gateway times out"
        }

        result = await agent.execute({
            "operation": "classify_ticket",
            "ticket": test_ticket
        })

        if result["status"] == "success":
            cl = result['classification']
            print(f"   SUCCESS: Ticket classified")
            print(f"   - Category: {cl['category']}")
            print(f"   - Confidence: {cl['confidence']:.2f}")
            print(f"   - Priority: {cl['priority']}")
            print(f"   - Routed to: {cl['routed_to_agent']}")
            results.append(("ClassifierAgent", "SUCCESS"))
        else:
            print(f"   PARTIAL: {result.get('error')}")
            results.append(("ClassifierAgent", "PARTIAL"))
    except Exception as e:
        print(f"   FAILED: {e}")
        results.append(("ClassifierAgent", "FAILED"))

    # TEST 5: ResolverAgent
    print("\n5. TESTING ResolverAgent...")
    try:
        from agents.real.real_resolver_agent import RealResolverAgent
        agent = RealResolverAgent()

        result = await agent.execute({
            "operation": "execute_sop",
            "sop_id": "SOP-001",
            "params": {"target": "192.168.0.1"}
        })

        if result["status"] == "success":
            ex = result['execution']
            print(f"   SUCCESS: SOP executed")
            print(f"   - SOP: {ex['sop_id']}")
            print(f"   - Steps: {ex['steps_executed']}")
            print(f"   - Success: {ex['success']}")
            print(f"   - Outcome: {ex['outcome']}")
            print(f"   - Time: {ex['execution_time']:.2f}s")
            results.append(("ResolverAgent", "SUCCESS"))
        else:
            print(f"   PARTIAL: {result.get('error')}")
            results.append(("ResolverAgent", "PARTIAL"))
    except Exception as e:
        print(f"   FAILED: {e}")
        results.append(("ResolverAgent", "FAILED"))

    # TEST 6: DesktopCommanderAgent
    print("\n6. TESTING DesktopCommanderAgent...")
    try:
        from agents.real.real_desktop_commander_agent import RealDesktopCommanderAgent
        agent = RealDesktopCommanderAgent()
        result = await agent.execute({"operation": "get_system_info"})

        if result["status"] == "success":
            si = result['system_info']
            print(f"   SUCCESS: System info retrieved")
            print(f"   - Hostname: {si['hostname']}")
            print(f"   - Platform: {si['platform']}")
            print(f"   - Commands: {len(si['available_commands'])}")
            results.append(("DesktopCommanderAgent", "SUCCESS"))
        else:
            print(f"   PARTIAL: {result.get('error')}")
            results.append(("DesktopCommanderAgent", "PARTIAL"))
    except Exception as e:
        print(f"   FAILED: {e}")
        results.append(("DesktopCommanderAgent", "FAILED"))

    # TEST 7: MaestroAgent
    print("\n7. TESTING MaestroAgent...")
    try:
        from agents.real.real_maestro_agent import RealMaestroAgent
        agent = RealMaestroAgent()
        result = await agent.execute({"operation": "health_check_all"})

        if result["status"] == "success":
            print(f"   SUCCESS: Orchestration working")
            print(f"   - Total agents: {result['total_agents']}")
            print(f"   - Healthy: {result['healthy_agents']}")
            print(f"   - Unhealthy: {result['unhealthy_agents']}")
            results.append(("MaestroAgent", "SUCCESS"))
        else:
            print(f"   PARTIAL: {result.get('error')}")
            results.append(("MaestroAgent", "PARTIAL"))
    except Exception as e:
        print(f"   FAILED: {e}")
        results.append(("MaestroAgent", "FAILED"))

    # SUMMARY
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for agent_name, status in results:
        symbol = "+" if status == "SUCCESS" else ("~" if status == "PARTIAL" else "X")
        print(f"   [{symbol}] {status:10} {agent_name}")

    success = sum(1 for _, s in results if s == "SUCCESS")
    partial = sum(1 for _, s in results if s == "PARTIAL")
    failed = sum(1 for _, s in results if s == "FAILED")

    print(f"\n   Total: {len(results)} agents")
    print(f"   Success: {success}")
    print(f"   Partial: {partial}")
    print(f"   Failed: {failed}")

    percentage = (success / len(results)) * 100 if results else 0
    print(f"\n   Overall Success Rate: {percentage:.1f}%")

    if percentage >= 80:
        print("\n   AGENTS ARE OPERATIONAL!")
    elif percentage >= 50:
        print("\n   AGENTS PARTIALLY WORKING")
    else:
        print("\n   AGENTS NEED FIXES")

    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test_all_agents())
'@

# Write test script to temp file
$tempScript = Join-Path $env:TEMP "test_all_agents.py"
$testScript | Out-File -FilePath $tempScript -Encoding UTF8

# Run tests
Write-Host "`n▶️  Running tests...`n" -ForegroundColor Green
& $pythonCmd $tempScript

# Cleanup
Remove-Item $tempScript -Force

Write-Host "`n✅ Testing complete`n" -ForegroundColor Green
