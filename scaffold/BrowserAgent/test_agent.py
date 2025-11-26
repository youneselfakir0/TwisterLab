import pytest

from twisterlab.agents.real.browser_agent import BrowserAgent
from twisterlab.twisterlang.codec import (
    build_message,
    decode_message_from_base64,
    encode_message_to_base64,
)


@pytest.fixture
def browser_agent():
    return BrowserAgent()


def test_browser_agent_initialization(browser_agent):
    assert browser_agent is not None


def test_browser_agent_functionality(browser_agent):
    # Verify the agent's execute_tool behavior
    result = browser_agent.execute_tool(
        "create_browser_tool", {"target_url": "https://example.com"}
    )
    assert result is not None
    assert isinstance(result, dict)
    assert result.get("status") == "success"


def test_browser_agent_error_handling(browser_agent):
    # Verify invalid URL yields an error result
    result = browser_agent.execute_tool(
        "create_browser_tool", {"target_url": "invalid_url"}
    )
    assert result.get("status") == "error"


def test_twisterlang_roundtrip(browser_agent):
    payload = {
        "twisterlang_version": "1.0",
        "correlation_id": "roundtrip-id",
        "data": {"k": "v"},
    }
    message = build_message(payload)
    encoded_message = encode_message_to_base64(message)
    decoded_message = decode_message_from_base64(encoded_message)
    assert decoded_message == message
