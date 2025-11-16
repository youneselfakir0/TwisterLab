import asyncio

from agents.real.real_classifier_agent import RealClassifierAgent


async def test():
    agent = RealClassifierAgent()
    ticket = {
        "ticket_id": "TEST-001",
        "title": "Cannot connect to WiFi network",
        "description": "Laptop unable to join office wireless",
        "priority": "high",
    }
    result = await agent.execute(ticket)
    print(f"Category: {result.get('category', 'N/A')}")
    print(f"Confidence: {result.get('confidence', 0):.2%}")
    print(f"LLM Used: {result.get('llm_used', False)}")
    print(f"Time: {result.get('processing_time_ms', 0)}ms")


asyncio.run(test())
