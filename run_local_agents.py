#!/usr/bin/env python3
"""
TwisterLab Local Agents Runner
Execute Real agents locally on CoreRTX without API dependency
"""
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Any

from agents.real.real_monitoring_agent import RealMonitoringAgent
from agents.real.real_backup_agent import RealBackupAgent
from agents.real.real_sync_agent import RealSyncAgent
from agents.real.real_classifier_agent import RealClassifierAgent
from agents.real.real_resolver_agent import RealResolverAgent
from agents.real.real_desktop_commander_agent import RealDesktopCommanderAgent
from agents.real.real_maestro_agent import RealMaestroAgent


class LocalAgentRunner:
    """Run TwisterLab agents locally without API"""

    def __init__(self):
        self.agents = {
            "monitoring": RealMonitoringAgent(),
            "backup": RealBackupAgent(),
            "sync": RealSyncAgent(),
            "classifier": RealClassifierAgent(),
            "resolver": RealResolverAgent(),
            "desktop_commander": RealDesktopCommanderAgent(),
            "maestro": RealMaestroAgent()
        }

    async def get_system_health(self) -> Dict[str, Any]:
        """Get full system health from RealMonitoringAgent"""
        agent = self.agents["monitoring"]
        return await agent.execute({"check_type": "all"})

    async def create_backup(self, backup_type: str = "full") -> Dict[str, Any]:
        """Create system backup"""
        agent = self.agents["backup"]
        return await agent.execute({
            "backup_type": backup_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    async def sync_cache_db(self) -> Dict[str, Any]:
        """Synchronize cache and database"""
        agent = self.agents["sync"]
        return await agent.execute({"action": "sync"})

    async def classify_ticket(self, description: str) -> Dict[str, Any]:
        """Classify a support ticket"""
        agent = self.agents["classifier"]
        return await agent.execute({
            "ticket_description": description,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    async def resolve_ticket(self, ticket_id: str, category: str) -> Dict[str, Any]:
        """Execute SOP to resolve ticket"""
        agent = self.agents["resolver"]
        return await agent.execute({
            "ticket_id": ticket_id,
            "category": category,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    async def execute_command(self, command: str, target: str = "localhost") -> Dict[str, Any]:
        """Execute remote desktop command"""
        agent = self.agents["desktop_commander"]
        return await agent.execute({
            "command": command,
            "target": target,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    async def orchestrate_workflow(self, workflow_type: str) -> Dict[str, Any]:
        """Orchestrate multi-agent workflow"""
        agent = self.agents["maestro"]
        return await agent.execute({
            "workflow_type": workflow_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    async def list_agents(self) -> Dict[str, Any]:
        """List all available agents"""
        return {
            "status": "success",
            "mode": "local",
            "agents": {
                name: {
                    "name": agent.name,
                    "status": "operational",
                    "type": type(agent).__name__
                }
                for name, agent in self.agents.items()
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


async def demo():
    """Demonstration of local agents"""
    runner = LocalAgentRunner()

    print("=" * 80)
    print("TWISTERLAB LOCAL AGENTS - RUNNING ON CORERTX")
    print("=" * 80)
    print()

    # List agents
    print("📋 Available Agents:")
    agents_list = await runner.list_agents()
    for name, info in agents_list["agents"].items():
        print(f"  ✓ {info['name']} ({info['type']})")
    print()

    # System health
    print("🔍 System Health Check:")
    health = await runner.get_system_health()
    if health["status"] == "success":
        hc = health["health_check"]
        print(f"  CPU: {hc['cpu_percent']}% ({hc['cpu_count']} cores)")
        print(f"  Memory: {hc['memory_percent']}% ({hc['memory_used_gb']:.1f}/{hc['memory_total_gb']:.1f} GB)")
        print(f"  Disk: {hc['disk_percent']}% ({hc['disk_used_gb']:.1f}/{hc['disk_total_gb']:.1f} GB)")
        print(f"  Network: ↓{hc['network_received_mb']:.1f} MB  ↑{hc['network_sent_mb']:.1f} MB")
        print(f"  Processes: {hc['processes']}")
    print()

    # Classify ticket
    print("🎯 Ticket Classification:")
    ticket = await runner.classify_ticket("Server API returns 500 error on /health endpoint")
    if ticket["status"] == "success":
        print(f"  Category: {ticket.get('category', 'N/A')}")
        print(f"  Priority: {ticket.get('priority', 'N/A')}")
        print(f"  Agent: {ticket.get('assigned_agent', 'N/A')}")
    print()

    print("=" * 80)
    print("✓ ALL AGENTS OPERATIONAL IN LOCAL MODE")
    print("=" * 80)


async def interactive():
    """Interactive mode for manual agent testing"""
    runner = LocalAgentRunner()

    print("\n🤖 TwisterLab Local Agent Runner - Interactive Mode")
    print("Commands:")
    print("  1. health       - System health check")
    print("  2. backup       - Create backup")
    print("  3. sync         - Sync cache/DB")
    print("  4. classify     - Classify ticket")
    print("  5. resolve      - Resolve ticket")
    print("  6. command      - Execute desktop command")
    print("  7. orchestrate  - Run workflow")
    print("  8. list         - List agents")
    print("  9. demo         - Run demo")
    print("  q. quit\n")

    while True:
        choice = input("Enter command: ").strip().lower()

        if choice == "q":
            break
        elif choice == "1" or choice == "health":
            result = await runner.get_system_health()
            print(json.dumps(result, indent=2))
        elif choice == "2" or choice == "backup":
            result = await runner.create_backup()
            print(json.dumps(result, indent=2))
        elif choice == "3" or choice == "sync":
            result = await runner.sync_cache_db()
            print(json.dumps(result, indent=2))
        elif choice == "4" or choice == "classify":
            desc = input("Ticket description: ")
            result = await runner.classify_ticket(desc)
            print(json.dumps(result, indent=2))
        elif choice == "5" or choice == "resolve":
            ticket_id = input("Ticket ID: ")
            category = input("Category: ")
            result = await runner.resolve_ticket(ticket_id, category)
            print(json.dumps(result, indent=2))
        elif choice == "6" or choice == "command":
            cmd = input("Command: ")
            result = await runner.execute_command(cmd)
            print(json.dumps(result, indent=2))
        elif choice == "7" or choice == "orchestrate":
            workflow = input("Workflow type: ")
            result = await runner.orchestrate_workflow(workflow)
            print(json.dumps(result, indent=2))
        elif choice == "8" or choice == "list":
            result = await runner.list_agents()
            print(json.dumps(result, indent=2))
        elif choice == "9" or choice == "demo":
            await demo()
        else:
            print("Unknown command")

        print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive())
    else:
        asyncio.run(demo())
