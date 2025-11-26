from twisterlab.agents.real.browser_agent import BrowserAgent
from twisterlang.codec import build_message, encode_message_to_base64, validate_message


def test_browser_agent_initialization():
    agent = BrowserAgent()
    assert agent is not None


def test_browser_tool_creation():
    tool_name = "create_browser_tool"
    target_url = "https://example.com"
    llm_backend = "ollama"

    message = build_message(
        tool_name=tool_name,
        args={
            "target_url": target_url,
            "tool_name": "scrape_home",
            "llm_backend": llm_backend,
        },
    )

    assert validate_message(message)

    encoded_message = encode_message_to_base64(message)
    assert encoded_message is not None


def test_browser_agent_execution():
    agent = BrowserAgent()
    result = agent.execute_tool(
        "create_browser_tool", {"target_url": "https://example.com"}
    )

    assert result["status"] == "success"
    assert result["tool_name"] == "browser_scraper"
    assert result["page_loaded"] is True
    assert "snapshots" in result
    assert "llm_summary" in result


def test_browser_agent_error_handling():
    agent = BrowserAgent()
    result = agent.execute_tool("create_browser_tool", {"target_url": "invalid_url"})

    assert result["status"] == "error"
    assert (
        "Invalid URL" in result["message"]
    )  # Assuming the agent returns a message on error
