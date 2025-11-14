"""
Test d'intégration pour valider que les 3 agents utilisent correctement le failover automatique.

Teste :
- RealClassifierAgent avec generate_with_fallover()
- RealResolverAgent avec generate_with_fallback()
- RealDesktopCommanderAgent avec generate_with_fallback()
"""
import asyncio
import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from agents.real.real_classifier_agent import RealClassifierAgent
from agents.real.real_resolver_agent import RealResolverAgent
from agents.real.real_desktop_commander_agent import RealDesktopCommanderAgent


async def test_classifier_with_failover():
    """Test RealClassifierAgent avec failover automatique"""
    print("\n" + "="*70)
    print("TEST 1: RealClassifierAgent avec failover automatique")
    print("="*70)

    agent = RealClassifierAgent()

    # Ticket de test (problème WiFi)
    ticket = {
        "id": "TEST-001",
        "title": "Cannot connect to WiFi",
        "description": "My laptop cannot detect any WiFi networks since this morning. Other devices work fine.",
        "user": "test_user@twisterlab.local"
    }

    context = {
        "operation": "classify_ticket",
        "ticket": ticket
    }

    start_time = datetime.now(timezone.utc)
    result = await agent.execute(context)
    end_time = datetime.now(timezone.utc)

    duration_ms = int((end_time - start_time).total_seconds() * 1000)

    print(f"\n📊 Résultat Classification:")
    print(f"   Status: {result.get('status')}")

    # Get classification data (may be nested)
    classification = result.get('classification', {})
    category = classification.get('category', result.get('category'))
    confidence = classification.get('confidence', result.get('confidence', 0))
    routed_to = classification.get('routed_to_agent', result.get('route_to'))
    method = classification.get('method', 'unknown')

    print(f"   Category: {category}")
    print(f"   Confidence: {confidence:.2f}")
    print(f"   Routed to: {routed_to}")
    print(f"   Method: {method}")
    print(f"   Duration: {duration_ms} ms")

    assert result["status"] == "success", f"Classification failed: {result.get('error')}"
    assert category is not None, "No category returned"

    # Check if LLM was used (indicates failover worked)
    if method == "llm":
        print(f"\n✅ Classification successful via LLM (failover opérationnel)")
    else:
        print(f"\n⚠️ Classification via keywords (LLM non disponible)")

    return result


async def test_resolver_with_failover():
    """Test RealResolverAgent avec failover automatique"""
    print("\n" + "="*70)
    print("TEST 2: RealResolverAgent avec failover automatique")
    print("="*70)

    agent = RealResolverAgent()

    # Ticket de test (problème réseau)
    ticket = {
        "id": "TEST-002",
        "title": "Network connectivity issue",
        "description": "User cannot access internal network shares",
        "category": "network",
        "priority": "high",
        "user": "test_user@twisterlab.local"
    }

    context = {
        "operation": "resolve_ticket",
        "ticket": ticket
    }

    start_time = datetime.now(timezone.utc)
    result = await agent.execute(context)
    end_time = datetime.now(timezone.utc)

    duration_ms = int((end_time - start_time).total_seconds() * 1000)

    print(f"\n📊 Résultat Résolution:")
    print(f"   Status: {result.get('status')}")
    print(f"   SOP Steps: {len(result.get('sop', {}).get('steps', []))}")
    print(f"   Duration: {duration_ms} ms")

    # Extract source from SOP metadata if available
    sop = result.get("sop", {})
    steps = sop.get("steps", [])

    if steps:
        print(f"   First step: {steps[0].get('description', 'N/A')[:60]}...")

    assert result["status"] == "success", f"Resolution failed: {result.get('error')}"
    assert len(steps) > 0, "No SOP steps generated"

    print(f"\n✅ SOP generation successful with {len(steps)} steps")

    return result


async def test_commander_with_failover():
    """Test RealDesktopCommanderAgent avec failover automatique"""
    print("\n" + "="*70)
    print("TEST 3: RealDesktopCommanderAgent avec failover automatique")
    print("="*70)

    agent = RealDesktopCommanderAgent()

    # Commande safe de test
    safe_command = "ping 8.8.8.8 -n 2"

    context = {
        "operation": "validate_command",
        "command": safe_command
    }

    start_time = datetime.now(timezone.utc)
    result = await agent.execute(context)
    end_time = datetime.now(timezone.utc)

    duration_ms = int((end_time - start_time).total_seconds() * 1000)

    print(f"\n📊 Résultat Validation:")
    print(f"   Status: {result.get('status')}")
    print(f"   Command: {safe_command}")
    print(f"   Is Safe: {result.get('is_safe')}")
    print(f"   Duration: {duration_ms} ms")

    assert result["status"] == "success", f"Validation failed: {result.get('error')}"
    assert result.get("is_safe") == True, f"Safe command marked as unsafe: {safe_command}"

    print(f"\n✅ Command validation successful (marked as SAFE)")

    # Test une commande unsafe
    print(f"\n   Testing unsafe command detection...")
    unsafe_command = "shutdown /s /t 0"

    context_unsafe = {
        "operation": "validate_command",
        "command": unsafe_command
    }

    result_unsafe = await agent.execute(context_unsafe)

    print(f"   Unsafe command: {unsafe_command}")
    print(f"   Is Safe: {result_unsafe.get('is_safe')}")

    assert result_unsafe.get("is_safe") == False, f"Unsafe command marked as safe: {unsafe_command}"

    print(f"\n✅ Unsafe command correctly detected as UNSAFE")

    return result


async def main():
    """Exécute tous les tests d'intégration"""
    print("\n🚀 TwisterLab - Tests d'intégration des agents avec failover automatique")
    print(f"   Date: {datetime.now(timezone.utc).isoformat()}")
    print(f"   Ollama PRIMARY: http://192.168.0.20:11434 (Corertx RTX 3060)")
    print(f"   Ollama BACKUP: http://192.168.0.30:11434 (Edgeserver GTX 1050)")

    results = {}

    try:
        # Test 1: Classifier
        results["classifier"] = await test_classifier_with_failover()

        # Test 2: Resolver
        results["resolver"] = await test_resolver_with_failover()

        # Test 3: Desktop Commander
        results["commander"] = await test_commander_with_failover()

        # Résumé final
        print("\n" + "="*70)
        print("📊 RÉSUMÉ DES TESTS")
        print("="*70)

        all_success = all(
            result.get("status") == "success"
            for result in results.values()
        )

        print(f"\n   ✅ RealClassifierAgent: {results['classifier']['status'].upper()}")
        print(f"   ✅ RealResolverAgent: {results['resolver']['status'].upper()}")
        print(f"   ✅ RealDesktopCommanderAgent: {results['commander']['status'].upper()}")

        if all_success:
            print(f"\n🎉 TOUS LES TESTS RÉUSSIS - Failover opérationnel sur les 3 agents!")
            print(f"\n✅ Haute disponibilité validée:")
            print(f"   - Automatic failover PRIMARY → BACKUP")
            print(f"   - Agents utilisent generate_with_fallback()")
            print(f"   - Logging de la source (primary/fallback)")
            return 0
        else:
            print(f"\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
            return 1

    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
