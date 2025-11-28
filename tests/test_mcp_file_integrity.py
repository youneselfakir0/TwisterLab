import os
from pathlib import Path


def test_mcp_files_have_no_nul_bytes():
    root = Path(__file__).resolve().parents[1]
    # Paths to check
    wrapper = root / 'src' / 'twisterlab' / 'agents' / 'mcp' / 'mcp_server_continue_sync.py'
    root_mcp = root / 'mcp_server_production.py'
    pkg_mcp = root / 'src' / 'twisterlab' / 'agents' / 'mcp' / 'mcp_server_production.py'

    for p in (wrapper, root_mcp, pkg_mcp):
        assert p.exists(), f"MCP file missing: {p}"
        data = p.read_bytes()
        assert b"\x00" not in data, f"File contains NUL bytes: {p}"


def test_wrapper_importable():
    # Ensure that the wrapper can import the MCP server class
    import sys
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    src_path = os.path.join(project_root, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    from twisterlab.agents.mcp import mcp_server_continue_sync as wrapper
    assert hasattr(wrapper, 'MCPServerContinue'), "Wrapper does not expose MCPServerContinue"
