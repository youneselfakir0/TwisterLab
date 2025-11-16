#!/usr/bin/env python3
"""
Patch api/main.py to replace mock functions with real orchestrator calls.
"""
import re
import sys


def patch_api_main(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    print("Applying patches...")

    # 1. Add orchestrator import at the top (after other imports)
    if "from agents.orchestrator.autonomous_orchestrator import get_orchestrator" not in content:
        # Find the last import statement
        import_pattern = r"(from [^\n]+\nimport [^\n]+\n)"
        matches = list(re.finditer(import_pattern, content))
        if matches:
            last_import_pos = matches[-1].end()
            content = (
                content[:last_import_pos]
                + "\n# Real agent orchestrator\n"
                + "from agents.orchestrator.autonomous_orchestrator import get_orchestrator\n\n"
                + content[last_import_pos:]
            )
            print("  âœ“ Added orchestrator import")

    # 2. Replace the execute_agent_operation endpoint
    old_endpoint = r'@app\.post\("/api/v1/autonomous/agents/\{agent_name\}/execute"\)[^}]+async def execute_agent_operation\(agent_name: str, payload: Dict\[str, Any\]\):[^}]+?\n    # Mock routing logic.*?(?=\n@app\.|$)'

    new_endpoint = '''@app.post("/api/v1/autonomous/agents/{agent_name}/execute")
async def execute_agent_operation(agent_name: str, payload: Dict[str, Any]):
    """
    Execute an agent operation using the real orchestrator.
    
    Args:
        agent_name: Name of the agent (e.g., 'MonitoringAgent')
        payload: Operation payload with 'operation' and optional 'context'
    
    Returns:
        Result from the real agent execution
    """
    try:
        # Get orchestrator instance
        orchestrator = await get_orchestrator()
        
        # Map API agent names to orchestrator agent names
        agent_mapping = {
            "monitoringagent": "monitoring",
            "backupagent": "backup",
            "syncagent": "sync",
            "classifieragent": "classifier",
            "resolveragent": "resolver",
            "desktopcommanderagent": "desktop_commander",
            "maestroorchestratoragent": "maestro",
        }
        
        orchestrator_agent_name = agent_mapping.get(agent_name.lower())
        
        if not orchestrator_agent_name:
            return {
                "agent": agent_name,
                "status": "error",
                "error": f"Unknown agent: {agent_name}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Extract operation and context from payload
        operation = payload.get("operation", "health_check")
        context = payload.get("context", {})
        
        # Execute real agent operation via orchestrator
        result = await orchestrator.execute_agent_operation(
            orchestrator_agent_name,
            operation,
            context
        )
        
        return {
            "agent": agent_name,
            "operation": operation,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
    
    except Exception as e:
        return {
            "agent": agent_name,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
'''

    # Try to replace the endpoint
    if re.search(old_endpoint, content, re.DOTALL):
        content = re.sub(old_endpoint, new_endpoint, content, flags=re.DOTALL)
        print("  âœ“ Replaced execute_agent_operation endpoint")
    else:
        # Fallback: find and replace more aggressively
        # Find the endpoint definition
        endpoint_start = content.find('@app.post("/api/v1/autonomous/agents/{agent_name}/execute")')
        if endpoint_start != -1:
            # Find the next endpoint or end of file
            next_endpoint = content.find("\n@app.", endpoint_start + 1)
            if next_endpoint == -1:
                next_endpoint = len(content)

            # Replace the section
            content = content[:endpoint_start] + new_endpoint + "\n" + content[next_endpoint:]
            print("  âœ“ Replaced execute_agent_operation endpoint (fallback method)")

    # 3. Remove mock functions
    mock_functions = [
        "async def execute_monitoring_agent",
        "async def execute_backup_agent",
        "async def execute_sync_agent",
    ]

    for mock_func in mock_functions:
        # Find and remove each mock function
        pattern = (
            r"\n\n"
            + re.escape(mock_func)
            + r"\(.*?\):[^}]+?(?=\n\n(?:async def |@app\.|C:\TwisterLab\patch_api_main_real_agents.ps1))"
        )
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, "", content, flags=re.DOTALL)
            print(f"  âœ“ Removed {mock_func}()")

    # Write patched content
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\nâœ“ Patch applied successfully!")
    print(f"  Original: {input_file}")
    print(f"  Patched:  {output_file}")

    return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: patch_script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if patch_api_main(input_file, output_file):
        sys.exit(0)
    else:
        sys.exit(1)
