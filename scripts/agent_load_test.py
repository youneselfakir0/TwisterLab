#!/usr/bin/env python3
"""
TwisterLab Agent Load Testing Script
Generates realistic agent operations to populate metrics and dashboards.
"""
import asyncio
import json
import random
import sys
from datetime import datetime
from typing import Dict, List

import httpx

# Configuration
API_BASE_URL = "http://192.168.0.30:8000"
GRAFANA_DASHBOARD_URL = "http://192.168.0.30:3000/d/twisterlab-agents-realtime"

# Agent operations configuration
AGENT_OPERATIONS = {
    "backupagent": [
        {"operation": "status", "weight": 3},
        {"operation": "execute", "weight": 1},
    ],
    "syncagent": [
        {"operation": "status", "weight": 2},
        {"operation": "execute", "weight": 2},
        {"operation": "verify", "weight": 1},
    ],
    "monitoringagent": [
        {"operation": "status", "weight": 3},
        {"operation": "health_check", "weight": 2, "context": {"check_type": "system"}},
    ],
    "classifieragent": [
        {"operation": "classify", "weight": 5, "data": {
            "ticket_id": lambda: f"T-{random.randint(1000, 9999)}",
            "title": lambda: random.choice([
                "Printer not working",
                "Cannot connect to WiFi",
                "Slow computer performance",
                "Password reset needed",
                "Software installation request"
            ]),
            "priority": lambda: random.choice(["low", "medium", "high", "critical"])
        }},
    ],
    "resolveragent": [
        {"operation": "resolve", "weight": 3, "data": {
            "ticket_id": lambda: f"T-{random.randint(1000, 9999)}",
            "issue_type": lambda: random.choice(["printer", "network", "software", "hardware"])
        }},
    ],
    "desktopcommanderagent": [
        {"operation": "execute_command", "weight": 2, "data": {
            "command": lambda: random.choice([
                "ipconfig /renew",
                "systeminfo",
                "tasklist",
                "netstat -an"
            ])
        }},
    ],
    "maestroorchestratoragent": [
        {"operation": "orchestrate", "weight": 1, "data": {
            "workflow": lambda: random.choice([
                "ticket_resolution",
                "system_maintenance",
                "backup_and_sync"
            ]),
            "agents": lambda: random.choice([
                ["classifier", "resolver"],
                ["backup", "sync"],
                ["monitoring", "sync"]
            ])
        }},
    ],
}


class AgentLoadTester:
    """Generate load on TwisterLab agents to populate monitoring dashboards."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "operations_by_agent": {},
            "start_time": datetime.now(),
        }

    async def execute_agent_operation(
        self,
        client: httpx.AsyncClient,
        agent_name: str,
        operation_config: Dict
    ) -> Dict:
        """Execute a single agent operation."""

        # Build payload
        payload = {
            "operation": operation_config["operation"]
        }

        # Add dynamic data if configured
        if "data" in operation_config:
            data = {}
            for key, value_func in operation_config["data"].items():
                data[key] = value_func() if callable(value_func) else value_func
            payload["data"] = data

        # Add context if configured
        if "context" in operation_config:
            payload["context"] = operation_config["context"]

        # Execute request
        url = f"{self.base_url}/api/v1/autonomous/agents/{agent_name}/execute"

        try:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            result = response.json()

            self.stats["successful_operations"] += 1

            return {
                "status": "success",
                "agent": agent_name,
                "operation": operation_config["operation"],
                "result": result
            }

        except httpx.HTTPStatusError as e:
            self.stats["failed_operations"] += 1
            return {
                "status": "error",
                "agent": agent_name,
                "operation": operation_config["operation"],
                "error": str(e)
            }

        except Exception as e:
            self.stats["failed_operations"] += 1
            return {
                "status": "error",
                "agent": agent_name,
                "operation": operation_config["operation"],
                "error": str(e)
            }

    def select_random_operation(self, agent_name: str) -> Dict:
        """Select a random operation for the given agent based on weights."""
        operations = AGENT_OPERATIONS.get(agent_name, [])
        if not operations:
            return None

        # Weighted random selection
        weights = [op["weight"] for op in operations]
        selected = random.choices(operations, weights=weights, k=1)[0]

        return selected

    async def run_continuous_load(
        self,
        duration_seconds: int = 300,
        operations_per_minute: int = 60
    ):
        """Run continuous load test for specified duration."""

        print(f"\n{'='*70}")
        print(f"🚀 TwisterLab Agent Load Testing")
        print(f"{'='*70}")
        print(f"Duration: {duration_seconds}s ({duration_seconds//60} minutes)")
        print(f"Target Rate: {operations_per_minute} ops/minute (~{operations_per_minute/60:.1f} ops/sec)")
        print(f"Grafana Dashboard: {GRAFANA_DASHBOARD_URL}")
        print(f"{'='*70}\n")

        interval = 60.0 / operations_per_minute  # seconds between operations
        end_time = datetime.now().timestamp() + duration_seconds

        async with httpx.AsyncClient() as client:
            operation_count = 0

            while datetime.now().timestamp() < end_time:
                # Select random agent and operation
                agent_name = random.choice(list(AGENT_OPERATIONS.keys()))
                operation_config = self.select_random_operation(agent_name)

                if operation_config:
                    # Execute operation
                    result = await self.execute_agent_operation(
                        client, agent_name, operation_config
                    )

                    self.stats["total_operations"] += 1

                    # Track per-agent stats
                    if agent_name not in self.stats["operations_by_agent"]:
                        self.stats["operations_by_agent"][agent_name] = 0
                    self.stats["operations_by_agent"][agent_name] += 1

                    operation_count += 1

                    # Print status every 10 operations
                    if operation_count % 10 == 0:
                        elapsed = (datetime.now() - self.stats["start_time"]).total_seconds()
                        rate = self.stats["total_operations"] / elapsed if elapsed > 0 else 0

                        print(f"[{operation_count:04d}] "
                              f"{agent_name:25s} → {operation_config['operation']:15s} "
                              f"({result['status']}) "
                              f"[Rate: {rate:.2f} ops/sec]")

                    # Wait for next operation
                    await asyncio.sleep(interval)

        self.print_final_stats()

    async def run_burst_test(
        self,
        num_operations: int = 100,
        agents: List[str] = None
    ):
        """Run a burst of operations as fast as possible."""

        print(f"\n{'='*70}")
        print(f"⚡ TwisterLab Agent Burst Test")
        print(f"{'='*70}")
        print(f"Operations: {num_operations}")
        print(f"Agents: {', '.join(agents) if agents else 'ALL'}")
        print(f"{'='*70}\n")

        target_agents = agents if agents else list(AGENT_OPERATIONS.keys())

        async with httpx.AsyncClient() as client:
            tasks = []

            for i in range(num_operations):
                agent_name = random.choice(target_agents)
                operation_config = self.select_random_operation(agent_name)

                if operation_config:
                    task = self.execute_agent_operation(client, agent_name, operation_config)
                    tasks.append(task)

            # Execute all operations concurrently
            results = await asyncio.gather(*tasks)

            # Update stats
            for result in results:
                self.stats["total_operations"] += 1
                agent_name = result["agent"]

                if agent_name not in self.stats["operations_by_agent"]:
                    self.stats["operations_by_agent"][agent_name] = 0
                self.stats["operations_by_agent"][agent_name] += 1

        self.print_final_stats()

    def print_final_stats(self):
        """Print final test statistics."""

        elapsed = (datetime.now() - self.stats["start_time"]).total_seconds()
        success_rate = (
            self.stats["successful_operations"] / self.stats["total_operations"] * 100
            if self.stats["total_operations"] > 0 else 0
        )
        avg_rate = self.stats["total_operations"] / elapsed if elapsed > 0 else 0

        print(f"\n{'='*70}")
        print(f"📊 Test Results Summary")
        print(f"{'='*70}")
        print(f"Total Operations:      {self.stats['total_operations']}")
        print(f"Successful:            {self.stats['successful_operations']} ({success_rate:.1f}%)")
        print(f"Failed:                {self.stats['failed_operations']}")
        print(f"Duration:              {elapsed:.1f}s")
        print(f"Average Rate:          {avg_rate:.2f} ops/sec")
        print(f"\nOperations by Agent:")
        print(f"{'-'*70}")

        for agent, count in sorted(
            self.stats["operations_by_agent"].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            percentage = count / self.stats["total_operations"] * 100
            print(f"  {agent:30s} {count:5d} ops ({percentage:5.1f}%)")

        print(f"{'='*70}")
        print(f"\n✅ View metrics in Grafana:")
        print(f"   {GRAFANA_DASHBOARD_URL}")
        print(f"\n✅ View Prometheus metrics:")
        print(f"   {API_BASE_URL}/metrics")
        print(f"{'='*70}\n")


async def main():
    """Main entry point."""

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python agent_load_test.py continuous [duration_seconds] [ops_per_minute]")
        print("  python agent_load_test.py burst [num_operations]")
        print("\nExamples:")
        print("  python agent_load_test.py continuous 300 60    # 5 min @ 60 ops/min")
        print("  python agent_load_test.py burst 100            # 100 ops as fast as possible")
        sys.exit(1)

    mode = sys.argv[1]
    tester = AgentLoadTester()

    try:
        if mode == "continuous":
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 300
            ops_per_min = int(sys.argv[3]) if len(sys.argv) > 3 else 60
            await tester.run_continuous_load(duration, ops_per_min)

        elif mode == "burst":
            num_ops = int(sys.argv[2]) if len(sys.argv) > 2 else 100
            await tester.run_burst_test(num_ops)

        else:
            print(f"Unknown mode: {mode}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        tester.print_final_stats()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
