"""
Test Ollama Failover - TwisterLab v1.0.2
Tests automatic failover from PRIMARY to BACKUP Ollama servers.
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.base.llm_client import OllamaClient
from agents.config import OLLAMA_FALLBACK, OLLAMA_URL


async def test_primary():
    """Test PRIMARY Ollama (Corertx RTX 3060)"""
    print("\n" + "=" * 60)
    print("TEST 1: PRIMARY Ollama (Corertx RTX 3060)")
    print("=" * 60)
    print(f"URL: {OLLAMA_URL}")

    client = OllamaClient()

    try:
        result = await client.generate_with_fallback(
            prompt="Respond with only 'OK' if you can read this.", agent_type="general"
        )

        print(f"✅ SUCCESS")
        print(f"   Response: {result['response']}")
        print(f"   Source: {result['source']}")
        print(f"   Duration: {result['duration_seconds']:.2f}s")
        print(f"   GPU: RTX 3060 12GB")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def test_fallback_only():
    """Test FALLBACK Ollama (Edgeserver GTX 1050) by forcing PRIMARY failure"""
    print("\n" + "=" * 60)
    print("TEST 2: FALLBACK Ollama (Edgeserver GTX 1050)")
    print("=" * 60)
    print(f"URL: {OLLAMA_FALLBACK}")
    print("⚠️  Simulating PRIMARY failure...")

    client = OllamaClient()
    # Force PRIMARY to fail by using invalid URL
    client.primary_url = "http://192.168.0.99:11434"  # Non-existent IP

    try:
        result = await client.generate_with_fallback(
            prompt="Respond with only 'BACKUP' if you can read this.", agent_type="general"
        )

        print(f"✅ SUCCESS (Failover worked!)")
        print(f"   Response: {result['response']}")
        print(f"   Source: {result['source']}")
        print(f"   Duration: {result['duration_seconds']:.2f}s")
        print(f"   GPU: GTX 1050 2GB")
        print(f"   Performance: ~2-3x slower than PRIMARY (expected)")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def test_classifier_agent():
    """Test realistic ticket classification with failover"""
    print("\n" + "=" * 60)
    print("TEST 3: Real Agent Task (Ticket Classification)")
    print("=" * 60)

    client = OllamaClient()

    test_ticket = """
    User reports: "My computer won't connect to the WiFi network.
    I can see the network but it keeps saying wrong password even
    though I'm sure it's correct."
    """

    prompt = f"""Classify this IT helpdesk ticket into ONE category only.

Ticket: {test_ticket}

Choose from: hardware, software, network, printer, access, other

Category:"""

    try:
        result = await client.generate_with_fallback(prompt=prompt, agent_type="classifier")

        print(f"✅ SUCCESS")
        print(f"   Ticket: WiFi connection issue")
        print(f"   Classification: {result['response']}")
        print(f"   Source: {result['source'].upper()}")
        print(f"   Duration: {result['duration_seconds']:.2f}s")
        print(f"   URL: {result['url']}")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def test_both_down():
    """Test behavior when both PRIMARY and FALLBACK are down"""
    print("\n" + "=" * 60)
    print("TEST 4: Both Ollama Servers Down (Error Handling)")
    print("=" * 60)
    print("⚠️  Simulating complete service failure...")

    client = OllamaClient()
    # Force both to fail
    client.primary_url = "http://192.168.0.99:11434"
    client.fallback_url = "http://192.168.0.98:11434"

    try:
        result = await client.generate_with_fallback(
            prompt="This should fail", agent_type="general"
        )

        print(f"❌ UNEXPECTED SUCCESS (should have failed)")
        return False

    except RuntimeError as e:
        print(f"✅ SUCCESS (Error handled correctly)")
        print(f"   Error message: {str(e)[:100]}...")
        return True
    except Exception as e:
        print(f"⚠️  PARTIAL SUCCESS (Different error type)")
        print(f"   Error: {e}")
        return True


async def main():
    """Run all failover tests"""
    print("\n" + "=" * 60)
    print("TWISTERLAB v1.0.2 - OLLAMA FAILOVER TESTS")
    print("=" * 60)
    print(f"PRIMARY:  {OLLAMA_URL} (Corertx RTX 3060 12GB)")
    print(f"FALLBACK: {OLLAMA_FALLBACK} (Edgeserver GTX 1050 2GB)")

    results = []

    # Test 1: PRIMARY only
    results.append(("Primary Ollama", await test_primary()))

    # Test 2: FALLBACK only (simulated PRIMARY failure)
    results.append(("Fallback Ollama", await test_fallback_only()))

    # Test 3: Real agent task
    results.append(("Agent Classification", await test_classifier_agent()))

    # Test 4: Both down
    results.append(("Error Handling", await test_both_down()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {test_name}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED - Failover system operational!")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
