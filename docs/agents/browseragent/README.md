# BrowserAgent Documentation

## Overview

The BrowserAgent is a specialized agent within the TwisterLab framework designed for web automation, scraping, and summarization tasks. It leverages Playwright for browser interactions and integrates with the Model Context Protocol (MCP) to provide a seamless experience for developers and users.

## Features

- **Web Automation**: Automate interactions with web pages, including clicking buttons, filling forms, and navigating between pages.
- **Data Scraping**: Extract relevant information from web pages for analysis or storage.
- **Summarization**: Generate summaries of web content using integrated AI models.
- **Integration with MCP**: Expose functionalities as tools that can be consumed by the IDE and other agents.

## Quickstart

### Prerequisites

- Ensure you have the TwisterLab environment set up and running.
- Install necessary dependencies for the BrowserAgent.

### Running the BrowserAgent

1. Start the TwisterLab API:
   ```bash
   python -m uvicorn src.twisterlab.api.main:app --reload --port 8000
   ```

2. Call the BrowserAgent via the MCP API:
   ```bash
   curl -X POST http://localhost:8000/api/v1/mcp/execute -H "Content-Type: application/json" -d '{"tool_name":"create_browser_tool","args":{"target_url":"https://example.com","tool_name":"scrape_home", "llm_backend":"ollama"}}'
   ```

## Configuration

The BrowserAgent can be configured through environment variables or configuration files. Ensure that the necessary settings for the browser tool and AI backend are specified.

## Testing

Unit tests for the BrowserAgent are located in the `tests/test_agents/test_browser_agent.py` file. Run the tests using:
```bash
pytest tests/test_agents/test_browser_agent.py
```

## Contribution

Contributions to the BrowserAgent are welcome! Please follow the project's contribution guidelines and ensure that all new features are accompanied by appropriate tests and documentation.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
