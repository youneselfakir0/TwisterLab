#!/usr/bin/env python3
"""
TwisterLab Autonomous Agents Monitoring Script
Monitors autonomous agents health, performance, and generates reports.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AutonomousAgentsMonitor:
    """Monitors autonomous agents health and performance."""

    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.reports_dir = Path("reports/autonomous")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        try:
            url = f"{self.base_url}/autonomous/health"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
        return {"status": "unhealthy", "error": "Connection failed"}

    async def get_agent_status(self) -> Dict[str, Any]:
        """Get detailed agent status."""
        try:
            url = f"{self.base_url}/autonomous/agents/status"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            logger.error(f"Failed to get agent status: {e}")
        return {"agents": [], "error": "Connection failed"}

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics."""
        try:
            url = f"{self.base_url}/autonomous/metrics"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
        return {"metrics": {}, "error": "Connection failed"}

    async def get_scheduled_tasks(self) -> Dict[str, Any]:
        """Get scheduled tasks status."""
        try:
            url = f"{self.base_url}/autonomous/schedule/tasks"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            logger.error(f"Failed to get scheduled tasks: {e}")
        return {"tasks": [], "error": "Connection failed"}

    def analyze_health(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze system health data."""
        analysis = {"overall_status": "unknown", "issues": [], "recommendations": []}

        if health_data.get("status") == "healthy":
            analysis["overall_status"] = "healthy"
        else:
            analysis["overall_status"] = "unhealthy"
            analysis["issues"].append("System health check failed")
            analysis["recommendations"].append("Check autonomous agents service logs")

        # Check uptime
        uptime = health_data.get("uptime_seconds", 0)
        if uptime < 300:  # Less than 5 minutes
            analysis["issues"].append("System recently restarted")
            analysis["recommendations"].append("Monitor for stability issues")

        return analysis

    def analyze_agents(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze agent status data."""
        analysis = {
            "total_agents": 0,
            "active_agents": 0,
            "inactive_agents": 0,
            "issues": [],
            "recommendations": [],
        }

        agents = agent_data.get("agents", [])
        analysis["total_agents"] = len(agents)

        for agent in agents:
            if agent.get("status") == "active":
                analysis["active_agents"] += 1
            else:
                analysis["inactive_agents"] += 1
                analysis["issues"].append(f"Agent {agent.get('name')} is inactive")
                analysis["recommendations"].append(
                    f"Check {agent.get('name')} configuration and logs"
                )

        # Check for expected agents
        expected_agents = ["MonitoringAgent", "BackupAgent", "SyncAgent"]
        active_agent_names = [
            a.get("name") for a in agents if a.get("status") == "active"
        ]

        for expected in expected_agents:
            if expected not in active_agent_names:
                analysis["issues"].append(
                    f"Expected agent {expected} not found or inactive"
                )
                analysis["recommendations"].append(
                    f"Verify {expected} deployment and configuration"
                )

        return analysis

    def analyze_metrics(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze system metrics."""
        analysis = {
            "performance_status": "unknown",
            "issues": [],
            "recommendations": [],
        }

        metrics = metrics_data.get("metrics", {})

        # Check memory usage
        memory_usage = metrics.get("memory_percent", 0)
        if memory_usage > 90:
            analysis["issues"].append(f"High memory usage: {memory_usage}%")
            analysis["recommendations"].append(
                "Monitor memory consumption and consider optimization"
            )
            analysis["performance_status"] = "critical"
        elif memory_usage > 75:
            analysis["issues"].append(f"Elevated memory usage: {memory_usage}%")
            analysis["recommendations"].append("Monitor memory trends")
            analysis["performance_status"] = "warning"
        else:
            analysis["performance_status"] = "good"

        # Check CPU usage
        cpu_usage = metrics.get("cpu_percent", 0)
        if cpu_usage > 90:
            analysis["issues"].append(f"High CPU usage: {cpu_usage}%")
            analysis["recommendations"].append("Investigate CPU-intensive operations")
        elif cpu_usage > 75:
            analysis["issues"].append(f"Elevated CPU usage: {cpu_usage}%")
            analysis["recommendations"].append("Monitor CPU trends")

        # Check task queue
        queued_tasks = metrics.get("queued_tasks", 0)
        if queued_tasks > 10:
            analysis["issues"].append(f"High task queue: {queued_tasks} tasks")
            analysis["recommendations"].append("Check agent processing capacity")

        return analysis

    def analyze_tasks(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze scheduled tasks."""
        analysis = {
            "total_tasks": 0,
            "overdue_tasks": 0,
            "issues": [],
            "recommendations": [],
        }

        tasks = task_data.get("tasks", [])
        analysis["total_tasks"] = len(tasks)

        now = datetime.now()
        for task in tasks:
            next_run = task.get("next_run")
            if next_run:
                try:
                    next_run_dt = datetime.fromisoformat(
                        next_run.replace("Z", "+00:00")
                    )
                    if next_run_dt < now:
                        analysis["overdue_tasks"] += 1
                except Exception:
                    pass

        if analysis["overdue_tasks"] > 0:
            analysis["issues"].append(
                f"{analysis['overdue_tasks']} scheduled tasks are overdue"
            )
            analysis["recommendations"].append(
                "Review task scheduling and agent performance"
            )

        return analysis

    async def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report."""
        logger.info("Generating autonomous agents monitoring report...")

        # Collect all data
        health_data = await self.get_system_health()
        agent_data = await self.get_agent_status()
        metrics_data = await self.get_system_metrics()
        task_data = await self.get_scheduled_tasks()

        # Analyze data
        health_analysis = self.analyze_health(health_data)
        agent_analysis = self.analyze_agents(agent_data)
        metrics_analysis = self.analyze_metrics(metrics_data)
        task_analysis = self.analyze_tasks(task_data)

        # Compile report
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_health": health_data,
            "agent_status": agent_data,
            "system_metrics": metrics_data,
            "scheduled_tasks": task_data,
            "analysis": {
                "health": health_analysis,
                "agents": agent_analysis,
                "metrics": metrics_analysis,
                "tasks": task_analysis,
            },
            "summary": {
                "overall_status": self._calculate_overall_status(
                    [health_analysis, agent_analysis, metrics_analysis, task_analysis]
                ),
                "total_issues": sum(
                    len(a.get("issues", []))
                    for a in [
                        health_analysis,
                        agent_analysis,
                        metrics_analysis,
                        task_analysis,
                    ]
                ),
                "total_recommendations": sum(
                    len(a.get("recommendations", []))
                    for a in [
                        health_analysis,
                        agent_analysis,
                        metrics_analysis,
                        task_analysis,
                    ]
                ),
            },
        }

        return report

    def _calculate_overall_status(self, analyses: List[Dict[str, Any]]) -> str:
        """Calculate overall system status."""
        statuses = []
        for analysis in analyses:
            if "overall_status" in analysis:
                statuses.append(analysis["overall_status"])
            elif "performance_status" in analysis:
                statuses.append(analysis["performance_status"])

        if "critical" in statuses:
            return "critical"
        elif "unhealthy" in statuses or "unknown" in statuses:
            return "warning"
        elif "warning" in statuses:
            return "warning"
        else:
            return "healthy"

    async def save_report(
        self, report: Dict[str, Any], filename: Optional[str] = None
    ) -> str:
        """Save report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"autonomous_monitoring_report_{timestamp}.json"

        filepath = self.reports_dir / filename

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Report saved to {filepath}")
        return str(filepath)

    async def print_report(self, report: Dict[str, Any]):
        """Print human-readable report."""
        print("\n=== TwisterLab Autonomous Agents Monitoring Report ===")
        print(f"Generated: {report['timestamp']}")

        summary = report["summary"]
        print(f"\nOverall Status: {summary['overall_status'].upper()}")
        print(f"Total Issues: {summary['total_issues']}")
        print(f"Total Recommendations: {summary['total_recommendations']}")

        # Health summary
        health = report["analysis"]["health"]
        print(f"\nSystem Health: {health['overall_status'].upper()}")

        # Agent summary
        agents = report["analysis"]["agents"]
        print(f"\nAgents: {agents['active_agents']}/{agents['total_agents']} active")

        # Metrics summary
        metrics = report["analysis"]["metrics"]
        print(f"\nPerformance: {metrics['performance_status'].upper()}")

        # Issues and recommendations
        all_issues = []
        all_recommendations = []

        for analysis in report["analysis"].values():
            all_issues.extend(analysis.get("issues", []))
            all_recommendations.extend(analysis.get("recommendations", []))

        if all_issues:
            print("\nIssues:")
            for issue in all_issues:
                print(f"  - {issue}")

        if all_recommendations:
            print("\nRecommendations:")
            for rec in all_recommendations:
                print(f"  - {rec}")

    async def monitor_continuous(self, interval: int = 300):
        """Continuous monitoring with periodic reports."""
        logger.info(f"Starting continuous monitoring (interval: {interval}s)")

        try:
            while True:
                report = await self.generate_report()
                await self.print_report(report)

                # Save report if there are issues
                if report["summary"]["total_issues"] > 0:
                    await self.save_report(report)

                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")


async def main():
    """Main monitoring function."""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor autonomous agents")
    parser.add_argument(
        "--url",
        default="http://localhost:8001",
        help="Base URL for autonomous agents API",
    )
    parser.add_argument(
        "--continuous", action="store_true", help="Run continuous monitoring"
    )
    parser.add_argument(
        "--interval", type=int, default=300, help="Monitoring interval in seconds"
    )
    parser.add_argument("--save", action="store_true", help="Save report to file")
    parser.add_argument("--quiet", action="store_true", help="Suppress console output")

    args = parser.parse_args()

    async with AutonomousAgentsMonitor(args.url) as monitor:
        try:
            if args.continuous:
                await monitor.monitor_continuous(args.interval)
            else:
                report = await monitor.generate_report()

                if not args.quiet:
                    await monitor.print_report(report)

                if args.save:
                    filepath = await monitor.save_report(report)
                    print(f"\nReport saved: {filepath}")

        except Exception as e:
            logger.error(f"Monitoring failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
