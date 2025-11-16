import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

import pytest

from agents.helpdesk.auto_resolver import HelpdeskResolverAgent
from agents.helpdesk.classifier import TicketClassifierAgent
from agents.helpdesk.desktop_commander import DesktopCommanderAgent
from agents.orchestrator.maestro import MaestroOrchestratorAgent


@pytest.fixture
def agents():
    """Fixture qui instancie et retourne tous les agents nécessaires aux tests."""
    return {
        "maestro": MaestroOrchestratorAgent(),
        "classifier": TicketClassifierAgent(),
        "resolver": HelpdeskResolverAgent(),
        "commander": DesktopCommanderAgent(),
    }


# Configuration du logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_agent_creation():
    """Test la création de tous les agents"""
    logger.info("Testing agent creation...")

    try:
        # Import des agents
        from agents.helpdesk.auto_resolver import HelpdeskResolverAgent
        from agents.helpdesk.classifier import TicketClassifierAgent
        from agents.helpdesk.desktop_commander import DesktopCommanderAgent
        from agents.orchestrator.maestro import MaestroOrchestratorAgent

        # Création des instances
        maestro = MaestroOrchestratorAgent()
        classifier = TicketClassifierAgent()
        resolver = HelpdeskResolverAgent()
        commander = DesktopCommanderAgent()

        logger.info("✅ All agents created successfully")

        return {
            "maestro": maestro,
            "classifier": classifier,
            "resolver": resolver,
            "commander": commander,
        }

    except Exception as e:
        logger.error(f"❌ Agent creation failed: {e}")
        raise


async def test_ticket_workflow(agents: Dict[str, Any]):
    """Test le workflow complet de traitement d'un ticket"""
    logger.info("Testing complete ticket workflow...")

    maestro = agents["maestro"]

    # Test ticket simple (devrait être résolu automatiquement)
    simple_ticket = {
        "ticket_id": "TICKET-001",
        "subject": "Password Reset Request",
        "description": "I forgot my password and need to reset it. Please help me access my account.",
        "requestor": "john.doe@company.com",
    }

    # Test ticket complexe (devrait être escaladé)
    complex_ticket = {
        "ticket_id": "TICKET-002",
        "subject": "System Crash - Multiple Applications Failing",
        "description": "Multiple applications are crashing simultaneously. Started after Windows update. Need immediate assistance.",
        "requestor": "jane.smith@company.com",
    }

    # Test ticket urgent (devrait être escaladé immédiatement)
    urgent_ticket = {
        "ticket_id": "TICKET-003",
        "subject": "URGENT: CEO Account Locked - Board Meeting in 30 Minutes",
        "description": "CEO's account is locked and he needs access immediately for an important board meeting.",
        "requestor": "security@company.com",
    }

    results = {}

    for ticket_name, ticket_data in [
        ("simple_password", simple_ticket),
        ("complex_crash", complex_ticket),
        ("urgent_ceo", urgent_ticket),
    ]:
        logger.info(f"Processing {ticket_name} ticket...")

        try:
            context = {"operation": "route_ticket", **ticket_data}
            result = await maestro.execute(f"Process {ticket_name} ticket", context)

            results[ticket_name] = result
            logger.info(f"✅ {ticket_name} result: {result['status']}")

        except Exception as e:
            logger.error(f"❌ {ticket_name} failed: {e}")
            results[ticket_name] = {"status": "error", "error": str(e)}

    return results


async def test_individual_agents(agents: Dict[str, Any]):
    """Test chaque agent individuellement"""
    logger.info("Testing individual agents...")

    results = {}

    # Test Classifier Agent
    try:
        classifier = agents["classifier"]
        context = {
            "ticket_id": "TEST-001",
            "subject": "Software Installation",
            "description": "Need to install Microsoft Office on my laptop",
        }
        result = await classifier.execute("Classify software installation ticket", context)
        results["classifier"] = result
        logger.info(f"✅ Classifier result: {result['status']}")
    except Exception as e:
        logger.error(f"❌ Classifier test failed: {e}")
        results["classifier"] = {"status": "error", "error": str(e)}

    # Test Resolver Agent
    try:
        resolver = agents["resolver"]
        context = {
            "ticket_id": "TEST-002",
            "category": "password",
            "priority": "high",
            "complexity": "simple",
        }
        result = await resolver.execute("Resolve password reset ticket", context)
        results["resolver"] = result
        logger.info(f"✅ Resolver result: {result['status']}")
    except Exception as e:
        logger.error(f"❌ Resolver test failed: {e}")
        results["resolver"] = {"status": "error", "error": str(e)}

    # Test Desktop Commander Agent
    try:
        commander = agents["commander"]
        context = {
            "device_id": "LAPTOP-001",
            "command": "systeminfo",
            "command_type": "execute_command",
        }
        result = await commander.execute("Execute system info command", context)
        results["commander"] = result
        logger.info(f"✅ Commander result: {result['status']}")
    except Exception as e:
        logger.error(f"❌ Commander test failed: {e}")
        results["commander"] = {"status": "error", "error": str(e)}

    return results


async def test_agent_status(agents: Dict[str, Any]):
    """Test la vérification du statut des agents"""
    logger.info("Testing agent status check...")

    try:
        maestro = agents["maestro"]
        context = {"operation": "get_agent_status", "include_health": True}
        result = await maestro.execute("Check agent status", context)

        logger.info(f"✅ Agent status check result: {result['status']}")
        return result

    except Exception as e:
        logger.error(f"❌ Agent status check failed: {e}")
        return {"status": "error", "error": str(e)}


async def test_load_balancing(agents: Dict[str, Any]):
    """Test l'équilibrage de charge"""
    logger.info("Testing load balancing...")

    try:
        maestro = agents["maestro"]
        context = {"operation": "rebalance_load", "strategy": "round_robin"}
        result = await maestro.execute("Rebalance agent load", context)

        logger.info(f"✅ Load balancing result: {result['status']}")
        return result

    except Exception as e:
        logger.error(f"❌ Load balancing test failed: {e}")
        return {"status": "error", "error": str(e)}


async def run_all_tests():
    """Exécute tous les tests"""
    logger.info("🚀 Starting TwisterLab Agent Integration Tests")
    logger.info("=" * 60)

    start_time = datetime.now()
    test_results = {
        "creation": False,
        "individual": False,
        "workflow": False,
        "status": False,
        "load_balancing": False,
        "errors": [],
    }

    try:
        # Test 1: Création des agents
        agents = await test_agent_creation()
        test_results["creation"] = True

        # Test 2: Tests individuels
        individual_results = await test_individual_agents(agents)
        test_results["individual"] = all(
            r.get("status") == "success" for r in individual_results.values()
        )

        # Test 3: Workflow complet
        workflow_results = await test_ticket_workflow(agents)
        test_results["workflow"] = all(
            r.get("status") in ["auto_resolved", "escalated_to_human"]
            for r in workflow_results.values()
        )

        # Test 4: Statut des agents
        status_result = await test_agent_status(agents)
        test_results["status"] = status_result.get("status") == "success"

        # Test 5: Équilibrage de charge
        lb_result = await test_load_balancing(agents)
        test_results["load_balancing"] = lb_result.get("status") == "success"

    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        test_results["errors"].append(str(e))

    # Rapport final
    end_time = datetime.now()
    duration = end_time - start_time

    logger.info("=" * 60)
    logger.info("📊 Test Results Summary")
    logger.info("=" * 60)

    total_tests = len([k for k in test_results.keys() if k != "errors"])
    passed_tests = sum(test_results.values()) - len(test_results["errors"])

    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {total_tests - passed_tests}")
    logger.info(f"Duration: {duration.total_seconds():.2f}s")

    if test_results["errors"]:
        logger.info("Errors:")
        for error in test_results["errors"]:
            logger.info(f"  - {error}")

    # Détails des résultats
    logger.info("\nDetailed Results:")
    for test_name, result in test_results.items():
        if test_name != "errors":
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {test_name}: {status}")

    # Métriques du maestro
    if "agents" in locals():
        try:
            metrics = agents["maestro"].get_metrics()
            logger.info(f"\nMaestro Metrics: {metrics}")
        except Exception:
            pass

    overall_success = all(test_results[k] for k in test_results.keys() if k not in ["errors"])

    if overall_success:
        logger.info("\n🎉 All tests passed! TwisterLab agents are ready for production.")
        return 0
    else:
        logger.error("\n💥 Some tests failed. Please check the logs above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
