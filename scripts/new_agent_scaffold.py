import json
import os


def create_agent_scaffold(agent_name, llm_backend):
    # Define the scaffold directory
    scaffold_dir = os.path.join("scaffold", agent_name)

    # Create the scaffold directory
    os.makedirs(scaffold_dir, exist_ok=True)

    # Create agent.py
    agent_content = f"""class {agent_name}:
    def __init__(self):
        pass

    def run(self):
        pass
"""
    with open(os.path.join(scaffold_dir, "agent.py"), "w") as f:
        f.write(agent_content)

    # Create test_agent.py
    test_content = f"""import pytest
from ..{agent_name.lower()} import {agent_name}

def test_{agent_name.lower()}():
    agent = {agent_name}()
    assert agent is not None
"""
    with open(os.path.join(scaffold_dir, "test_agent.py"), "w") as f:
        f.write(test_content)

    # Create twisterlang_sample.json
    sample_payload = {
        "twisterlang_version": "1.0",
        "correlation_id": "sample-correlation-id",
        "data": {
            "tool_name": "sample_tool",
            "target_url": "https://example.com",
            "llm_backend": llm_backend,
        },
    }
    with open(os.path.join(scaffold_dir, "twisterlang_sample.json"), "w") as f:
        json.dump(sample_payload, f, indent=4)

    print(f"Scaffold for {agent_name} created successfully at {scaffold_dir}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create a new agent scaffold.")
    parser.add_argument("--name", required=True, help="Name of the agent")
    parser.add_argument("--llm", required=True, help="LLM backend to use")

    args = parser.parse_args()
    create_agent_scaffold(args.name, args.llm)
