"""
Tests for RealResolverAgent with LLM integration
"""

import asyncio

import pytest

from agents.real.real_resolver_agent import RealResolverAgent


@pytest.fixture
def resolver():
    """Create resolver agent instance."""
    return RealResolverAgent()


@pytest.mark.asyncio
async def test_resolver_llm_network_ticket(resolver):
    """Test LLM SOP generation for network ticket."""
    ticket = {
        "id": "TEST-RES-001",
        "title": "Cannot connect to WiFi",
        "description": "Laptop won't join office network. Error: 'Limited connectivity'",
        "category": "network",
        "user": "john.doe@company.com",
    }

    result = await resolver.execute({"operation": "resolve_ticket", "ticket": ticket})

    assert result["status"] == "success"
    assert result["ticket_id"] == "TEST-RES-001"

    resolution = result["resolution"]
    assert resolution["steps_executed"] >= 3  # At least 3 steps
    assert resolution["success"] is True
    assert resolution["outcome"] == "resolved"

    # Check method used
    method = resolution.get("method", "static")
    print(f"\n✅ Resolution method: {method}")
    print(f"   SOP: {resolution['sop_name']}")
    print(f"   Steps: {resolution['steps_executed']}")

    if method == "llm":
        assert "model" in result["analysis"]
        assert len(resolution["steps_detail"]) >= 3
        print(f"   Model: {result['analysis']['model']}")
        print(f"   LLM duration: {result['analysis']['llm_duration_seconds']:.2f}s")
        print(f"   First step: {resolution['steps_detail'][0]['description'][:60]}...")


@pytest.mark.asyncio
async def test_resolver_llm_software_ticket(resolver):
    """Test LLM SOP generation for software ticket."""
    ticket = {
        "id": "TEST-RES-002",
        "title": "Excel keeps crashing",
        "description": "Microsoft Excel freezes when opening large files",
        "category": "software",
        "user": "jane.smith@company.com",
    }

    result = await resolver.execute({"operation": "resolve_ticket", "ticket": ticket})

    assert result["status"] == "success"
    resolution = result["resolution"]
    assert resolution["steps_executed"] >= 3

    method = resolution.get("method", "static")
    print(f"\n✅ Software ticket resolved: {method}")
    print(f"   Steps generated: {resolution['steps_executed']}")

    if method == "llm":
        # Verify steps are relevant to Excel/software issues
        steps_text = " ".join([s["description"] for s in resolution["steps_detail"]])
        assert any(
            word in steps_text.lower()
            for word in ["excel", "update", "repair", "reinstall", "office"]
        )


@pytest.mark.asyncio
async def test_resolver_llm_performance_ticket(resolver):
    """Test LLM SOP generation for performance ticket."""
    ticket = {
        "id": "TEST-RES-003",
        "title": "Computer running very slow",
        "description": "System sluggish, high CPU usage, takes long to open programs",
        "category": "performance",
        "user": "bob.johnson@company.com",
    }

    result = await resolver.execute({"operation": "resolve_ticket", "ticket": ticket})

    assert result["status"] == "success"
    resolution = result["resolution"]
    assert resolution["steps_executed"] >= 3

    method = resolution.get("method", "static")
    print(f"\n✅ Performance ticket resolved: {method}")
    print(f"   Steps: {resolution['steps_executed']}")

    if method == "llm":
        # Verify steps are relevant (more flexible check)
        steps_text = " ".join([s["description"] for s in resolution["steps_detail"]]).lower()
        # Check for performance-related words OR generic troubleshooting
        performance_keywords = [
            "cpu",
            "memory",
            "disk",
            "task",
            "process",
            "cleanup",
            "restart",
            "check",
            "monitor",
            "usage",
        ]
        assert any(
            word in steps_text for word in performance_keywords
        ), f"No performance keywords found in: {steps_text[:200]}"


@pytest.mark.asyncio
async def test_resolver_llm_database_ticket(resolver):
    """Test LLM SOP generation for database ticket."""
    ticket = {
        "id": "TEST-RES-004",
        "title": "Database connection timeout",
        "description": "Application cannot connect to PostgreSQL database",
        "category": "database",
        "user": "admin@company.com",
    }

    result = await resolver.execute({"operation": "resolve_ticket", "ticket": ticket})

    assert result["status"] == "success"
    resolution = result["resolution"]
    assert resolution["steps_executed"] >= 3

    print(f"\n✅ Database ticket resolved")
    print(f"   Method: {resolution.get('method', 'static')}")


@pytest.mark.asyncio
async def test_resolver_fallback_on_llm_failure(resolver):
    """Test that resolver falls back to static SOPs if LLM fails."""
    # Disable LLM temporarily
    original_use_llm = resolver.use_llm
    resolver.use_llm = False

    ticket = {
        "id": "TEST-RES-005",
        "title": "Network printer not working",
        "description": "Cannot print to office printer",
        "category": "network",
        "user": "test@company.com",
    }

    result = await resolver.execute({"operation": "resolve_ticket", "ticket": ticket})

    assert result["status"] == "success"
    resolution = result["resolution"]
    assert resolution["method"] == "static"
    assert resolution["sop_used"] == "network_troubleshoot"

    print(f"\n✅ Fallback to static SOP worked")
    print(f"   SOP: {resolution['sop_name']}")
    print(f"   Steps: {resolution['steps_executed']}")

    # Restore LLM setting
    resolver.use_llm = original_use_llm


@pytest.mark.asyncio
async def test_resolver_list_sops(resolver):
    """Test listing available static SOPs."""
    result = await resolver.execute({"operation": "list_sops"})

    assert result["status"] == "success"
    assert result["total_sops"] == 5  # 5 built-in SOPs
    assert len(result["sops"]) == 5

    # Check SOP structure
    first_sop = result["sops"][0]
    assert "id" in first_sop
    assert "name" in first_sop
    assert "category" in first_sop
    assert "steps_count" in first_sop

    print(f"\n✅ Listed {result['total_sops']} static SOPs")
    for sop in result["sops"]:
        print(f"   - {sop['id']}: {sop['name']} ({sop['steps_count']} steps)")


@pytest.mark.asyncio
async def test_resolver_sop_quality():
    """Test quality of LLM-generated SOP steps."""
    resolver = RealResolverAgent()

    if not resolver.use_llm:
        pytest.skip("LLM not available, skipping quality test")

    ticket = {
        "id": "QUALITY-001",
        "title": "Email not sending",
        "description": "Outlook gives error when trying to send emails",
        "category": "email",
        "user": "user@company.com",
    }

    result = await resolver.execute({"operation": "resolve_ticket", "ticket": ticket})

    if result["resolution"].get("method") == "llm":
        steps = result["resolution"]["steps_detail"]

        # Quality checks
        assert len(steps) >= 3, "Should have at least 3 steps"
        assert len(steps) <= 10, "Should not exceed 10 steps"

        # Each step should have description
        for step in steps:
            assert len(step["description"]) > 10, "Step description too short"
            assert step["step_number"] > 0, "Step number should be positive"

        print(f"\n✅ SOP Quality Test Passed")
        print(f"   Steps count: {len(steps)}")
        print(
            f"   Avg step length: {sum(len(s['description']) for s in steps) / len(steps):.0f} chars"
        )


if __name__ == "__main__":
    # Run tests manually
    async def run_tests():
        print("🧪 Running ResolverAgent LLM Tests\n")

        resolver = RealResolverAgent()

        # Test 1: Network ticket
        print("Test 1: Network Ticket")
        await test_resolver_llm_network_ticket(resolver)

        # Test 2: Software ticket
        print("\nTest 2: Software Ticket")
        await test_resolver_llm_software_ticket(resolver)

        # Test 3: Performance ticket
        print("\nTest 3: Performance Ticket")
        await test_resolver_llm_performance_ticket(resolver)

        # Test 4: Database ticket
        print("\nTest 4: Database Ticket")
        await test_resolver_llm_database_ticket(resolver)

        # Test 5: Fallback
        print("\nTest 5: Fallback to Static SOPs")
        await test_resolver_fallback_on_llm_failure(resolver)

        # Test 6: List SOPs
        print("\nTest 6: List Static SOPs")
        await test_resolver_list_sops(resolver)

        # Test 7: SOP Quality
        print("\nTest 7: SOP Quality Check")
        await test_resolver_sop_quality()

        print("\n✅ All tests passed!")

    asyncio.run(run_tests())
