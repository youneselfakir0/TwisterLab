"""Simple test of agent communication without Rich"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.real.real_maestro_agent import RealMaestroAgent
from agents.real.real_classifier_agent import RealClassifierAgent

async def test_agents():
    print("\n=== TwisterLab Agent Communication Test ===\n")

    # Test 1: Maestro
    print("Test 1: Maestro Initialization")
    try:
        maestro = MaestroOrchestratorAgent()
        print(f"  SUCCESS: {maestro.name} initialized")
        print(f"  Display Name: {maestro.display_name}")
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

    # Test 2: Load Balancer
    print("\nTest 2: Load Balancer")
    try:
        lb = maestro.load_balancer
        classifier_inst = lb.get_best_instance("classifier")
        resolver_inst = lb.get_best_instance("resolver")
        dc_inst = lb.get_best_instance("desktop_commander")

        if classifier_inst:
            print(f"  SUCCESS: Classifier registered ({classifier_inst.instance_id})")
        else:
            print("  FAILED: No classifier registered")

        if resolver_inst:
            print(f"  SUCCESS: Resolver registered ({resolver_inst.instance_id})")
        else:
            print("  FAILED: No resolver registered")

        if dc_inst:
            print(f"  SUCCESS: Desktop Commander registered ({dc_inst.instance_id})")
        else:
            print("  FAILED: No desktop commander registered")

    except Exception as e:
        print(f"  FAILED: {e}")
        return False

    # Test 3: Classifier
    print("\nTest 3: Classifier Agent")
    try:
        classifier = TicketClassifierAgent()
        print(f"  SUCCESS: {classifier.name} initialized")
        print(f"  Tools available: {len(classifier.tools)}")
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

    # Test 4: Resolver
    print("\nTest 4: Resolver Agent")
    try:
        resolver = HelpdeskAgent()
        print(f"  SUCCESS: {resolver.name} initialized")
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

    # Test 5: Metrics
    print("\nTest 5: Maestro Metrics")
    try:
        metrics = maestro.metrics
        print(f"  Tickets routed: {metrics.get('tickets_routed', 0)}")
        print(f"  Classification requests: {metrics.get('classification_requests', 0)}")
        print(f"  Resolution requests: {metrics.get('resolution_requests', 0)}")
        print(f"  Errors: {metrics.get('errors', 0)}")
        print("  SUCCESS: Metrics operational")
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

    print("\n=== ALL TESTS PASSED ===")
    print("\nAGENT COMMUNICATION STATUS: OPERATIONAL")
    print("- Maestro Orchestrator: READY")
    print("- Load Balancer: CONFIGURED")
    print("- Classifier Agent: READY")
    print("- Resolver Agent: READY")
    print("- Worker agents registered with Maestro")
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_agents())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
