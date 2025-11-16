"""
Production API Testing Script for TwisterLab Autonomous Agents
Tests all endpoints and agent operations in production environment
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List

import httpx


class ProductionAPITester:
    """Test production APIs and autonomous agents."""

    def __init__(self, base_url: str = "http://api.twisterlab.local"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = []

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive API tests."""
        print("🧪 Starting Production API Tests...")

        tests = [
            self.test_health_endpoint,
            self.test_autonomous_status,
            self.test_autonomous_agents,
            self.test_monitoring_agent,
            self.test_backup_agent,
            self.test_sync_agent,
            self.test_emergency_response,
            self.test_scheduled_tasks,
        ]

        for test in tests:
            try:
                result = await test()
                self.results.append(result)
                status = "✅ PASS" if result["status"] == "success" else "❌ FAIL"
                print(f"{status}: {result['test_name']}")
            except Exception as e:
                error_result = {
                    "test_name": test.__name__,
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
                self.results.append(error_result)
                print(f"❌ ERROR: {test.__name__} - {str(e)}")

        summary = self._generate_summary()
        await self.client.aclose()
        return summary

    async def test_health_endpoint(self) -> Dict[str, Any]:
        """Test basic health endpoint."""
        response = await self.client.get(f"{self.base_url}/health")

        return {
            "test_name": "health_endpoint",
            "status": "success" if response.status_code == 200 else "failed",
            "response_code": response.status_code,
            "response_data": response.json() if response.status_code == 200 else None,
            "timestamp": datetime.now().isoformat(),
        }

    async def test_autonomous_status(self) -> Dict[str, Any]:
        """Test autonomous agents status endpoint."""
        response = await self.client.get(f"{self.base_url}/api/v1/autonomous/status")

        if response.status_code == 200:
            data = response.json()
            agents_count = data.get("agents", 0)
            tasks_count = data.get("scheduled_tasks", 0)

            return {
                "test_name": "autonomous_status",
                "status": "success",
                "agents_count": agents_count,
                "scheduled_tasks": tasks_count,
                "response_data": data,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "test_name": "autonomous_status",
                "status": "failed",
                "response_code": response.status_code,
                "timestamp": datetime.now().isoformat(),
            }

    async def test_autonomous_agents(self) -> Dict[str, Any]:
        """Test autonomous agents list endpoint."""
        response = await self.client.get(f"{self.base_url}/api/v1/autonomous/agents")

        if response.status_code == 200:
            data = response.json()
            agents = data.get("agents", [])

            return {
                "test_name": "autonomous_agents",
                "status": "success",
                "agents_listed": len(agents),
                "agent_names": [agent["name"] for agent in agents],
                "response_data": data,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "test_name": "autonomous_agents",
                "status": "failed",
                "response_code": response.status_code,
                "timestamp": datetime.now().isoformat(),
            }

    async def test_monitoring_agent(self) -> Dict[str, Any]:
        """Test MonitoringAgent operations."""
        payload = {"operation": "check_system_health", "context": {"detailed": True}}

        response = await self.client.post(
            f"{self.base_url}/api/v1/autonomous/agents/monitoring/execute",
            json=payload,
            headers={"Content-Type": "application/json"},
        )

        return {
            "test_name": "monitoring_agent",
            "status": "success" if response.status_code == 200 else "failed",
            "response_code": response.status_code,
            "response_data": response.json() if response.status_code == 200 else None,
            "timestamp": datetime.now().isoformat(),
        }

    async def test_backup_agent(self) -> Dict[str, Any]:
        """Test BackupAgent operations."""
        payload = {
            "operation": "integrity_check",
            "context": {"check_type": "database"},
        }

        response = await self.client.post(
            f"{self.base_url}/api/v1/autonomous/agents/backup/execute",
            json=payload,
            headers={"Content-Type": "application/json"},
        )

        return {
            "test_name": "backup_agent",
            "status": "success" if response.status_code == 200 else "failed",
            "response_code": response.status_code,
            "response_data": response.json() if response.status_code == 200 else None,
            "timestamp": datetime.now().isoformat(),
        }

    async def test_sync_agent(self) -> Dict[str, Any]:
        """Test SyncAgent operations."""
        payload = {"operation": "consistency_check", "context": {"check_type": "cache"}}

        response = await self.client.post(
            f"{self.base_url}/api/v1/autonomous/agents/sync/execute",
            json=payload,
            headers={"Content-Type": "application/json"},
        )

        return {
            "test_name": "sync_agent",
            "status": "success" if response.status_code == 200 else "failed",
            "response_code": response.status_code,
            "response_data": response.json() if response.status_code == 200 else None,
            "timestamp": datetime.now().isoformat(),
        }

    async def test_emergency_response(self) -> Dict[str, Any]:
        """Test emergency response endpoints."""
        # Test emergency status (not actual emergency)
        response = await self.client.get(f"{self.base_url}/api/v1/autonomous/emergency/status")

        return {
            "test_name": "emergency_response",
            "status": "success" if response.status_code in [200, 404] else "failed",
            "response_code": response.status_code,
            "response_data": response.json() if response.status_code == 200 else None,
            "timestamp": datetime.now().isoformat(),
        }

    async def test_scheduled_tasks(self) -> Dict[str, Any]:
        """Test scheduled tasks endpoint."""
        response = await self.client.get(f"{self.base_url}/api/v1/autonomous/schedule/tasks")

        if response.status_code == 200:
            data = response.json()
            tasks = data.get("tasks", [])

            return {
                "test_name": "scheduled_tasks",
                "status": "success",
                "tasks_count": len(tasks),
                "task_names": [task.get("name", "unknown") for task in tasks],
                "response_data": data,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "test_name": "scheduled_tasks",
                "status": "failed",
                "response_code": response.status_code,
                "timestamp": datetime.now().isoformat(),
            }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate test summary."""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["status"] == "success"])
        failed_tests = total_tests - passed_tests

        return {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (
                    f"{(passed_tests / total_tests) * 100:.1f}%" if total_tests > 0 else "0%"
                ),
            },
            "results": self.results,
            "timestamp": datetime.now().isoformat(),
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        failed_tests = [r for r in self.results if r["status"] != "success"]
        if failed_tests:
            recommendations.append(
                f"Address {len(failed_tests)} failed tests before production use"
            )

        # Check for specific issues
        for result in self.results:
            if result["test_name"] == "autonomous_status" and result["status"] == "success":
                agents_count = result.get("agents_count", 0)
                if agents_count < 3:
                    recommendations.append(f"Only {agents_count} agents registered, expected 7")

            if result["test_name"] == "scheduled_tasks" and result["status"] == "success":
                tasks_count = result.get("tasks_count", 0)
                if tasks_count < 6:
                    recommendations.append(f"Only {tasks_count} scheduled tasks, expected 6")

        if not recommendations:
            recommendations.append("All systems operational - proceed with confidence")

        return recommendations


async def main():
    """Main test execution."""
    tester = ProductionAPITester()
    results = await tester.run_all_tests()

    # Save results
    with open("production_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    # Print summary
    summary = results["summary"]
    print(f"\n{'=' * 50}")
    print("PRODUCTION API TEST RESULTS")
    print(f"{'=' * 50}")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']}")
    print("\nRecommendations:")
    for rec in results["recommendations"]:
        print(f"• {rec}")

    print("\nDetailed results saved to: production_test_results.json")


if __name__ == "__main__":
    asyncio.run(main())
