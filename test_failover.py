import asyncio
import time
import sys
import os

# Add project root to path
sys.path.insert(0, '/home/twister')

from agents.base.llm_client import ollama_client

async def test_ollama_primary():
    print("🧪 Testing PRIMARY Ollama (Corertx RTX 3060)...")
    start_time = time.time()

    try:
        result = await ollama_client.generate_with_fallback(
            prompt="Classify this IT ticket: 'Network is very slow, cannot connect to internet'. Respond with only one word: network, software, hardware, security, or other.",
            agent_type="classifier"
        )

        duration = time.time() - start_time
        response = result.get('response', 'error')
        source = result.get('source', 'unknown')

        print(f"✅ PRIMARY Result: response='{response}', source='{source}', duration={duration:.2f}s")
        return result

    except Exception as e:
        print(f"❌ PRIMARY Test failed: {e}")
        return None

async def test_ollama_failover():
    print("\n🔄 Testing FAILOVER (PRIMARY down, should use BACKUP)...")
    start_time = time.time()

    try:
        result = await ollama_client.generate_with_fallback(
            prompt="Classify this IT ticket: 'Computer is frozen and unresponsive'. Respond with only one word: network, software, hardware, security, or other.",
            agent_type="classifier"
        )

        duration = time.time() - start_time
        response = result.get('response', 'error')
        source = result.get('source', 'unknown')

        print(f"✅ FAILOVER Result: response='{response}', source='{source}', duration={duration:.2f}s")
        return result

    except Exception as e:
        print(f"❌ FAILOVER Test failed: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Starting Ollama Failover Tests")
    print("=" * 50)

    # Test 1: PRIMARY active
    result1 = asyncio.run(test_ollama_primary())

    print("\n" + "=" * 50)
    print("🛑 Now manually stop Ollama on PRIMARY (corertx 192.168.0.20)")
    print("   Run: ssh corertx 'sudo systemctl stop ollama'")
    print("   Then press Enter to continue...")
    input()

    # Test 2: PRIMARY down, should failover
    result2 = asyncio.run(test_ollama_failover())

    print("\n" + "=" * 50)
    print("✅ Test complete!")
    print("Expected: Test 1 uses 'primary', Test 2 uses 'fallback'")