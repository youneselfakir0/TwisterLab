#!/usr/bin/env python3
import asyncio
import sys
import time

# Add project path
sys.path.insert(0, "/app")


async def test_failover():
    print("🔄 Testing Ollama Failover (PRIMARY down, should use BACKUP)")
    print("=" * 60)

    try:
        from agents.base.llm_client import ollama_client

        start_time = time.time()

        # Test with PRIMARY down - should failover to BACKUP
        result = await ollama_client.generate_with_fallback(
            prompt="Classify: Computer is frozen. Respond with one word: hardware",
            agent_type="classifier",
        )

        duration = time.time() - start_time

        response = result.get("response", "ERROR").strip()
        source = result.get("source", "unknown")
        url = result.get("url", "unknown")

        print("✅ FAILOVER TEST RESULTS:")
        print(f"   Response: '{response}'")
        print(f"   Duration: {duration:.2f}s")
        print(f"   Source: {source}")
        print(f"   URL: {url}")

        # Verify it used BACKUP
        if source == "fallback":
            print("✅ SUCCESS: Failover worked! Used BACKUP as expected")
            return True
        else:
            print("❌ FAILURE: Did not failover to BACKUP")
            return False

    except Exception as e:
        print(f"❌ FAILOVER TEST FAILED: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_failover())
    sys.exit(0 if success else 1)
