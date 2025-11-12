"""Test ClassifierAgent LLM integration on production EdgeServer"""
import asyncio
import httpx
import sys

async def test_classifier_production():
    """Test real ClassifierAgent on EdgeServer with LLM"""

    # Import the real agent (will connect to Ollama on edgeserver)
    sys.path.insert(0, 'C:/TwisterLab')
    from agents.real.real_classifier_agent import RealClassifierAgent

    # Create agent
    agent = RealClassifierAgent()

    # Test ticket
    test_ticket = {
        "ticket_id": "PROD-TEST-001",
        "title": "Cannot connect to WiFi network",
        "description": "Laptop unable to join office wireless network. Error: 'Can't connect to this network'",
        "priority": "high",
        "requester": "test@twisterlab.com"
    }

    print("\n" + "="*60)
    print("TESTING CLASSIFIERAGENT LLM ON PRODUCTION")
    print("="*60)
    print(f"\nTicket: {test_ticket['title']}")
    print(f"Priority: {test_ticket['priority']}")

    # Classify
    print("\n🤖 Classifying with LLM (Ollama on EdgeServer)...")
    result = await agent.execute(test_ticket)

    # Display results
    print("\n" + "="*60)
    print("CLASSIFICATION RESULT")
    print("="*60)
    print(f"Status: {result['status']}")
    print(f"Category: {result['category']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Processing Time: {result['processing_time_ms']}ms")
    print(f"LLM Used: {result.get('llm_used', 'N/A')}")

    if result.get('llm_response'):
        print(f"\n💬 LLM Response:\n{result['llm_response']}")

    # Check metrics
    print("\n" + "="*60)
    print("CHECKING PROMETHEUS METRICS")
    print("="*60)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://192.168.0.30:9090/api/v1/query?query=classifier_llm_duration_seconds_count")
            metrics = response.json()

            if metrics['status'] == 'success' and metrics['data']['result']:
                count = metrics['data']['result'][0]['value'][1]
                print(f"✅ classifier_llm_duration_seconds_count: {count}")
            else:
                print("⚠️  No metrics found yet (may need time to scrape)")
    except Exception as e:
        print(f"⚠️  Could not fetch metrics: {e}")

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test_classifier_production())
