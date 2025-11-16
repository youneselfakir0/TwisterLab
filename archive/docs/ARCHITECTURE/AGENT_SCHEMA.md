# Agent Schema Compatibility Guide

**TwisterLab v1.0** - Multi-Framework Interoperability

---

## Table of Contents

1. [Overview](#overview)
2. [Supported Formats](#supported-formats)
3. [Microsoft Agent Framework](#microsoft-agent-framework)
4. [LangChain Agents](#langchain-agents)
5. [Semantic Kernel](#semantic-kernel)
6. [OpenAI Assistants API](#openai-assistants-api)
7. [Compatibility Matrix](#compatibility-matrix)
8. [CLI Usage](#cli-usage)
9. [Python API](#python-api)
10. [Examples](#examples)
11. [References](#references)

---

## Overview

TwisterLab agents can be exported to standard formats for interoperability with enterprise AI frameworks. This enables seamless integration with existing Microsoft, LangChain, and OpenAI ecosystems.

### Key Features

- **Native MCP Protocol**: Primary integration method
- **Microsoft Agent Framework**: Production-ready export
- **Multi-Framework Support**: LangChain, Semantic Kernel, OpenAI (planned v2.0)
- **Zero Dependencies**: No additional packages required
- **CLI & API**: Export via command-line or Python

---

## Supported Formats

| Format | Status | Use Case | Documentation |
|--------|--------|----------|---------------|
| **Microsoft Agent Framework** | ✅ **Production** | Azure AI Services integration | [Docs](https://learn.microsoft.com/azure/ai-services/agents/) |
| **LangChain** | ⚠️ Stub (v2.0) | LangChain ecosystem | [Docs](https://python.langchain.com/docs/modules/agents/) |
| **Semantic Kernel** | ⚠️ Stub (v2.0) | Microsoft SK integration | [Docs](https://learn.microsoft.com/semantic-kernel/) |
| **OpenAI Assistants** | ⚠️ Stub (v2.0) | OpenAI API compatibility | [Docs](https://platform.openai.com/docs/assistants/) |

### Status Legend

- ✅ **Production**: Fully implemented, tested, production-ready
- ⚠️ **Stub**: Basic structure implemented, full support planned for v2.0

---

## Microsoft Agent Framework

### Overview

Microsoft Agent Framework is the primary interoperability target for TwisterLab v1.0. Agents can be exported to this format for integration with Azure AI Services.

### Schema Format

Based on the official [Microsoft Agent Framework specification](https://learn.microsoft.com/azure/ai-services/agents/):

```json
{
  "id": "agent-identifier",
  "object": "agent",
  "created_at": 1730131200,
  "name": "Agent Display Name",
  "description": "Agent description and capabilities",
  "model": "model-name",
  "instructions": "System instructions for the agent",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "function_name",
        "description": "Function description",
        "parameters": {
          "type": "object",
          "properties": {...},
          "required": [...]
        }
      }
    }
  ],
  "metadata": {
    "role": "helpdesk",
    "temperature": 0.3,
    "framework": "twisterlab",
    "version": "1.0.0"
  }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique agent identifier (kebab-case) |
| `object` | string | Always "agent" |
| `created_at` | integer | Unix timestamp of creation |
| `name` | string | Human-readable agent name |
| `description` | string | Agent purpose and capabilities |
| `model` | string | LLM model (e.g., "gpt-4", "llama-3.2") |
| `instructions` | string | System prompt/instructions |
| `tools` | array | Available functions/tools |
| `metadata` | object | Additional metadata |

### Tool Schema

Tools follow the OpenAPI function calling format:

```json
{
  "type": "function",
  "function": {
    "name": "reset_password",
    "description": "Reset user password in Active Directory",
    "parameters": {
      "type": "object",
      "properties": {
        "username": {
          "type": "string",
          "description": "Username to reset password for"
        }
      },
      "required": ["username"]
    }
  }
}
```

### Export Example

```bash
# Export IT Helpdesk Agent to Microsoft format
twisterlab export-agent helpdesk-resolver --format microsoft --output helpdesk.json
```

---

## LangChain Agents

### Overview

LangChain support is planned for v2.0. Current implementation provides stub format.

### Schema Format (Stub)

```json
{
  "_format": "langchain",
  "_status": "stub",
  "_note": "Full LangChain compatibility planned for v2.0",
  "name": "agent_name",
  "description": "Agent description",
  "llm": {
    "model_name": "llama-3.2",
    "temperature": 0.7
  },
  "tools": ["tool1", "tool2"],
  "agent_type": "zero-shot-react-description",
  "memory": null
}
```

### Roadmap

**v2.0 Features**:
- Full LangChain tool conversion
- Agent executor compatibility
- Memory integration
- Chain composition

---

## Semantic Kernel

### Overview

Semantic Kernel support is planned for v2.0. Current implementation provides stub format.

### Schema Format (Stub)

```json
{
  "_format": "semantic-kernel",
  "_status": "stub",
  "_note": "Full Semantic Kernel compatibility planned for v2.0",
  "name": "SkillName",
  "description": "Skill description",
  "functions": [
    {
      "name": "function_name",
      "description": "Function description",
      "parameters": {...}
    }
  ],
  "settings": {
    "model": "llama-3.2",
    "temperature": 0.7
  }
}
```

### Roadmap

**v2.0 Features**:
- Full SK plugin compatibility
- Semantic function support
- Planner integration
- Native function mapping

---

## OpenAI Assistants API

### Overview

OpenAI Assistants API support is planned for v2.0. Current implementation provides stub format.

### Schema Format (Stub)

```json
{
  "_format": "openai-assistant",
  "_status": "stub",
  "_note": "Full OpenAI Assistants API compatibility planned for v2.0",
  "id": "asst_agent_name",
  "object": "assistant",
  "created_at": 1730131200,
  "name": "Assistant Name",
  "description": "Assistant description",
  "model": "gpt-4",
  "instructions": "System instructions",
  "tools": [...],
  "file_ids": [],
  "metadata": {...}
}
```

### Roadmap

**v2.0 Features**:
- OpenAI API compatibility
- File upload support
- Code interpreter integration
- Retrieval augmented generation (RAG)

---

## Compatibility Matrix

### TwisterLab vs Microsoft Agent Framework

| TwisterLab Feature | Microsoft Equivalent | Compatibility | Notes |
|-------------------|---------------------|---------------|-------|
| Agent name | `id` | ✅ Full | Direct mapping |
| Display name | `name` | ✅ Full | Direct mapping |
| Instructions | `instructions` | ✅ Full | System prompt |
| Tools | `tools` | ✅ Full | OpenAPI function format |
| Model | `model` | ✅ Full | Model identifier |
| Metadata | `metadata` | ✅ Full | Extended metadata |
| MCP Protocol | N/A | ✅ Bridge | Via `microsoft_agent_bridge.py` |

### Framework Comparison

| Feature | TwisterLab | Microsoft | LangChain | Semantic Kernel | OpenAI |
|---------|-----------|-----------|-----------|-----------------|--------|
| **Agent Definition** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Tool/Function Calling** | ✅ MCP | ✅ Functions | ✅ Tools | ✅ Functions | ✅ Functions |
| **State Management** | ✅ Redis | ✅ Azure | ✅ Memory | ✅ Context | ✅ Threads |
| **Multi-Agent** | ✅ Maestro | ✅ Supported | ✅ Multi-agent | ✅ Planner | ⚠️ Limited |
| **Cost** | **$0** | $$$ | $ | $$$ | $$$ |

---

## CLI Usage

### Installation

```bash
# No installation needed - part of TwisterLab CLI
pip install -r requirements.txt  # Install dependencies only
```

### Commands

#### List Agents

```bash
twisterlab list-agents
```

Output:
```
📋 Available TwisterLab Agents
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Agent Name         ┃ Display Name         ┃ Role            ┃ Tools ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ helpdesk-resolver  │ IT Helpdesk Resolver │ helpdesk        │     3 │
│ classifier         │ Ticket Classifier    │ classifier      │     1 │
│ desktop-commander  │ Desktop Commander    │ desktop-command │     3 │
└────────────────────┴──────────────────────┴─────────────────┴───────┘
```

#### Export Agent

```bash
# Export to stdout (default: Microsoft format)
twisterlab export-agent helpdesk-resolver

# Export to file
twisterlab export-agent helpdesk-resolver --output config/agents/helpdesk.json

# Export to different format
twisterlab export-agent classifier --format langchain

# Export without pretty-printing
twisterlab export-agent desktop-commander --no-pretty
```

#### Show Agent Details

```bash
twisterlab show-agent helpdesk-resolver
```

#### Validate Schema

```bash
twisterlab validate-schema config/agent_schemas/helpdesk_resolver.json
```

#### List Formats

```bash
twisterlab formats
```

---

## Python API

### Basic Usage

```python
from agents.base import HelpdeskAgent, ClassifierAgent, DesktopCommanderAgent

# Create agent instance
agent = HelpdeskAgent()

# Export to Microsoft format
microsoft_schema = agent.to_schema("microsoft")

# Export to other formats
langchain_schema = agent.to_schema("langchain")
sk_schema = agent.to_schema("semantic-kernel")
openai_schema = agent.to_schema("openai")

# Save to file
agent.export_to_file("helpdesk_agent.json", format="microsoft")
```

### Custom Agent

```python
from agents.base import TwisterAgent
from typing import Any, Dict, Optional

class CustomAgent(TwisterAgent):
    def __init__(self):
        super().__init__(
            name="custom-agent",
            display_name="Custom Agent",
            description="My custom agent",
            role="custom",
            instructions="Custom instructions",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "custom_function",
                        "description": "A custom function",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "param1": {"type": "string"}
                            },
                            "required": ["param1"]
                        }
                    }
                }
            ],
            model="llama-3.2",
            temperature=0.5
        )

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        # Implementation
        return {"status": "success"}

# Export
agent = CustomAgent()
schema = agent.to_schema("microsoft")
```

### Programmatic Export

```python
import json
from pathlib import Path
from agents.base import HelpdeskAgent

# Create agent
agent = HelpdeskAgent()

# Export all formats
formats = ["microsoft", "langchain", "semantic-kernel", "openai"]
output_dir = Path("exports")
output_dir.mkdir(exist_ok=True)

for fmt in formats:
    schema = agent.to_schema(fmt)
    filepath = output_dir / f"helpdesk_agent_{fmt}.json"

    with open(filepath, 'w') as f:
        json.dump(schema, f, indent=2)

    print(f"Exported to {filepath}")
```

---

## Examples

### Example 1: IT Helpdesk Resolver (Microsoft Format)

**Export**:
```bash
twisterlab export-agent helpdesk-resolver --format microsoft --output helpdesk.json
```

**Output** ([helpdesk_resolver.json](../config/agent_schemas/helpdesk_resolver.json)):
```json
{
  "id": "helpdesk-resolver",
  "object": "agent",
  "name": "IT Helpdesk Resolver",
  "model": "llama-3.2",
  "instructions": "You are an IT Helpdesk Agent...",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "reset_password",
        "description": "Reset user password in Active Directory",
        "parameters": {...}
      }
    }
  ],
  "metadata": {
    "role": "helpdesk",
    "temperature": 0.3,
    "automation_rate": "60-70%"
  }
}
```

### Example 2: Ticket Classifier (Microsoft Format)

**Export**:
```bash
twisterlab export-agent classifier --format microsoft
```

**Output** ([classifier.json](../config/agent_schemas/classifier.json)):
```json
{
  "id": "classifier",
  "object": "agent",
  "name": "Ticket Classifier",
  "model": "deepseek-r1",
  "instructions": "You are a Ticket Classifier Agent...",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "classify_ticket",
        "parameters": {...}
      }
    }
  ],
  "metadata": {
    "accuracy_target": "95%"
  }
}
```

### Example 3: Desktop Commander (Microsoft Format)

**Export**:
```bash
twisterlab export-agent desktop-commander --output desktop_commander.json
```

**Output** ([desktop_commander.json](../config/agent_schemas/desktop_commander.json)):
```json
{
  "id": "desktop-commander",
  "object": "agent",
  "name": "Desktop Commander",
  "model": "llama-3.2",
  "instructions": "You are a Desktop Commander Agent...",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "execute_command",
        "description": "Execute command on remote desktop client",
        "parameters": {...}
      }
    }
  ],
  "metadata": {
    "security_level": "zero-trust"
  }
}
```

---

## References

### Official Documentation

#### Microsoft Agent Framework
- **Overview**: https://learn.microsoft.com/azure/ai-services/agents/
- **API Reference**: https://learn.microsoft.com/azure/ai-services/agents/reference
- **Quickstart**: https://learn.microsoft.com/azure/ai-services/agents/quickstart
- **GitHub**: https://github.com/microsoft/autogen

#### LangChain
- **Agents Documentation**: https://python.langchain.com/docs/modules/agents/
- **Agent Types**: https://python.langchain.com/docs/modules/agents/agent_types/
- **Tools**: https://python.langchain.com/docs/modules/agents/tools/
- **GitHub**: https://github.com/langchain-ai/langchain

#### Semantic Kernel
- **Overview**: https://learn.microsoft.com/semantic-kernel/overview/
- **Get Started**: https://learn.microsoft.com/semantic-kernel/get-started/
- **Plugins**: https://learn.microsoft.com/semantic-kernel/agents/plugins/
- **GitHub**: https://github.com/microsoft/semantic-kernel

#### OpenAI Assistants API
- **Overview**: https://platform.openai.com/docs/assistants/overview
- **API Reference**: https://platform.openai.com/docs/api-reference/assistants
- **Tools**: https://platform.openai.com/docs/assistants/tools
- **GitHub**: https://github.com/openai/openai-python

#### MCP Protocol
- **Specification**: https://spec.modelcontextprotocol.io/2024-11-05/
- **GitHub**: https://github.com/modelcontextprotocol/specification
- **Examples**: https://github.com/modelcontextprotocol/servers

### TwisterLab Documentation

- **Main Documentation**: [README.md](../README.md)
- **Architecture**: [.github/copilot-instructions.md](../.github/copilot-instructions.md)
- **Security**: [SECURITY.md](SECURITY.md)
- **API Documentation**: [API.md](API.md)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)

---

## FAQ

### Q: Which format should I use?

**A**: Use **Microsoft Agent Framework** format for production deployments. It's fully tested and supported.

### Q: Are LangChain/SK/OpenAI formats production-ready?

**A**: Not yet. These are stubs for v2.0. Use Microsoft format or native MCP protocol for production.

### Q: Can I convert between formats?

**A**: Yes, export the agent to your target format using the CLI or Python API.

### Q: Do I need additional dependencies?

**A**: No. Schema export requires no additional packages. Only Typer and Rich for CLI (already in requirements.txt).

### Q: How do I add my own agent?

**A**: Subclass `TwisterAgent`, implement `execute()`, and add to `AGENTS` registry in `cli/twisterlab.py`.

### Q: Where are the exported schemas stored?

**A**: Pre-generated schemas are in `config/agent_schemas/`. Export to any location using `--output`.

---

## Troubleshooting

### Issue: CLI command not found

**Solution**:
```bash
# Add to PATH or use full path
python cli/twisterlab.py export-agent helpdesk-resolver
```

### Issue: Import errors

**Solution**:
```bash
# Ensure you're in project root
cd /path/to/TwisterLab

# Run with Python module syntax
python -m cli.twisterlab export-agent helpdesk-resolver
```

### Issue: Schema validation fails

**Solution**: Check that the exported JSON matches the target format specification. Use `validate-schema` command.

---

## Contributing

To add support for a new format:

1. Add export method to `TwisterAgent` in `agents/base.py`:
   ```python
   def _to_new_format_schema(self) -> Dict[str, Any]:
       # Implementation
       pass
   ```

2. Update `to_schema()` method to include new format

3. Add format to `SUPPORTED_FORMATS` in `cli/twisterlab.py`

4. Update documentation

5. Add tests

---

**Last Updated**: 2025-10-28
**Version**: 1.0.0
**License**: Apache 2.0
