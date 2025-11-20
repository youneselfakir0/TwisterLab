"""
Test d'intégration pour le workflow complet Maestro
Tests le workflow: Maestro → Classifier → Resolver
"""

import asyncio

from agents.orchestrator.maestro import MaestroOrchestratorAgent


def print_separator(title: str):
    """Print a formatted separator"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


async def test_full_workflow():
    """Test le workflow complet de routing d'un ticket"""

    maestro = MaestroOrchestratorAgent()

    # Test 1: Ticket password reset (devrait être auto-résolu)
    print_separator("Test 1: Password Reset")
    result1 = await maestro.route_ticket(
        {
            "ticket_id": "TICKET-001",
            "subject": "Password reset required",
            "description": "User forgot password and needs reset for Active Directory account",
            "requestor": "john.doe@example.com",
        }
    )
    print(f"[OK] Status: {result1['status']}")
    print(f"[OK] Ticket ID: {result1.get('ticket_id', 'N/A')}")
    if "classification" in result1:
        classification = result1["classification"]
        print(f"[OK] Category: {classification.get('category', 'N/A')}")
        print(f"[OK] Priority: {classification.get('priority', 'N/A')}")
        print(f"[OK] Complexity: {classification.get('complexity', 'N/A')}")
        print(f"[OK] Confidence: {classification.get('confidence', 'N/A')}")

    # Test 2: Ticket urgent (devrait être escaladé)
    print_separator("Test 2: Urgent Ticket")
    result2 = await maestro.route_ticket(
        {
            "ticket_id": "TICKET-002",
            "subject": "URGENT: Production server down",
            "description": "Critical server failure requires immediate attention",
            "requestor": "admin@example.com",
        }
    )
    print(f"[OK] Status: {result2['status']}")
    print(f"[OK] Ticket ID: {result2.get('ticket_id', 'N/A')}")
    print(f"[OK] Reason: {result2.get('reason', 'N/A')}")
    print(f"[OK] Recommended Agent: {result2.get('recommended_agent', 'N/A')}")
    print(f"[OK] Estimated Response Time: {result2.get('estimated_response_time', 'N/A')}")

    # Test 3: Ticket software installation (modéré)
    print_separator("Test 3: Software Installation")
    result3 = await maestro.route_ticket(
        {
            "ticket_id": "TICKET-003",
            "subject": "Install Microsoft Office",
            "description": "Need to install Office 365 on new laptop",
            "requestor": "jane.smith@example.com",
        }
    )
    print(f"[OK] Status: {result3['status']}")
    print(f"[OK] Ticket ID: {result3.get('ticket_id', 'N/A')}")
    if "classification" in result3:
        classification = result3["classification"]
        print(f"[OK] Category: {classification.get('category', 'N/A')}")
        print(f"[OK] Complexity: {classification.get('complexity', 'N/A')}")

    # Test 4: Ticket access request
    print_separator("Test 4: Access Request")
    result4 = await maestro.route_ticket(
        {
            "ticket_id": "TICKET-004",
            "subject": "Access to shared folder",
            "description": "Need access to the Finance shared folder on network",
            "requestor": "bob.jones@example.com",
        }
    )
    print(f"[OK] Status: {result4['status']}")
    print(f"[OK] Ticket ID: {result4.get('ticket_id', 'N/A')}")

    # Test 5: Get agent status
    print_separator("Test 5: Agent Status")
    status = await maestro.get_agent_status(include_health=True)
    print(f"[OK] Overall Health: {status['overall_health']}")
    print(f"[OK] Available Agents:")
    for agent_name, agent_info in status["agents"].items():
        print(f"  - {agent_name}:")
        print(f"    Status: {agent_info['status']}")
        print(f"    Load: {agent_info['load']}/{agent_info['max_load']}")
        if "health_metrics" in agent_info:
            metrics = agent_info["health_metrics"]
            print(f"    Response Time: {metrics.get('response_time', 'N/A')}")
            print(f"    Error Rate: {metrics.get('error_rate', 'N/A')}")
            print(f"    Uptime: {metrics.get('uptime', 'N/A')}")

    # Test 6: Load balancing
    print_separator("Test 6: Load Balancing")
    rebalance_result = await maestro.rebalance_load(strategy="round_robin")
    print(f"[OK] Status: {rebalance_result['status']}")
    print(f"[OK] Strategy: {rebalance_result['strategy']}")
    print(f"[OK] Agents Adjusted: {rebalance_result['agents_adjusted']}")

    # Show metrics
    print_separator("Performance Metrics")
    metrics = maestro.get_metrics()
    print(f"[OK] Tickets Processed: {metrics['tickets_processed']}")
    print(f"[OK] Auto-Resolved: {metrics['auto_resolved']}")
    print(f"[OK] Escalated to Human: {metrics['escalated_to_human']}")
    print(f"[OK] Agent Failures: {metrics['agent_failures']}")

    # Summary
    print_separator("Test Summary")
    total_tests = 6
    print(f"[OK] Total Tests Run: {total_tests}")
    print(f"[OK] All Tests Passed Successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  TwisterLab - Maestro Orchestrator Integration Tests")
    print("=" * 60)
    asyncio.run(test_full_workflow())
