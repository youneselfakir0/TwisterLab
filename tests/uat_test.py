"""
TwisterLab v1.0.0 - User Acceptance Testing (UAT)
Tests 10+ real-world helpdesk scenarios to validate production readiness.

Target: >90% success rate across all scenarios.
"""

import asyncio
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List

import aiohttp


@dataclass
class UATScenario:
    """User acceptance test scenario"""

    id: int
    name: str
    description: str
    category: str
    priority: str
    expected_sop: str
    expected_actions: List[str]
    success_criteria: str


@dataclass
class UATResult:
    """Results from UAT scenario execution"""

    scenario: UATScenario
    status: str  # "passed", "failed", "skipped"
    ticket_id: str
    classification: Dict[str, Any]
    resolution: Dict[str, Any]
    execution_time_sec: float
    error_message: str = ""


class UATTester:
    """User acceptance testing framework"""

    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.scenarios = self._define_scenarios()
        self.results: List[UATResult] = []

    def _define_scenarios(self) -> List[UATScenario]:
        """Define real-world helpdesk scenarios"""
        return [
            UATScenario(
                id=1,
                name="Outlook Connection Issues",
                description="User cannot connect to Outlook, emails not syncing",
                category="EMAIL_CLIENT",
                priority="high",
                expected_sop="SOP-EMAIL-001",
                expected_actions=[
                    "Check network connectivity",
                    "Verify email server settings",
                    "Clear Outlook cache",
                ],
                success_criteria="Outlook reconnected, emails syncing",
            ),
            UATScenario(
                id=2,
                name="WiFi Connection Problems",
                description="Laptop cannot connect to corporate WiFi network",
                category="NETWORK",
                priority="high",
                expected_sop="SOP-NETWORK-001",
                expected_actions=[
                    "Check WiFi adapter status",
                    "Forget and reconnect network",
                    "Update WiFi drivers",
                ],
                success_criteria="WiFi connected and stable",
            ),
            UATScenario(
                id=3,
                name="Printer Not Working",
                description="Network printer not responding, documents stuck in queue",
                category="HARDWARE",
                priority="medium",
                expected_sop="SOP-PRINTER-001",
                expected_actions=[
                    "Check printer power and network",
                    "Clear print queue",
                    "Restart print spooler service",
                ],
                success_criteria="Printer online, queue cleared",
            ),
            UATScenario(
                id=4,
                name="Password Reset Request",
                description="User forgot Active Directory password, cannot login",
                category="ACCESS",
                priority="high",
                expected_sop="SOP-PASSWORD-001",
                expected_actions=[
                    "Verify user identity",
                    "Reset AD password",
                    "Send temporary password securely",
                ],
                success_criteria="User can login with new password",
            ),
            UATScenario(
                id=5,
                name="VPN Connection Failure",
                description="Remote worker cannot connect to corporate VPN",
                category="NETWORK",
                priority="high",
                expected_sop="SOP-VPN-001",
                expected_actions=[
                    "Check VPN client version",
                    "Verify credentials",
                    "Reset VPN connection",
                ],
                success_criteria="VPN connected, can access resources",
            ),
            UATScenario(
                id=6,
                name="Software Installation Request",
                description="User needs Microsoft Teams installed on new laptop",
                category="SOFTWARE",
                priority="medium",
                expected_sop="SOP-SOFTWARE-001",
                expected_actions=[
                    "Verify license availability",
                    "Download Teams installer",
                    "Install and configure Teams",
                ],
                success_criteria="Teams installed and working",
            ),
            UATScenario(
                id=7,
                name="Slow Computer Performance",
                description="Desktop running very slowly, applications freezing",
                category="PERFORMANCE",
                priority="medium",
                expected_sop="SOP-PERFORMANCE-001",
                expected_actions=[
                    "Check CPU and memory usage",
                    "Close unnecessary processes",
                    "Run disk cleanup",
                ],
                success_criteria="Computer responsive, apps running smoothly",
            ),
            UATScenario(
                id=8,
                name="File Share Access Denied",
                description="User cannot access departmental file share",
                category="ACCESS",
                priority="medium",
                expected_sop="SOP-FILE-SHARE-001",
                expected_actions=[
                    "Verify user permissions",
                    "Check security group membership",
                    "Grant appropriate access",
                ],
                success_criteria="User can read/write to file share",
            ),
            UATScenario(
                id=9,
                name="Blue Screen of Death (BSOD)",
                description="Desktop shows BSOD on startup, cannot boot Windows",
                category="HARDWARE",
                priority="critical",
                expected_sop="SOP-BSOD-001",
                expected_actions=[
                    "Analyze crash dump",
                    "Check hardware diagnostics",
                    "Boot in safe mode, repair Windows",
                ],
                success_criteria="Windows boots normally",
            ),
            UATScenario(
                id=10,
                name="Email Attachment Blocked",
                description="User cannot send email with .exe attachment",
                category="EMAIL_CLIENT",
                priority="low",
                expected_sop="SOP-EMAIL-ATTACHMENT-001",
                expected_actions=[
                    "Explain attachment policy",
                    "Suggest alternative (zip, cloud storage)",
                    "Request exception if justified",
                ],
                success_criteria="User understands policy, uses alternative",
            ),
            UATScenario(
                id=11,
                name="Malware Detection Alert",
                description="Antivirus detected malware, system quarantined files",
                category="SECURITY",
                priority="critical",
                expected_sop="SOP-MALWARE-001",
                expected_actions=[
                    "Isolate infected machine",
                    "Run full antivirus scan",
                    "Remove malware, verify clean",
                ],
                success_criteria="System clean, no malware detected",
            ),
            UATScenario(
                id=12,
                name="Microsoft Office Activation",
                description="Office shows unlicensed product, features disabled",
                category="SOFTWARE",
                priority="medium",
                expected_sop="SOP-OFFICE-LICENSE-001",
                expected_actions=[
                    "Check Office license status",
                    "Re-activate with product key",
                    "Verify activation successful",
                ],
                success_criteria="Office fully activated and functional",
            ),
        ]

    async def create_ticket(self, session: aiohttp.ClientSession, scenario: UATScenario) -> str:
        """Create ticket for scenario"""
        ticket_data = {
            "subject": scenario.name,
            "description": scenario.description,
            "priority": scenario.priority,
            "source": "uat_test",
        }

        async with session.post(
            f"{self.base_url}/api/v1/tickets",
            json=ticket_data,
            timeout=aiohttp.ClientTimeout(total=10),
        ) as response:
            if response.status in [200, 201]:
                data = await response.json()
                return data.get("id", "")
            else:
                raise Exception(f"Failed to create ticket: HTTP {response.status}")

    async def get_ticket_status(
        self, session: aiohttp.ClientSession, ticket_id: str
    ) -> Dict[str, Any]:
        """Get ticket classification and resolution status"""
        async with session.get(
            f"{self.base_url}/api/v1/tickets/{ticket_id}", timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to get ticket: HTTP {response.status}")

    async def run_scenario(
        self, session: aiohttp.ClientSession, scenario: UATScenario
    ) -> UATResult:
        """Execute single UAT scenario"""
        print(f"\n{'='*60}")
        print(f"Scenario {scenario.id}: {scenario.name}")
        print(f"{'='*60}")
        print(f"Description: {scenario.description}")
        print(f"Category: {scenario.category}")
        print(f"Priority: {scenario.priority}")

        start_time = asyncio.get_event_loop().time()

        try:
            # Step 1: Create ticket
            print("\n[1/3] Creating ticket...")
            ticket_id = await self.create_ticket(session, scenario)
            print(f"  ✅ Ticket created: {ticket_id}")

            # Step 2: Wait for classification
            print("\n[2/3] Waiting for classification...")
            await asyncio.sleep(3)  # Wait for agents to process

            ticket_status = await self.get_ticket_status(session, ticket_id)
            classification = ticket_status.get("classification", {})
            print(f"  Category: {classification.get('category', 'N/A')}")
            print(f"  Urgency: {classification.get('urgency', 'N/A')}")
            print(f"  Complexity: {classification.get('complexity', 'N/A')}")

            # Step 3: Check resolution
            print("\n[3/3] Checking resolution...")
            await asyncio.sleep(5)  # Wait for resolution

            ticket_status = await self.get_ticket_status(session, ticket_id)
            resolution = ticket_status.get("resolution", {})
            status = ticket_status.get("status", "CREATED")

            print(f"  Status: {status}")
            print(f"  SOP: {resolution.get('sop_id', 'N/A')}")
            print(f"  Actions: {resolution.get('actions_executed', 0)}")

            # Validate scenario
            elapsed = asyncio.get_event_loop().time() - start_time

            # Check if category matches
            category_match = classification.get("category") == scenario.category

            # Check if resolved
            is_resolved = status in ["RESOLVED", "CLOSED"]

            if category_match and is_resolved:
                print(f"\n✅ PASSED - Scenario completed successfully")
                result_status = "passed"
                error_msg = ""
            else:
                print(f"\n⚠️  PARTIAL - Scenario incomplete")
                result_status = "failed"
                error_msg = f"Category match: {category_match}, Resolved: {is_resolved}"

            return UATResult(
                scenario=scenario,
                status=result_status,
                ticket_id=ticket_id,
                classification=classification,
                resolution=resolution,
                execution_time_sec=elapsed,
                error_message=error_msg,
            )

        except Exception as e:
            elapsed = asyncio.get_event_loop().time() - start_time
            print(f"\n❌ FAILED - {e}")

            return UATResult(
                scenario=scenario,
                status="failed",
                ticket_id="",
                classification={},
                resolution={},
                execution_time_sec=elapsed,
                error_message=str(e),
            )

    async def run_all_scenarios(self):
        """Execute all UAT scenarios"""
        print(f"\n{'='*60}")
        print("  TwisterLab v1.0.0 - User Acceptance Testing")
        print(f"{'='*60}\n")
        print(f"Total Scenarios: {len(self.scenarios)}")
        print(f"Target Success Rate: >90%\n")

        input("Press ENTER to start UAT (ensure staging environment running)...")

        async with aiohttp.ClientSession() as session:
            for scenario in self.scenarios:
                result = await self.run_scenario(session, scenario)
                self.results.append(result)
                await asyncio.sleep(2)  # Cool-down between scenarios

        self.print_summary()
        self.save_results()

    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print("  UAT SUMMARY")
        print(f"{'='*60}\n")

        passed = sum(1 for r in self.results if r.status == "passed")
        failed = sum(1 for r in self.results if r.status == "failed")
        total = len(self.results)

        success_rate = (passed / total * 100) if total > 0 else 0

        print(f"Total Scenarios:     {total}")
        print(f"Passed:              {passed} ({passed/total*100:.1f}%)")
        print(f"Failed:              {failed} ({failed/total*100:.1f}%)")
        print(f"Success Rate:        {success_rate:.1f}%")

        print(f"\n{'='*60}")
        if success_rate >= 90:
            print("  ✅ UAT PASSED - Production ready (>90% success)")
        elif success_rate >= 75:
            print("  ⚠️  UAT WARNING - Some issues (75-90% success)")
        else:
            print("  ❌ UAT FAILED - Critical issues (<75% success)")
        print(f"{'='*60}\n")

        # Failed scenarios
        if failed > 0:
            print("Failed Scenarios:")
            for result in self.results:
                if result.status == "failed":
                    print(f"  - Scenario {result.scenario.id}: {result.scenario.name}")
                    print(f"    Error: {result.error_message}")

    def save_results(self):
        """Save UAT results to JSON"""
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "total_scenarios": len(self.results),
            "passed": sum(1 for r in self.results if r.status == "passed"),
            "failed": sum(1 for r in self.results if r.status == "failed"),
            "scenarios": [
                {
                    "id": r.scenario.id,
                    "name": r.scenario.name,
                    "status": r.status,
                    "ticket_id": r.ticket_id,
                    "execution_time": r.execution_time_sec,
                    "error": r.error_message,
                }
                for r in self.results
            ],
        }

        with open("uat_results.json", "w") as f:
            json.dump(results_data, f, indent=2)

        print(f"Results saved: uat_results.json")


async def main():
    tester = UATTester(base_url="http://localhost:8001")
    await tester.run_all_scenarios()


if __name__ == "__main__":
    asyncio.run(main())
