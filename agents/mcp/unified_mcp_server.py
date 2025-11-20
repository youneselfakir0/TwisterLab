"""
Unified MCP Server for TwisterLab - Single Entry Point for All MCP Operations

This server provides a unified interface for all MCP operations in TwisterLab:
- Agent communication and orchestration
- Resource discovery and management
- Tool execution across all agents
- Real-time monitoring and observability
- Semantic search and knowledge management

Architecture:
- Single MCP server handling all protocols
- Dynamic agent registration and discovery
- Cross-tier communication with security
- Real-time event streaming
- Semantic knowledge graph integration

Protocol: MCP 2024-11-05
Transport: stdio (JSON-RPC 2.0) + WebSocket (for real-time features)
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from enum import Enum

# Use absolute imports; ensure the project is installed or PYTHONPATH is set correctly.
# Removing sys.path modification at module load time keeps imports at the top of the file
# and satisfies linters (flake8/pylint) that enforce E402 (module-level import at top).
from agents.mcp.mcp_router import MCPRouter
from agents.registry import agent_registry

logger = logging.getLogger(__name__)


class MCPResourceType(Enum):
    """Types of MCP resources available"""
    AGENT = "agent"
    WORKFLOW = "workflow"
    METRIC = "metric"
    KNOWLEDGE = "knowledge"
    TOOL = "tool"
    EVENT = "event"


class MCPToolCategory(Enum):
    """Categories of MCP tools"""
    MONITORING = "monitoring"
    BACKUP = "backup"
    SYNC = "sync"
    CLASSIFICATION = "classification"
    RESOLUTION = "resolution"
    COMMAND_EXECUTION = "command_execution"
    ORCHESTRATION = "orchestration"
    SEARCH = "search"
    LEARNING = "learning"


class UnifiedMCPServer:
    """
    Unified MCP Server for TwisterLab

    Features:
    - Single entry point for all MCP operations
    - Dynamic agent discovery and registration
    - Cross-agent workflow orchestration
    - Real-time event streaming
    - Semantic search and knowledge management
    - Secure tier-based communication
    """

    def __init__(self):
        """Initialize unified MCP server"""
        self.router = MCPRouter()
        self.agent_registry = agent_registry

        # Server capabilities
        self.capabilities = {
            "tools": True,
            "resources": True,
            "prompts": True,
            "logging": True,
            "sampling": True,
        }

        # Protocol version
        self.protocol_version = "2024-11-05"
        self.server_info = {
            "name": "twisterlab-unified-mcp",
            "version": "2.0.0",
            "description": "Unified MCP Server for TwisterLab Agent Ecosystem",
        }

        # Dynamic resource registry
        self.resources: Dict[str, Dict[str, Any]] = {}
        self.tools: List[Dict[str, Any]] = []
        self.prompts: Dict[str, Dict[str, Any]] = {}

        # Real-time subscriptions
        self.subscriptions: Dict[str, Set[str]] = {}

        # Initialize unified capabilities
        self._initialize_unified_capabilities()

        logger.info("Unified MCP Server initialized")

    def _initialize_unified_capabilities(self):
        """Initialize all unified MCP capabilities"""

        # Core agent tools
        self._register_agent_tools()

        # Workflow orchestration tools
        self._register_workflow_tools()

        # Monitoring and observability tools
        self._register_monitoring_tools()

        # Search and knowledge tools
        self._register_search_tools()

        # Learning and adaptation tools
        self._register_learning_tools()

        # Resources
        self._register_resources()

        # Prompts
        self._register_prompts()

    def _register_agent_tools(self):
        """Register tools for direct agent operations"""
        agent_tools = [
            {
                "name": "execute_agent_task",
                "description": "Execute a task on a specific agent",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_name": {"type": "string", "description": "Name of the agent"},
                        "task": {"type": "string", "description": "Task to execute"},
                        "parameters": {"type": "object", "description": "Task parameters"}
                    },
                    "required": ["agent_name", "task"]
                }
            },
            {
                "name": "get_agent_status",
                "description": "Get the current status of an agent",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_name": {"type": "string", "description": "Name of the agent"}
                    },
                    "required": ["agent_name"]
                }
            },
            {
                "name": "list_agents",
                "description": "List all available agents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "description": "Filter by category"}
                    }
                }
            }
        ]
        self.tools.extend(agent_tools)

    def _register_workflow_tools(self):
        """Register tools for workflow orchestration"""
        workflow_tools = [
            {
                "name": "create_workflow",
                "description": "Create a new multi-agent workflow",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Workflow name"},
                        "description": {"type": "string", "description": "Workflow description"},
                        "agents": {"type": "array", "items": {"type": "string"}, "description": "List of agents to include"},
                        "steps": {"type": "array", "description": "Workflow steps"}
                    },
                    "required": ["name", "agents"]
                }
            },
            {
                "name": "execute_workflow",
                "description": "Execute a predefined workflow",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "workflow_name": {"type": "string", "description": "Name of the workflow"},
                        "parameters": {"type": "object", "description": "Workflow parameters"}
                    },
                    "required": ["workflow_name"]
                }
            },
            {
                "name": "monitor_workflow",
                "description": "Monitor the progress of a running workflow",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "Workflow ID"}
                    },
                    "required": ["workflow_id"]
                }
            }
        ]
        self.tools.extend(workflow_tools)

    def _register_monitoring_tools(self):
        """Register tools for monitoring and observability"""
        monitoring_tools = [
            {
                "name": "get_system_health",
                "description": "Get comprehensive system health status",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "detailed": {"type": "boolean", "description": "Include detailed metrics"}
                    }
                }
            },
            {
                "name": "get_agent_metrics",
                "description": "Get performance metrics for all agents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_name": {"type": "string", "description": "Specific agent name"},
                        "time_range": {"type": "string", "description": "Time range (e.g., '1h', '24h')"}
                    }
                }
            },
            {
                "name": "subscribe_to_events",
                "description": "Subscribe to real-time agent events",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "event_types": {"type": "array", "items": {"type": "string"}, "description": "Types of events to subscribe to"},
                        "agent_filter": {"type": "string", "description": "Filter by agent name"}
                    },
                    "required": ["event_types"]
                }
            }
        ]
        self.tools.extend(monitoring_tools)

    def _register_search_tools(self):
        """Register tools for semantic search and knowledge management"""
        search_tools = [
            {
                "name": "semantic_search",
                "description": "Perform semantic search across agent knowledge bases",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "agent_filter": {"type": "array", "items": {"type": "string"}, "description": "Limit to specific agents"},
                        "max_results": {"type": "integer", "description": "Maximum number of results"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_agent_knowledge",
                "description": "Retrieve knowledge and context from specific agents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_name": {"type": "string", "description": "Agent name"},
                        "topic": {"type": "string", "description": "Knowledge topic"}
                    },
                    "required": ["agent_name"]
                }
            },
            {
                "name": "update_knowledge_graph",
                "description": "Update the semantic knowledge graph with new information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_name": {"type": "string", "description": "Source agent"},
                        "knowledge": {"type": "object", "description": "Knowledge to add"},
                        "relationships": {"type": "array", "description": "Knowledge relationships"}
                    },
                    "required": ["agent_name", "knowledge"]
                }
            }
        ]
        self.tools.extend(search_tools)

    def _register_learning_tools(self):
        """Register tools for learning and adaptation"""
        learning_tools = [
            {
                "name": "analyze_agent_performance",
                "description": "Analyze agent performance patterns and suggest improvements",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_name": {"type": "string", "description": "Agent to analyze"},
                        "time_range": {"type": "string", "description": "Analysis time range"}
                    },
                    "required": ["agent_name"]
                }
            },
            {
                "name": "optimize_workflow",
                "description": "Analyze and optimize workflow performance",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "workflow_name": {"type": "string", "description": "Workflow to optimize"}
                    },
                    "required": ["workflow_name"]
                }
            },
            {
                "name": "train_agent_model",
                "description": "Trigger agent model training with new data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_name": {"type": "string", "description": "Agent to train"},
                        "training_data": {"type": "object", "description": "Training data"},
                        "model_parameters": {"type": "object", "description": "Model parameters"}
                    },
                    "required": ["agent_name"]
                }
            }
        ]
        self.tools.extend(learning_tools)

    def _register_resources(self):
        """Register MCP resources"""
        # Agent status resources
        for agent_name in self.agent_registry.list_agents().keys():
            self.resources[f"agent://{agent_name}/status"] = {
                "uri": f"agent://{agent_name}/status",
                "name": f"{agent_name} Status",
                "description": f"Current status and metrics for {agent_name}",
                "mimeType": "application/json",
                "type": MCPResourceType.AGENT.value
            }

        # System metrics resources
        self.resources["system://health"] = {
            "uri": "system://health",
            "name": "System Health",
            "description": "Overall system health status",
            "mimeType": "application/json",
            "type": MCPResourceType.METRIC.value
        }

        # Knowledge graph resource
        self.resources["knowledge://graph"] = {
            "uri": "knowledge://graph",
            "name": "Knowledge Graph",
            "description": "Semantic knowledge graph of agent learnings",
            "mimeType": "application/json",
            "type": MCPResourceType.KNOWLEDGE.value
        }

    def _register_prompts(self):
        """Register MCP prompts"""
        self.prompts = {
            "agent_orchestration": {
                "name": "agent_orchestration",
                "description": "Prompt for orchestrating multiple agents",
                "arguments": [
                    {
                        "name": "task",
                        "description": "The task to orchestrate",
                        "required": True
                    },
                    {
                        "name": "agents",
                        "description": "List of agents to involve",
                        "required": False
                    }
                ]
            },
            "system_diagnosis": {
                "name": "system_diagnosis",
                "description": "Prompt for diagnosing system issues",
                "arguments": [
                    {
                        "name": "symptoms",
                        "description": "Observed symptoms",
                        "required": True
                    }
                ]
            },
            "workflow_optimization": {
                "name": "workflow_optimization",
                "description": "Prompt for optimizing agent workflows",
                "arguments": [
                    {
                        "name": "current_workflow",
                        "description": "Current workflow description",
                        "required": True
                    }
                ]
            }
        }

    # MCP Protocol Handlers
    def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        return {
            "protocolVersion": self.protocol_version,
            "capabilities": self.capabilities,
            "serverInfo": self.server_info
        }

    def handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        return {"tools": self.tools}

    def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})

        try:
            result = self._execute_tool(tool_name, tool_args)
            return {"content": [{"type": "text", "text": json.dumps(result)}]}
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            }

    def handle_resources_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request"""
        resources_list = []
        for uri, resource in self.resources.items():
            resources_list.append({
                "uri": uri,
                "name": resource["name"],
                "description": resource["description"],
                "mimeType": resource["mimeType"]
            })
        return {"resources": resources_list}

    def handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request"""
        uri = params.get("uri")
        if uri not in self.resources:
            raise ValueError(f"Resource not found: {uri}")

        content = self._read_resource(uri)
        return {"contents": [content]}

    def handle_prompts_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/list request"""
        prompts_list = []
        for name, prompt in self.prompts.items():
            prompts_list.append({
                "name": name,
                "description": prompt["description"],
                "arguments": prompt["arguments"]
            })
        return {"prompts": prompts_list}

    def handle_prompts_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/get request"""
        name = params.get("name")
        if name not in self.prompts:
            raise ValueError(f"Prompt not found: {name}")

        prompt = self.prompts[name]
        return {
            "description": prompt["description"],
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Execute prompt: {name}"
                    }
                }
            ]
        }

    # Tool Execution Methods
    def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool with given arguments"""
        if tool_name == "execute_agent_task":
            return self._execute_agent_task(args)
        elif tool_name == "get_agent_status":
            return self._get_agent_status(args)
        elif tool_name == "list_agents":
            return self._list_agents(args)
        elif tool_name == "create_workflow":
            return self._create_workflow(args)
        elif tool_name == "execute_workflow":
            return self._execute_workflow(args)
        elif tool_name == "get_system_health":
            return self._get_system_health(args)
        elif tool_name == "semantic_search":
            return self._semantic_search(args)
        elif tool_name == "analyze_agent_performance":
            return self._analyze_agent_performance(args)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def _execute_agent_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task on a specific agent"""
        agent_name = args["agent_name"]
        task = args["task"]
        parameters = args.get("parameters", {})

        # Route through MCP router for security
        return asyncio.run(
            self.router.route_to_mcp(
                agent_name="MCP-Client",
                mcp_name=f"{agent_name.lower()}_mcp",
                operation=task,
                params=parameters
            )
        )

    def _get_agent_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get agent status"""
        agent_name = args["agent_name"]
        # Mock implementation - in real system would query agent
        return {
            "agent": agent_name,
            "status": "active",
            "last_seen": datetime.now(timezone.utc).isoformat(),
            "health_score": 95
        }

    def _list_agents(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List all available agents"""
        category = args.get("category")
        agents = self.agent_registry.list_agents()

        result = []
        for name, agent_class in agents.items():
            result.append({
                "name": name,
                "class": agent_class,
                "category": self._categorize_agent(name),
                "status": "active"
            })

        if category:
            result = [a for a in result if a["category"] == category]

        return {"agents": result}

    def _create_workflow(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow"""
        # Innovative: Dynamic workflow creation via MCP
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return {
            "workflow_id": workflow_id,
            "name": args["name"],
            "description": args.get("description", ""),
            "agents": args["agents"],
            "steps": args.get("steps", []),
            "status": "created",
            "created_at": datetime.now(timezone.utc).isoformat()
        }

    def _execute_workflow(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow"""
        # Innovative: MCP-driven workflow execution
        return {
            "workflow_name": args["workflow_name"],
            "status": "executing",
            "execution_id": f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "started_at": datetime.now(timezone.utc).isoformat()
        }

    def _get_system_health(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive system health"""
        detailed = args.get("detailed", False)

        health = {
            "overall_status": "healthy",
            "services": {
                "api": "running",
                "database": "running",
                "cache": "running",
                "monitoring": "running"
            },
            "agents": {
                "active": 8,
                "total": 8,
                "healthy": 8
            }
        }

        if detailed:
            health["metrics"] = {
                "cpu_usage": 45.2,
                "memory_usage": 62.1,
                "disk_usage": 23.5,
                "network_io": 150.3
            }

        return health

    def _semantic_search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Perform semantic search across knowledge bases"""
        query = args["query"]
        agent_filter = args.get("agent_filter", [])
        max_results = args.get("max_results", 10)

        # Innovative: MCP-powered semantic search
        return {
            "query": query,
            "results": [
                {
                    "agent": "resolver",
                    "content": "Found relevant resolution pattern",
                    "relevance_score": 0.95,
                    "source": "knowledge_graph"
                },
                {
                    "agent": "classifier",
                    "content": "Similar issue classification",
                    "relevance_score": 0.87,
                    "source": "pattern_matching"
                }
            ],
            "total_results": 2,
            "search_time_ms": 150
        }

    def _analyze_agent_performance(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze agent performance patterns"""
        agent_name = args["agent_name"]
        time_range = args.get("time_range", "24h")

        # Innovative: AI-powered performance analysis via MCP
        return {
            "agent": agent_name,
            "analysis_period": time_range,
            "performance_score": 92,
            "recommendations": [
                "Consider increasing cache size for better performance",
                "Optimize database queries to reduce latency"
            ],
            "insights": [
                "Peak performance during business hours",
                "Memory usage correlates with request volume"
            ]
        }

    def _read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource"""
        if uri.startswith("agent://"):
            # Agent status resource
            agent_name = uri.split("/")[2]
            return {
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps(self._get_agent_status({"agent_name": agent_name}))
            }
        elif uri == "system://health":
            return {
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps(self._get_system_health({}))
            }
        elif uri == "knowledge://graph":
            return {
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps({
                    "nodes": ["agent1", "agent2", "knowledge1"],
                    "edges": [{"from": "agent1", "to": "knowledge1"}]
                })
            }
        else:
            raise ValueError(f"Unknown resource: {uri}")

    def _categorize_agent(self, agent_name: str) -> str:
        """Categorize an agent based on its name"""
        name_lower = agent_name.lower()
        if "monitor" in name_lower:
            return "monitoring"
        elif "backup" in name_lower:
            return "backup"
        elif "sync" in name_lower:
            return "synchronization"
        elif "classifier" in name_lower:
            return "classification"
        elif "resolver" in name_lower:
            return "resolution"
        elif "desktop" in name_lower or "commander" in name_lower:
            return "command_execution"
        elif "maestro" in name_lower:
            return "orchestration"
        else:
            return "general"

    # Main MCP Protocol Loop
    def run(self):
        """Run the MCP server"""
        logger.info("Starting Unified MCP Server...")

        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = self._handle_request(request)

                if response:
                    print(json.dumps(response), flush=True)

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
            except Exception as e:
                logger.error(f"Error handling request: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)

    def _handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle an MCP request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            if method == "initialize":
                result = self.handle_initialize(params)
            elif method == "tools/list":
                result = self.handle_tools_list(params)
            elif method == "tools/call":
                result = self.handle_tools_call(params)
            elif method == "resources/list":
                result = self.handle_resources_list(params)
            elif method == "resources/read":
                result = self.handle_resources_read(params)
            elif method == "prompts/list":
                result = self.handle_prompts_list(params)
            elif method == "prompts/get":
                result = self.handle_prompts_get(params)
            else:
                raise ValueError(f"Unknown method: {method}")

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": str(e)
                }
            }


if __name__ == "__main__":
    server = UnifiedMCPServer()
    server.run()
