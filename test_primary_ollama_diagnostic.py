"""
Test direct du PRIMARY Ollama (Corertx) depuis Python
Pour confirmer que le HTTP 500 est résolu
"""

import asyncio
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from agents.base.llm_client import ollama_client


async def test_primary_direct():
    """Tester PRIMARY Ollama directement (sans failover)"""
    print("\n" + "=" * 70)
    print("TEST: PRIMARY Ollama (Corertx RTX 3060) Direct")
    print("=" * 70)

    prompt = """Classify this IT support ticket into ONE category.

**Ticket**: Cannot connect to WiFi network
**Categories**: network, software, hardware, security

Answer with ONE word only:"""

    try:
        # Force PRIMARY URL
        ollama_client.base_url = "http://192.168.0.20:11434"

        start_time = datetime.now(timezone.utc)

        result = await ollama_client.generate(prompt=prompt, agent_type="classifier")

        end_time = datetime.now(timezone.utc)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        print(f"\n✅ PRIMARY Ollama OPÉRATIONNEL")
        print(f"   Response: {result['response'][:100]}")
        print(f"   Duration: {duration_ms} ms")
        print(f"   Model: {result['model']}")
        print(f"   Tokens: {result['tokens']}")

        return True

    except Exception as e:
        print(f"\n❌ PRIMARY Ollama ERREUR: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_primary_with_failover():
    """Tester PRIMARY via generate_with_fallback()"""
    print("\n" + "=" * 70)
    print("TEST: PRIMARY Ollama via generate_with_fallback()")
    print("=" * 70)

    prompt = "Classify this ticket: WiFi not working. Category (one word):"

    try:
        start_time = datetime.now(timezone.utc)

        result = await ollama_client.generate_with_fallback(prompt=prompt, agent_type="classifier")

        end_time = datetime.now(timezone.utc)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        source = result.get("source", "unknown")

        print(f"\n✅ Ollama via failover OPÉRATIONNEL")
        print(f"   Source: {source.upper()}")
        print(f"   Response: {result['response'][:100]}")
        print(f"   Duration: {duration_ms} ms")

        if source == "primary":
            print(f"\n🎉 PRIMARY utilisé avec succès (HTTP 500 résolu!)")
        elif source == "fallback":
            print(f"\n⚠️ BACKUP utilisé (PRIMARY peut-être toujours down)")

        return source

    except Exception as e:
        print(f"\n❌ Failover ERREUR: {e}")
        import traceback

        traceback.print_exc()
        return None


async def main():
    print("\n🔍 TwisterLab - Diagnostic PRIMARY Ollama (Corertx)")
    print(f"   Date: {datetime.now(timezone.utc).isoformat()}")
    print(f"   PRIMARY URL: http://192.168.0.20:11434")
    print(f"   BACKUP URL: http://192.168.0.30:11434")

    # Test 1: PRIMARY direct
    test1_success = await test_primary_direct()

    # Test 2: PRIMARY via failover
    test2_source = await test_primary_with_failover()

    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DIAGNOSTIC")
    print("=" * 70)

    if test1_success:
        print("\n✅ PRIMARY Ollama (Corertx RTX 3060) : OPÉRATIONNEL")
        print("   - /api/generate répond correctement")
        print("   - Latence normale attendue")
        print("   - HTTP 500 RÉSOLU !")
    else:
        print("\n❌ PRIMARY Ollama (Corertx RTX 3060) : PROBLÈME")

    if test2_source == "primary":
        print("\n✅ Failover utilise PRIMARY (optimal)")
        print("   - Architecture haute disponibilité fonctionnelle")
        print("   - Performance optimale (RTX 3060 12GB)")
    elif test2_source == "fallback":
        print("\n⚠️ Failover utilise BACKUP (dégradé)")
        print("   - PRIMARY toujours down pour le failover")
        print("   - BACKUP assure la continuité de service")

    print("\n" + "=" * 70)

    return 0 if test1_success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
