import asyncio
import httpx

async def test_direct():
    url = "http://192.168.0.30:11434/api/generate"
    data = {
        "model": "llama3.2:1b",
        "prompt": "Classify this IT ticket: 'Cannot connect to WiFi'. Category:",
        "stream": False
    }

    print(f"Testing direct Ollama call to {url}...")
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json=data)
        result = response.json()
        print(f"✓ Response: {result['response'][:200]}...")
        print(f"✓ Tokens: {result.get('eval_count', 0)}")
        print(f"✓ Duration: {result.get('total_duration', 0) / 1e9:.2f}s")

asyncio.run(test_direct())
