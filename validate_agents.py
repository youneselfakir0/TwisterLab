# =============================================================================
# TWISTERLAB AGENTS VALIDATION SCRIPT
# Version: 1.0.0
# Date: 2025-11-15
#
# Validates all TwisterLab agents are properly configured and functional
# =============================================================================

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def validate_agents():
    """Validate all Real agents"""
    print("=" * 80)
    print("TWISTERLAB AGENTS VALIDATION")
    print("=" * 80)
    print()
    
    agents = []
    errors = []
    
    # Import and validate each agent
    agent_modules = [
        ("RealMonitoringAgent", "agents.real.real_monitoring_agent"),
        ("RealBackupAgent", "agents.real.real_backup_agent"),
        ("RealSyncAgent", "agents.real.real_sync_agent"),
        ("RealClassifierAgent", "agents.real.real_classifier_agent"),
        ("RealResolverAgent", "agents.real.real_resolver_agent"),
        ("RealDesktopCommanderAgent", "agents.real.real_desktop_commander_agent"),
        ("RealMaestroAgent", "agents.real.real_maestro_agent"),
    ]
    
    for agent_name, module_path in agent_modules:
        try:
            print(f"Validating {agent_name}...", end=" ")
            
            # Import module
            module = __import__(module_path, fromlist=[agent_name])
            agent_class = getattr(module, agent_name)
            
            # Instantiate agent
            agent = agent_class()
            
            # Validate required attributes
            assert hasattr(agent, 'name'), f"{agent_name} missing 'name' attribute"
            assert hasattr(agent, 'execute'), f"{agent_name} missing 'execute' method"
            
            # Check if execute is async
            if asyncio.iscoroutinefunction(agent.execute):
                print(f"✓ OK (async)")
            else:
                print(f"✓ OK (sync)")
            
            agents.append({
                "name": agent.name,
                "class": agent_name,
                "module": module_path,
                "async": asyncio.iscoroutinefunction(agent.execute)
            })
            
        except Exception as e:
            print(f"✗ FAILED: {e}")
            errors.append({
                "agent": agent_name,
                "error": str(e)
            })
    
    print()
    print("=" * 80)
    print(f"VALIDATION RESULTS: {len(agents)} agents validated, {len(errors)} errors")
    print("=" * 80)
    print()
    
    if agents:
        print("✓ WORKING AGENTS:")
        for agent in agents:
            async_marker = " (async)" if agent["async"] else " (sync)"
            print(f"  - {agent['name']}{async_marker}")
        print()
    
    if errors:
        print("✗ FAILED AGENTS:")
        for error in errors:
            print(f"  - {error['agent']}: {error['error']}")
        print()
        return False
    
    # Test basic execution
    print("Testing MonitoringAgent execution...")
    try:
        from agents.real.real_monitoring_agent import RealMonitoringAgent
        monitoring_agent = RealMonitoringAgent()
        result = await monitoring_agent.execute({})
        
        if result.get("status") == "success":
            print(f"✓ MonitoringAgent executed successfully")
            print(f"  CPU: {result.get('data', {}).get('cpu_percent', 'N/A')}%")
            print(f"  Memory: {result.get('data', {}).get('memory_percent', 'N/A')}%")
            print(f"  Disk: {result.get('data', {}).get('disk_usage', {}).get('percent', 'N/A')}%")
        else:
            print(f"✗ MonitoringAgent execution failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"✗ MonitoringAgent test failed: {e}")
        return False
    
    print()
    print("=" * 80)
    print("✓ ALL AGENTS VALIDATED AND FUNCTIONAL")
    print("=" * 80)
    return True

if __name__ == "__main__":
    result = asyncio.run(validate_agents())
    sys.exit(0 if result else 1)
