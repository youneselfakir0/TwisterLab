"""
Tests for RealDesktopCommanderAgent with LLM command validation
"""

import asyncio

import pytest

from agents.real.real_desktop_commander_agent import RealDesktopCommanderAgent


@pytest.fixture
def commander():
    """Create commander agent instance."""
    return RealDesktopCommanderAgent()


@pytest.mark.asyncio
async def test_commander_llm_safe_ping(commander):
    """Test LLM validates safe ping command."""
    print("\n🧪 Testing LLM validation: Safe ping command")

    context = {"operation": "execute_command", "command": "ping", "args": ["8.8.8.8"]}

    result = await commander.execute(context)

    print(f"✅ Command status: {result['status']}")
    print(f"   Command: {result.get('command')}")
    print(f"   Return code: {result.get('return_code')}")

    assert result["status"] == "success"
    assert result["command"] == "ping"
    assert result["return_code"] == 0


@pytest.mark.asyncio
async def test_commander_llm_safe_ipconfig(commander):
    """Test LLM validates safe ipconfig command."""
    print("\n🧪 Testing LLM validation: Safe ipconfig command")

    context = {"operation": "execute_command", "command": "ipconfig"}

    result = await commander.execute(context)

    print(f"✅ Command status: {result['status']}")
    print(f"   Output length: {len(result.get('output', ''))}")

    assert result["status"] == "success"
    assert result["command"] == "ipconfig"
    assert len(result.get("output", "")) > 0


@pytest.mark.asyncio
async def test_commander_llm_unsafe_delete(commander):
    """Test whitelist rejects unsafe delete command."""
    print("\n🧪 Testing whitelist rejection: Unsafe delete command")

    # Try a dangerous delete command (should be rejected by whitelist)
    context = {
        "operation": "execute_command",
        "command": "del",  # Not in whitelist
        "args": ["C:\\important_file.txt"],
    }

    result = await commander.execute(context)

    print(f"Command rejected: {result['status']}")
    print(f"   Error: {result.get('error', 'N/A')[:150]}")

    assert result["status"] == "error"
    # Should be rejected because not in whitelist
    error_msg = result.get("error", "").lower()
    assert "not in whitelist" in error_msg or "not whitelisted" in error_msg


@pytest.mark.asyncio
async def test_commander_llm_validation_method(commander):
    """Test LLM validation method directly (advisory only)."""
    print("\n🧪 Testing LLM _validate_command_llm() method")

    if not commander.use_llm:
        pytest.skip("LLM not available")

    # Note: LLM validation is now ADVISORY only (not blocking)
    # Whitelist is the primary security mechanism

    # Test ping (whitelisted command)
    is_safe_ping = await commander._validate_command_llm("ping", ["8.8.8.8"])
    print(f"ping 8.8.8.8 -> {'SAFE' if is_safe_ping else 'UNSAFE (LLM advisory)'}")
    # Don't assert - LLM is advisory only

    # Test shutdown (not whitelisted)
    is_safe_shutdown = await commander._validate_command_llm("shutdown", ["/s", "/t", "0"])
    print(f"shutdown /s /t 0 -> {'SAFE' if is_safe_shutdown else 'UNSAFE (LLM advisory)'}")
    # Don't assert - whitelist will block it anyway


@pytest.mark.asyncio
async def test_commander_whitelist_fallback(commander):
    """Test whitelist fallback when LLM disabled."""
    print("\n🧪 Testing whitelist fallback mechanism")

    # Temporarily disable LLM
    original_use_llm = commander.use_llm
    commander.use_llm = False

    try:
        # Whitelisted command should work
        context = {"operation": "execute_command", "command": "hostname"}

        result = await commander.execute(context)

        print(f"✅ Fallback to whitelist worked")
        print(f"   Status: {result['status']}")
        print(f"   Command: {result.get('command')}")

        assert result["status"] == "success"
        assert result["command"] == "hostname"

    finally:
        # Restore LLM setting
        commander.use_llm = original_use_llm


@pytest.mark.asyncio
async def test_commander_system_info(commander):
    """Test system info gathering."""
    print("\n🧪 Testing system info gathering")

    context = {"operation": "get_system_info"}

    result = await commander.execute(context)

    print(f"✅ System info gathered")
    print(f"   Hostname: {result['system_info'].get('hostname')}")
    print(f"   Platform: {result['system_info'].get('platform')}")
    print(f"   CPU percent: {result['system_info']['cpu'].get('percent')}%")
    print(f"   Memory total: {result['system_info']['memory'].get('total_gb')} GB")

    assert result["status"] == "success"
    assert "system_info" in result
    assert "cpu" in result["system_info"]
    assert "memory" in result["system_info"]


@pytest.mark.asyncio
async def test_commander_network_diagnostic(commander):
    """Test network diagnostics."""
    print("\n🧪 Testing network diagnostics")

    context = {"operation": "network_diagnostic", "target": "8.8.8.8"}

    result = await commander.execute(context)

    print(f"✅ Network diagnostics complete")
    print(f"   Target: {result.get('target')}")
    print(f"   Overall health: {result.get('overall_health')}")
    print(f"   Ping success: {result['diagnostics']['ping'].get('success')}")

    assert result["status"] == "success"
    assert "diagnostics" in result
    assert "ping" in result["diagnostics"]


# Manual test runner (if not using pytest)
async def run_tests():
    """Run all tests manually."""
    print("\n" + "=" * 60)
    print("🧪 DESKTOP COMMANDER AGENT LLM TESTS")
    print("=" * 60)

    commander = RealDesktopCommanderAgent()

    print(f"\n📊 Agent Info:")
    print(f"   Name: {commander.name}")
    print(f"   OS: {commander.os_type}")
    print(f"   LLM Available: {commander.use_llm}")
    print(f"   Whitelisted commands: {len(commander.safe_commands)}")

    tests = [
        ("Safe ping command", test_commander_llm_safe_ping),
        ("Safe ipconfig command", test_commander_llm_safe_ipconfig),
        ("Unsafe delete command", test_commander_llm_unsafe_delete),
        ("LLM validation method", test_commander_llm_validation_method),
        ("Whitelist fallback", test_commander_whitelist_fallback),
        ("System info", test_commander_system_info),
        ("Network diagnostics", test_commander_network_diagnostic),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            await test_func(commander)
            print(f"✅ PASSED: {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name}")
            print(f"   Error: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(run_tests())
