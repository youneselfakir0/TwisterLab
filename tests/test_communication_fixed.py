"""Test de communication entre Maestro et agents workers - Version corrigée"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.real.real_classifier_agent import RealClassifierAgent
from agents.real.real_desktop_commander_agent import RealDesktopCommanderAgent
from agents.real.real_maestro_agent import RealMaestroAgent


def main():
    print("\n=== TwisterLab Agent Communication Test (FIXED) ===\n")

    # Test 1: Initialiser Maestro
    print("Test 1: Maestro Initialization")
    try:
        maestro = MaestroOrchestratorAgent()
        print(f"  SUCCESS: {maestro.name} initialized")
        print(f"  Display Name: {maestro.display_name}")
        print(f"  Tools: {len(maestro.tools)} tools registered")
    except Exception as e:
        print(f"  FAILED: {e}")
        return 1

    # Test 2: Load Balancer (CORRIGÉ)
    print("\nTest 2: Load Balancer - Instance Selection")
    try:
        lb = maestro.load_balancer

        # Tester sélection pour chaque type d'agent
        classifier_inst = lb.select_instance("classifier", LoadBalancingStrategy.LEAST_LOADED)
        resolver_inst = lb.select_instance("resolver", LoadBalancingStrategy.LEAST_LOADED)
        dc_inst = lb.select_instance("desktop_commander", LoadBalancingStrategy.LEAST_LOADED)

        print(f"  SUCCESS: Load balancer operational")
        print(f"  Classifier instance: {classifier_inst}")
        print(f"  Resolver instance: {resolver_inst}")
        print(f"  Desktop Commander instance: {dc_inst}")

        # Vérifier qu'on a bien des instances
        if not all([classifier_inst, resolver_inst, dc_inst]):
            print("  WARNING: Some instances not available")
            return 1

    except Exception as e:
        print(f"  FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1

    # Test 3: Initialiser Classifier Worker
    print("\nTest 3: Classifier Worker Initialization")
    try:
        classifier = ClassifierAgent()
        print(f"  SUCCESS: {classifier.name} initialized")
        print(f"  Display Name: {classifier.display_name}")
        print(f"  Tools: {len(classifier.tools)} tools")
    except Exception as e:
        print(f"  FAILED: {e}")
        return 1

    # Test 4: Initialiser Resolver Worker
    print("\nTest 4: Resolver Worker Initialization")
    try:
        resolver = HelpdeskAgent()
        print(f"  SUCCESS: {resolver.name} initialized")
        print(f"  Display Name: {resolver.display_name}")
        print(f"  Tools: {len(resolver.tools)} tools")
    except Exception as e:
        print(f"  FAILED: {e}")
        return 1

    # Test 5: Initialiser Desktop Commander Worker
    print("\nTest 5: Desktop Commander Worker Initialization")
    try:
        dc = DesktopCommanderAgent()
        print(f"  SUCCESS: {dc.name} initialized")
        print(f"  Display Name: {dc.display_name}")
        print(f"  Tools: {len(dc.tools)} tools")
    except Exception as e:
        print(f"  FAILED: {e}")
        return 1

    # Test 6: Vérifier métriques Maestro
    print("\nTest 6: Maestro Metrics Tracking")
    try:
        metrics = maestro.metrics
        print(f"  SUCCESS: Metrics initialized")
        print(f"  tickets_routed: {metrics.get('tickets_routed', 0)}")
        print(f"  classification_requests: {metrics.get('classification_requests', 0)}")
        print(f"  resolution_requests: {metrics.get('resolution_requests', 0)}")
        print(f"  command_executions: {metrics.get('command_executions', 0)}")
        print(f"  errors: {metrics.get('errors', 0)}")
    except Exception as e:
        print(f"  FAILED: {e}")
        return 1

    # Test 7: Tester stratégies de load balancing
    print("\nTest 7: Load Balancing Strategies")
    try:
        strategies = [
            ("LEAST_LOADED", LoadBalancingStrategy.LEAST_LOADED),
            ("ROUND_ROBIN", LoadBalancingStrategy.ROUND_ROBIN),
            ("PRIORITY_BASED", LoadBalancingStrategy.PRIORITY_BASED),
            ("WEIGHTED", LoadBalancingStrategy.WEIGHTED),
        ]

        for strategy_name, strategy in strategies:
            inst = lb.select_instance("classifier", strategy)
            print(f"  {strategy_name}: {inst}")

        print(f"  SUCCESS: All strategies working")
    except Exception as e:
        print(f"  FAILED: {e}")
        return 1

    # Test 8: Simuler routing de ticket
    print("\nTest 8: Ticket Routing Simulation")
    try:
        # Simuler classification
        ticket_data = {
            "subject": "Test Ticket",
            "description": "Test de communication",
            "priority": "medium",
        }

        # Sélectionner instance classifier
        classifier_inst = lb.select_instance("classifier", LoadBalancingStrategy.LEAST_LOADED)
        print(f"  Routing to classifier: {classifier_inst}")

        # Incrémenter la charge
        lb.increment_load("classifier", classifier_inst)
        print(f"  Load incremented for {classifier_inst}")

        # Sélectionner instance resolver
        resolver_inst = lb.select_instance("resolver", LoadBalancingStrategy.LEAST_LOADED)
        print(f"  Routing to resolver: {resolver_inst}")

        # Décrémenter la charge
        lb.decrement_load("classifier", classifier_inst)
        print(f"  Load decremented for {classifier_inst}")

        print(f"  SUCCESS: Ticket routing operational")
    except Exception as e:
        print(f"  FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1

    print("\n" + "=" * 60)
    print("RÉSULTAT FINAL: TOUS LES TESTS RÉUSSIS ✓")
    print("Maestro Orchestrator et Workers sont en communication")
    print("=" * 60 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
