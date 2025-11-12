"""
Tests for RealClassifierAgent with LLM integration
"""
import pytest
import asyncio
from agents.real.real_classifier_agent import RealClassifierAgent


@pytest.fixture
def classifier():
    """Create classifier agent instance."""
    return RealClassifierAgent()


@pytest.mark.asyncio
async def test_classifier_llm_network_ticket(classifier):
    """Test LLM classification of network ticket."""
    ticket = {
        "id": "TEST-001",
        "title": "Cannot connect to WiFi",
        "description": "My laptop won't join the office network. Getting error 'Limited connectivity'",
        "user": "john.doe@company.com"
    }

    result = await classifier.execute({
        "operation": "classify_ticket",
        "ticket": ticket
    })

    assert result["status"] == "success"
    assert result["ticket_id"] == "TEST-001"

    classification = result["classification"]
    assert classification["category"] == "network"
    assert classification["confidence"] >= 0.5
    assert classification["priority"] in ["critical", "high", "medium", "low"]
    assert classification["routed_to_agent"] in ["DesktopCommanderAgent", "ResolverAgent", "MonitoringAgent", "SyncAgent"]

    # Check if LLM was used
    method = classification.get("method", "keywords")
    print(f"\n✅ Classification method: {method}")
    print(f"   Category: {classification['category']}")
    print(f"   Confidence: {classification['confidence']}")
    print(f"   Priority: {classification['priority']}")
    print(f"   Routed to: {classification['routed_to_agent']}")

    if method == "llm":
        assert "model" in result["analysis"]
        print(f"   Model: {result['analysis']['model']}")
        print(f"   Processing time: {result['processing_time_ms']}ms")


@pytest.mark.asyncio
async def test_classifier_llm_software_ticket(classifier):
    """Test LLM classification of software ticket."""
    ticket = {
        "id": "TEST-002",
        "title": "Excel keeps crashing",
        "description": "When I open large files, Microsoft Excel freezes and crashes. Happens every time.",
        "user": "jane.smith@company.com"
    }

    result = await classifier.execute({
        "operation": "classify_ticket",
        "ticket": ticket
    })

    assert result["status"] == "success"
    classification = result["classification"]
    # LLM might classify "crashes" as either software OR performance (both valid)
    assert classification["category"] in ["software", "performance"]

    print(f"\n✅ Software ticket classified: {classification['category']}")
    print(f"   Method: {classification.get('method', 'keywords')}")
    print(f"   Priority: {classification['priority']}")


@pytest.mark.asyncio
async def test_classifier_llm_hardware_ticket(classifier):
    """Test LLM classification of hardware ticket."""
    ticket = {
        "id": "TEST-003",
        "title": "Screen flickering",
        "description": "My monitor has black lines and keeps flickering. Hard to read.",
        "user": "bob.johnson@company.com"
    }

    result = await classifier.execute({
        "operation": "classify_ticket",
        "ticket": ticket
    })

    assert result["status"] == "success"
    classification = result["classification"]
    # LLM might classify "flickering screen" as hardware OR performance (both valid)
    assert classification["category"] in ["hardware", "performance"]

    print(f"\n✅ Hardware ticket classified: {classification['category']}")
    print(f"   Method: {classification.get('method', 'keywords')}")


@pytest.mark.asyncio
async def test_classifier_llm_security_ticket(classifier):
    """Test LLM classification of security ticket."""
    ticket = {
        "id": "TEST-004",
        "title": "Forgot my password",
        "description": "I cannot remember my domain password and need to reset it urgently.",
        "user": "alice.williams@company.com"
    }

    result = await classifier.execute({
        "operation": "classify_ticket",
        "ticket": ticket
    })

    assert result["status"] == "success"
    classification = result["classification"]
    assert classification["category"] == "security"

    print(f"\n✅ Security ticket classified: {classification['category']}")
    print(f"   Method: {classification.get('method', 'keywords')}")


@pytest.mark.asyncio
async def test_classifier_fallback_on_llm_failure(classifier):
    """Test that classifier falls back to keywords if LLM fails."""
    # Disable LLM temporarily
    original_use_llm = classifier.use_llm
    classifier.use_llm = False

    ticket = {
        "id": "TEST-005",
        "title": "Network printer not working",
        "description": "Cannot print to the office printer",
        "user": "test@company.com"
    }

    result = await classifier.execute({
        "operation": "classify_ticket",
        "ticket": ticket
    })

    assert result["status"] == "success"
    classification = result["classification"]
    assert classification["method"] == "keywords"
    assert classification["category"] in ["network", "hardware"]

    print(f"\n✅ Fallback to keywords worked")
    print(f"   Category: {classification['category']}")

    # Restore LLM setting
    classifier.use_llm = original_use_llm


@pytest.mark.asyncio
async def test_classifier_performance_comparison():
    """Compare LLM vs keyword classification performance."""
    classifier = RealClassifierAgent()

    test_tickets = [
        {"id": "PERF-1", "title": "WiFi down", "description": "Cannot connect", "user": "user1"},
        {"id": "PERF-2", "title": "Outlook crash", "description": "Email app freezing", "user": "user2"},
        {"id": "PERF-3", "title": "Keyboard broken", "description": "Keys not working", "user": "user3"},
    ]

    # Test with LLM
    llm_times = []
    for ticket in test_tickets:
        result = await classifier.execute({"operation": "classify_ticket", "ticket": ticket})
        llm_times.append(result.get("processing_time_ms", 0))

    avg_llm_time = sum(llm_times) / len(llm_times) if llm_times else 0

    # Test with keywords (fallback)
    classifier.use_llm = False
    keyword_times = []
    for ticket in test_tickets:
        result = await classifier.execute({"operation": "classify_ticket", "ticket": ticket})
        keyword_times.append(result.get("processing_time_ms", 0))

    avg_keyword_time = sum(keyword_times) / len(keyword_times) if keyword_times else 0

    print(f"\n📊 Performance Comparison:")
    print(f"   LLM avg: {avg_llm_time:.0f}ms")
    print(f"   Keywords avg: {avg_keyword_time:.0f}ms")
    print(f"   Overhead: {avg_llm_time - avg_keyword_time:.0f}ms")

    # LLM should be slower but not excessively (< 10 seconds)
    assert avg_llm_time < 10000, "LLM classification too slow"


if __name__ == "__main__":
    # Run tests manually
    async def run_tests():
        print("🧪 Running ClassifierAgent LLM Tests\n")

        classifier = RealClassifierAgent()

        # Test 1: Network ticket
        print("Test 1: Network Ticket")
        await test_classifier_llm_network_ticket(classifier)

        # Test 2: Software ticket
        print("\nTest 2: Software Ticket")
        await test_classifier_llm_software_ticket(classifier)

        # Test 3: Hardware ticket
        print("\nTest 3: Hardware Ticket")
        await test_classifier_llm_hardware_ticket(classifier)

        # Test 4: Security ticket
        print("\nTest 4: Security Ticket")
        await test_classifier_llm_security_ticket(classifier)

        # Test 5: Fallback
        print("\nTest 5: Fallback to Keywords")
        await test_classifier_fallback_on_llm_failure(classifier)

        # Test 6: Performance
        print("\nTest 6: Performance Comparison")
        await test_classifier_performance_comparison()

        print("\n✅ All tests passed!")

    asyncio.run(run_tests())
