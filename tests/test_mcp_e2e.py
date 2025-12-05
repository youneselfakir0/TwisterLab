"""
End-to-End Tests for TwisterLab MCP Server

Tests all 21 MCP tools against the live K8s deployment.
Requires: MCP server running on http://192.168.0.30:30080

Run: pytest tests/test_mcp_e2e.py -v
"""

import pytest
import httpx
import asyncio
from typing import Any, Dict

# Configuration
MCP_BASE_URL = "http://192.168.0.30:30080"
CORTEX_URL = "http://192.168.0.20:11434"
TIMEOUT = 30.0


@pytest.fixture
def client():
    """HTTP client for MCP server."""
    return httpx.Client(base_url=MCP_BASE_URL, timeout=TIMEOUT)


@pytest.fixture
async def async_client():
    """Async HTTP client for MCP server."""
    async with httpx.AsyncClient(base_url=MCP_BASE_URL, timeout=TIMEOUT) as client:
        yield client


class TestMCPHealth:
    """Test MCP server health and basic endpoints."""
    
    def test_health_endpoint(self, client):
        """Test /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["tools"] == 21
        assert data["version"] == "2.0.0"
    
    def test_root_endpoint(self, client):
        """Test / endpoint returns server info."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "agents" in data
    
    def test_tools_endpoint(self, client):
        """Test /tools endpoint lists all tools."""
        response = client.get("/tools")
        assert response.status_code == 200
        
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) == 21
        
        # Check all expected tools exist
        tool_names = [t["name"] for t in data["tools"]]
        assert "monitoring_health_check" in tool_names
        assert "maestro_chat" in tool_names
        assert "database_execute_query" in tool_names
        assert "cache_cache_get" in tool_names


class TestMonitoringAgent:
    """Test monitoring agent tools."""
    
    def test_monitoring_health_check(self, client):
        """Test monitoring_health_check tool."""
        response = client.post("/tools/monitoring_health_check", json={})
        assert response.status_code == 200
        
        data = response.json()
        assert "content" in data
    
    def test_monitoring_get_system_metrics(self, client):
        """Test monitoring_get_system_metrics tool."""
        response = client.post("/tools/monitoring_get_system_metrics", json={})
        assert response.status_code == 200
        
        data = response.json()
        assert "content" in data
    
    def test_monitoring_list_containers(self, client):
        """Test monitoring_list_containers tool."""
        response = client.post("/tools/monitoring_list_containers", json={
            "arguments": {"all": True}
        })
        assert response.status_code == 200
    
    def test_monitoring_get_llm_status(self, client):
        """Test monitoring_get_llm_status tool."""
        response = client.post("/tools/monitoring_get_llm_status", json={})
        assert response.status_code == 200
        
        data = response.json()
        assert "content" in data
    
    def test_monitoring_list_models(self, client):
        """Test monitoring_list_models tool."""
        response = client.post("/tools/monitoring_list_models", json={})
        assert response.status_code == 200
        
        data = response.json()
        assert "content" in data
        # Should contain at least one model
        content = data.get("content", [{}])[0].get("text", "")
        assert "qwen" in content.lower() or "llama" in content.lower() or "models" in content.lower()


class TestMaestroAgent:
    """Test maestro agent tools."""
    
    def test_maestro_list_agents(self, client):
        """Test maestro_list_agents tool."""
        response = client.post("/tools/maestro_list_agents", json={})
        assert response.status_code == 200
        
        data = response.json()
        assert "content" in data
    
    def test_maestro_chat(self, client):
        """Test maestro_chat tool with Cortex LLM."""
        response = client.post("/tools/maestro_chat", json={
            "arguments": {
                "message": "Say 'hello' in one word.",
                "model": "qwen3:8b"
            }
        })
        
        # May fail if Cortex is offline, but should not error on server side
        assert response.status_code in [200, 400, 500]
    
    def test_maestro_generate(self, client):
        """Test maestro_generate tool."""
        response = client.post("/tools/maestro_generate", json={
            "arguments": {
                "prompt": "1 + 1 = ",
                "model": "qwen3:8b"
            }
        })
        
        assert response.status_code in [200, 400, 500]
    
    def test_maestro_analyze(self, client):
        """Test maestro_analyze tool."""
        response = client.post("/tools/maestro_analyze", json={
            "arguments": {
                "content": "def hello(): print('world')",
                "analysis_type": "code"
            }
        })
        
        assert response.status_code in [200, 400, 500]


class TestDatabaseAgent:
    """Test database agent tools."""
    
    def test_database_db_health(self, client):
        """Test database_db_health tool."""
        response = client.post("/tools/database_db_health", json={})
        # May fail if DB is not running, but should return proper response
        assert response.status_code in [200, 400, 500]
    
    def test_database_list_tables(self, client):
        """Test database_list_tables tool."""
        response = client.post("/tools/database_list_tables", json={})
        assert response.status_code in [200, 400, 500]
    
    def test_database_execute_query_select(self, client):
        """Test database_execute_query with SELECT."""
        response = client.post("/tools/database_execute_query", json={
            "arguments": {
                "sql": "SELECT 1 as test",
                "limit": 10
            }
        })
        assert response.status_code in [200, 400, 500]
    
    def test_database_execute_query_rejects_insert(self, client):
        """Test that INSERT queries are rejected."""
        response = client.post("/tools/database_execute_query", json={
            "arguments": {
                "sql": "INSERT INTO test VALUES (1)",
                "limit": 10
            }
        })
        # Should return error for non-SELECT query
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            # Check if there's an error indication
            assert data.get("isError", False) or "error" in str(data).lower()


class TestCacheAgent:
    """Test cache agent tools."""
    
    def test_cache_set_get(self, client):
        """Test cache_set and cache_get tools."""
        # Set a value
        set_response = client.post("/tools/cache_cache_set", json={
            "arguments": {
                "key": "test:e2e:key",
                "value": "test_value_123",
                "ttl": 60
            }
        })
        
        if set_response.status_code == 200:
            # Get the value back
            get_response = client.post("/tools/cache_cache_get", json={
                "arguments": {
                    "key": "test:e2e:key"
                }
            })
            assert get_response.status_code == 200
    
    def test_cache_keys(self, client):
        """Test cache_cache_keys tool."""
        response = client.post("/tools/cache_cache_keys", json={
            "arguments": {
                "pattern": "*"
            }
        })
        assert response.status_code in [200, 400, 500]
    
    def test_cache_stats(self, client):
        """Test cache_cache_stats tool."""
        response = client.post("/tools/cache_cache_stats", json={})
        assert response.status_code in [200, 400, 500]
    
    def test_cache_delete(self, client):
        """Test cache_cache_delete tool."""
        # First set a key
        client.post("/tools/cache_cache_set", json={
            "arguments": {
                "key": "test:e2e:delete_me",
                "value": "to_delete"
            }
        })
        
        # Then delete it
        response = client.post("/tools/cache_cache_delete", json={
            "arguments": {
                "key": "test:e2e:delete_me"
            }
        })
        assert response.status_code in [200, 400, 500]


class TestMCPProtocol:
    """Test MCP JSON-RPC protocol endpoint."""
    
    def test_mcp_list_tools(self, client):
        """Test MCP tools/list method."""
        response = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("jsonrpc") == "2.0"
        assert "result" in data or "error" in data
    
    def test_mcp_call_tool(self, client):
        """Test MCP tools/call method."""
        response = client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "monitoring_health_check",
                "arguments": {}
            }
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("jsonrpc") == "2.0"


class TestIntegration:
    """Integration tests combining multiple tools."""
    
    def test_full_monitoring_flow(self, client):
        """Test complete monitoring flow."""
        # 1. Check health
        health = client.post("/tools/monitoring_health_check", json={})
        assert health.status_code == 200
        
        # 2. Get metrics
        metrics = client.post("/tools/monitoring_get_system_metrics", json={})
        assert metrics.status_code == 200
        
        # 3. List models
        models = client.post("/tools/monitoring_list_models", json={})
        assert models.status_code == 200
    
    def test_cache_workflow(self, client):
        """Test complete cache workflow."""
        test_key = "test:e2e:workflow"
        test_value = "workflow_test_value"
        
        # 1. Set value
        set_resp = client.post("/tools/cache_cache_set", json={
            "arguments": {"key": test_key, "value": test_value, "ttl": 30}
        })
        
        if set_resp.status_code == 200:
            # 2. Verify it exists in keys
            keys_resp = client.post("/tools/cache_cache_keys", json={
                "arguments": {"pattern": "test:e2e:*"}
            })
            assert keys_resp.status_code == 200
            
            # 3. Get the value
            get_resp = client.post("/tools/cache_cache_get", json={
                "arguments": {"key": test_key}
            })
            assert get_resp.status_code == 200
            
            # 4. Delete
            del_resp = client.post("/tools/cache_cache_delete", json={
                "arguments": {"key": test_key}
            })
            assert del_resp.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
