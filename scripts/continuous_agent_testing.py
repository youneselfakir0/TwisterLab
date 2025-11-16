#!/usr/bin/env python3
"""
TwisterLab Continuous Agent Testing - Realistic Workload Generator
Simulates a typical IT helpdesk day with real agent operations.
"""
import asyncio
import json
import random
import time
from datetime import datetime
from typing import Any, Dict, List

import aiohttp

# Configuration
API_BASE_URL = "http://192.168.0.30:8000"
PROMETHEUS_URL = "http://192.168.0.30:9090"

# Realistic ticket scenarios for each agent
REALISTIC_SCENARIOS = {
    "classifieragent": [
        {
            "operation": "classify",
            "data": {"ticket_id": "T-{}", "title": "Cannot connect to WiFi", "priority": "high"},
        },
        {
            "operation": "classify",
            "data": {"ticket_id": "T-{}", "title": "Printer not working", "priority": "medium"},
        },
        {
            "operation": "classify",
            "data": {"ticket_id": "T-{}", "title": "Password reset request", "priority": "low"},
        },
        {
            "operation": "classify",
            "data": {"ticket_id": "T-{}", "title": "Email not sending", "priority": "high"},
        },
        {
            "operation": "classify",
            "data": {
                "ticket_id": "T-{}",
                "title": "Slow computer performance",
                "priority": "medium",
            },
        },
    ],
    "resolveragent": [
        {
            "operation": "resolve",
            "data": {"ticket_id": "T-{}", "issue_type": "wifi", "sop_id": "SOP-WIFI-001"},
        },
        {
            "operation": "resolve",
            "data": {"ticket_id": "T-{}", "issue_type": "printer", "sop_id": "SOP-PRINT-001"},
        },
        {
            "operation": "resolve",
            "data": {"ticket_id": "T-{}", "issue_type": "password", "sop_id": "SOP-PWD-001"},
        },
        {
            "operation": "resolve",
            "data": {"ticket_id": "T-{}", "issue_type": "email", "sop_id": "SOP-EMAIL-001"},
        },
    ],
    "desktopcommanderagent": [
        {
            "operation": "execute_command",
            "data": {"command": "ipconfig /all", "target": "DESKTOP-{}", "safe_mode": True},
        },
        {
            "operation": "execute_command",
            "data": {"command": "systeminfo", "target": "LAPTOP-{}", "safe_mode": True},
        },
        {
            "operation": "execute_command",
            "data": {"command": "ping 8.8.8.8 -n 4", "target": "WORKSTATION-{}", "safe_mode": True},
        },
        {
            "operation": "system_diagnostics",
            "data": {"target": "PC-{}", "tests": ["network", "disk", "memory"]},
        },
    ],
    "maestroagent": [
        {
            "operation": "orchestrate",
            "data": {"workflow_id": "WF-{}", "tasks": ["classify", "resolve", "verify"]},
        },
        {
            "operation": "balance_load",
            "data": {"agents": ["classifier", "resolver"], "threshold": 80},
        },
        {"operation": "health_check", "data": {"check_type": "full_system"}},
    ],
    "syncagent": [
        {
            "operation": "sync_cache",
            "data": {"source": "postgres", "target": "redis", "tables": ["tickets", "agents"]},
        },
        {"operation": "verify_consistency", "data": {"check_type": "cache_db_sync"}},
        {"operation": "invalidate_cache", "data": {"keys": ["ticket:*", "agent:*"]}},
    ],
    "backupagent": [
        {"operation": "status", "data": {}},
        {
            "operation": "create_backup",
            "data": {"type": "incremental", "databases": ["twisterlab_prod"]},
        },
        {
            "operation": "verify_backup",
            "data": {"backup_id": "BACKUP-{}", "verify_integrity": True},
        },
        {"operation": "list_backups", "data": {"limit": 10}},
    ],
    "monitoringagent": [
        {"operation": "check_health", "data": {"services": ["api", "postgres", "redis", "ollama"]}},
        {"operation": "collect_metrics", "data": {"interval": "1m", "aggregation": "avg"}},
        {"operation": "check_alerts", "data": {"severity": ["critical", "warning"]}},
    ],
}

# Workload distribution (percentage of operations per agent in a typical day)
AGENT_WORKLOAD_DISTRIBUTION = {
    "classifieragent": 30,  # 30% - Most tickets start here
    "resolveragent": 25,  # 25% - Main resolution work
    "desktopcommanderagent": 15,  # 15% - Remote commands
    "monitoringagent": 10,  # 10% - Continuous monitoring
    "syncagent": 10,  # 10% - Background sync
    "backupagent": 5,  # 5% - Scheduled backups
    "maestroagent": 5,  # 5% - Orchestration overhead
}


class AgentLoadTester:
    """Realistic load tester for TwisterLab agents."""

    def __init__(self):
        self.session: aiohttp.ClientSession = None
        self.ticket_counter = 1000
        self.stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "operations_by_agent": {},
            "start_time": None,
            "errors": [],
        }

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        self.stats["start_time"] = datetime.now()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    def _get_next_ticket_id(self) -> str:
        """Generate unique ticket ID."""
        ticket_id = f"T-{self.ticket_counter:06d}"
        self.ticket_counter += 1
        return ticket_id

    async def execute_agent_operation(
        self, agent_name: str, operation: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single agent operation."""

        # Replace placeholders in data
        processed_data = {}
        for key, value in data.items():
            if isinstance(value, str) and "{}" in value:
                if "ticket_id" in key.lower() or "id" in key.lower():
                    processed_data[key] = value.format(self._get_next_ticket_id())
                else:
                    processed_data[key] = value.format(random.randint(1000, 9999))
            else:
                processed_data[key] = value

        url = f"{API_BASE_URL}/api/v1/autonomous/agents/{agent_name}/execute"
        payload = {"operation": operation, "data": processed_data}

        try:
            async with self.session.post(url, json=payload, timeout=30) as response:
                result = await response.json()

                # Update stats
                self.stats["total_operations"] += 1
                if result.get("status") == "success":
                    self.stats["successful_operations"] += 1
                else:
                    self.stats["failed_operations"] += 1
                    self.stats["errors"].append(
                        {
                            "agent": agent_name,
                            "operation": operation,
                            "error": result.get("result", "Unknown error"),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                # Track per-agent stats
                if agent_name not in self.stats["operations_by_agent"]:
                    self.stats["operations_by_agent"][agent_name] = {
                        "total": 0,
                        "success": 0,
                        "failed": 0,
                    }

                self.stats["operations_by_agent"][agent_name]["total"] += 1
                if result.get("status") == "success":
                    self.stats["operations_by_agent"][agent_name]["success"] += 1
                else:
                    self.stats["operations_by_agent"][agent_name]["failed"] += 1

                return result

        except asyncio.TimeoutError:
            self.stats["total_operations"] += 1
            self.stats["failed_operations"] += 1
            self.stats["errors"].append(
                {
                    "agent": agent_name,
                    "operation": operation,
                    "error": "Timeout (30s)",
                    "timestamp": datetime.now().isoformat(),
                }
            )
            return {"status": "error", "error": "Timeout"}

        except Exception as e:
            self.stats["total_operations"] += 1
            self.stats["failed_operations"] += 1
            self.stats["errors"].append(
                {
                    "agent": agent_name,
                    "operation": operation,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )
            return {"status": "error", "error": str(e)}

    async def run_realistic_workload(
        self, duration_minutes: int = 5, operations_per_minute: int = 12
    ):
        """
        Run realistic workload based on typical helpdesk patterns.

        Args:
            duration_minutes: How long to run the test
            operations_per_minute: Target operations per minute (default: 12 = 1 ticket every 5 seconds)
        """
        print(f"\n{'='*80}")
        print(f"🚀 TWISTERLAB REALISTIC LOAD TEST")
        print(f"{'='*80}")
        print(f"📊 Configuration:")
        print(f"   - Duration: {duration_minutes} minutes")
        print(f"   - Target rate: {operations_per_minute} operations/minute")
        print(f"   - Expected total: ~{duration_minutes * operations_per_minute} operations")
        print(f"{'='*80}\n")

        end_time = time.time() + (duration_minutes * 60)
        interval = 60 / operations_per_minute  # Seconds between operations

        operation_count = 0

        while time.time() < end_time:
            # Select agent based on workload distribution
            agent_name = self._select_agent_by_distribution()

            # Select random scenario for this agent
            scenarios = REALISTIC_SCENARIOS.get(agent_name, [])
            if not scenarios:
                continue

            scenario = random.choice(scenarios)

            # Execute operation
            operation_count += 1
            print(
                f"[{operation_count:03d}] 🤖 {agent_name:25s} → {scenario['operation']:20s} ",
                end="",
            )

            start = time.time()
            result = await self.execute_agent_operation(
                agent_name, scenario["operation"], scenario["data"]
            )
            duration = time.time() - start

            # Print result
            status_icon = "✅" if result.get("status") == "success" else "❌"
            print(f"{status_icon} ({duration*1000:.1f}ms)")

            # Wait for next operation (with small random jitter)
            jitter = random.uniform(-0.2, 0.2) * interval
            await asyncio.sleep(max(0.1, interval + jitter))

        # Print final stats
        self._print_final_stats()

    def _select_agent_by_distribution(self) -> str:
        """Select agent based on realistic workload distribution."""
        rand = random.randint(1, 100)
        cumulative = 0

        for agent, percentage in AGENT_WORKLOAD_DISTRIBUTION.items():
            cumulative += percentage
            if rand <= cumulative:
                return agent

        # Fallback
        return "classifieragent"

    def _print_final_stats(self):
        """Print comprehensive test statistics."""
        duration = (datetime.now() - self.stats["start_time"]).total_seconds()

        print(f"\n{'='*80}")
        print(f"📈 TEST RESULTS SUMMARY")
        print(f"{'='*80}")
        print(f"⏱️  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"📊 Total Operations: {self.stats['total_operations']}")
        print(
            f"✅ Successful: {self.stats['successful_operations']} ({self.stats['successful_operations']/max(1,self.stats['total_operations'])*100:.1f}%)"
        )
        print(
            f"❌ Failed: {self.stats['failed_operations']} ({self.stats['failed_operations']/max(1,self.stats['total_operations'])*100:.1f}%)"
        )
        print(f"🚀 Throughput: {self.stats['total_operations']/(duration/60):.1f} ops/min")
        print(f"\n{'='*80}")
        print(f"📋 PER-AGENT BREAKDOWN")
        print(f"{'='*80}")

        for agent, stats in sorted(self.stats["operations_by_agent"].items()):
            success_rate = stats["success"] / max(1, stats["total"]) * 100
            print(
                f"  {agent:25s}: {stats['total']:4d} ops ({stats['success']:4d} ✅ / {stats['failed']:4d} ❌) - {success_rate:.1f}% success"
            )

        if self.stats["errors"]:
            print(f"\n{'='*80}")
            print(f"⚠️  ERRORS ENCOUNTERED ({len(self.stats['errors'])} total)")
            print(f"{'='*80}")

            # Show last 10 errors
            for error in self.stats["errors"][-10:]:
                print(
                    f"  [{error['timestamp']}] {error['agent']:20s} - {error['operation']:15s}: {error['error']}"
                )

        print(f"\n{'='*80}")
        print(f"✅ TEST COMPLETED")
        print(f"{'='*80}\n")

        # Save stats to file
        stats_file = f"load_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, "w") as f:
            json.dump(self.stats, f, indent=2, default=str)
        print(f"📁 Results saved to: {stats_file}\n")

    async def check_prometheus_metrics(self):
        """Query Prometheus for current agent metrics."""
        print(f"\n{'='*80}")
        print(f"📊 PROMETHEUS METRICS SNAPSHOT")
        print(f"{'='*80}")

        queries = {
            "Total Operations": "sum(agent_operations_total)",
            "Success Rate": 'sum(agent_operations_total{status="success"}) / sum(agent_operations_total) * 100',
            "Error Rate": 'sum(rate(agent_operations_total{status="error"}[5m]))',
            "Avg Execution Time": "avg(rate(agent_execution_duration_seconds_sum[5m]) / rate(agent_execution_duration_seconds_count[5m]))",
            "Active Agents": "active_agents_count",
        }

        try:
            for metric_name, query in queries.items():
                async with self.session.get(
                    f"{PROMETHEUS_URL}/api/v1/query", params={"query": query}
                ) as response:
                    result = await response.json()

                    if result.get("data", {}).get("result"):
                        value = result["data"]["result"][0]["value"][1]
                        print(f"  {metric_name:25s}: {value}")
                    else:
                        print(f"  {metric_name:25s}: No data")

        except Exception as e:
            print(f"  ⚠️  Error querying Prometheus: {e}")

        print(f"{'='*80}\n")


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="TwisterLab Realistic Agent Load Tester")
    parser.add_argument(
        "--duration", type=int, default=5, help="Test duration in minutes (default: 5)"
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=12,
        help="Operations per minute (default: 12, simulates 1 ticket every 5 seconds)",
    )
    parser.add_argument(
        "--check-metrics",
        action="store_true",
        help="Check Prometheus metrics before and after test",
    )

    args = parser.parse_args()

    async with AgentLoadTester() as tester:
        if args.check_metrics:
            print("\n🔍 PRE-TEST METRICS CHECK")
            await tester.check_prometheus_metrics()
            await asyncio.sleep(2)

        await tester.run_realistic_workload(
            duration_minutes=args.duration, operations_per_minute=args.rate
        )

        if args.check_metrics:
            print("\n🔍 POST-TEST METRICS CHECK")
            await asyncio.sleep(2)  # Wait for Prometheus scrape
            await tester.check_prometheus_metrics()


if __name__ == "__main__":
    asyncio.run(main())
