import asyncio
import httpx
from agents.base.llm_client import OllamaClient

async def test():
    # Force l'URL avec l'IP directe
    client = OllamaClient(base_url="http://10.0.1.14:11434", model="llama3.2:1b", timeout=30)

    prompt = """Classify this IT support ticket into ONE category.
Ticket: "Cannot connect to WiFi network. Laptop unable to join office wireless"
Category (network/software/hardware/access):"""

    result = await client.generate(prompt)
    print(f"✓ LLM Response: {result['response'][:200]}")
    print(f"✓ Tokens: {result['tokens']}")
    print(f"✓ Duration: {result['duration_seconds']:.2f}s")

asyncio.run(test())
