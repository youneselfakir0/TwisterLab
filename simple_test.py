import sys
import asyncio
import time

sys.path.insert(0, '/home/twister')

from agents.base.llm_client import ollama_client

async def test():
    print("🧪 Testing Ollama PRIMARY (Corertx RTX 3060)...")
    start = time.time()
    result = await ollama_client.generate_with_fallback("Hello, respond with 'test successful'", "test")
    duration = time.time() - start
    print(f"✅ Result: {result.get('response', 'error')}")
    print(f"⏱️  Duration: {duration:.2f}s")
    print(f"🎯 Source: {result.get('source', 'unknown')}")
    return result

if __name__ == "__main__":
    asyncio.run(test())