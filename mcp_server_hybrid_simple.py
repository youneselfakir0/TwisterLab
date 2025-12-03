#!/usr/bin/env python3
"""Minimal Hybrid MCP server for manual testing.

This script is intentionally minimal: it implements a JSON-RPC stdio loop
and responds to a very small subset of MCP methods so a client can
verify it can start the process and exchange messages.

It respects HYBRID_MODE, CORTEX_ENDPOINT and EDGESERVER_ENDPOINT environment
variables (reads them but does not connect to external services).

Usage:
  # in PowerShell
  $env:PYTHONPATH = 'src'; $env:HYBRID_MODE = 'true'; $env:CORTEX_ENDPOINT = 'http://192.168.0.20:11434'; $env:EDGESERVER_ENDPOINT = 'http://192.168.0.30:8000'; python mcp_server_hybrid_simple.py
"""
import json
import os
import sys
import logging
from typing import Any, Dict

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger("mcp.hybrid.simple")


def _initialize_response(request_id: Any) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "1.0",
            "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
            "serverInfo": {"name": "TwisterLab Hybrid Simple", "version": "0.1"},
        },
    }


def _tools_list_response(request_id: Any) -> Dict[str, Any]:
    tools = [
        {"name": "monitor_system_health", "description": "Minimal health tool", "inputSchema": {"type": "object"}},
    ]
    return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}


def _tools_call_response(request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    tool = params.get("name")
    if tool == "monitor_system_health":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "text", "text": "OK"}]}}
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": f"Unknown tool {tool}"}}


def main():
    logger.info("MCP HYBRID SIMPLE SERVER STARTING...")
    logger.info("Env: HYBRID_MODE=%s CORTEX_ENDPOINT=%s EDGESERVER_ENDPOINT=%s", os.getenv("HYBRID_MODE"), os.getenv("CORTEX_ENDPOINT"), os.getenv("EDGESERVER_ENDPOINT"))

    try:
        for raw in sys.stdin:
            raw = raw.strip()
            if not raw:
                continue

            try:
                req = json.loads(raw)
            except json.JSONDecodeError:
                logger.error("Invalid JSON received: %r", raw)
                continue

            method = req.get("method")
            req_id = req.get("id")
            if method == "initialize":
                resp = _initialize_response(req_id)
            elif method == "tools/list":
                resp = _tools_list_response(req_id)
            elif method == "tools/call":
                resp = _tools_call_response(req_id, req.get("params", {}))
            else:
                resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

            print(json.dumps(resp), flush=True)

    except KeyboardInterrupt:
        logger.info("MCP process interrupted, shutting down")
    except Exception as e:
        logger.exception("Unhandled exception in MCP stub: %s", e)


if __name__ == "__main__":
    main()
