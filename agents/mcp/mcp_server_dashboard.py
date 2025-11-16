#!/usr/bin/env python3
"""
TwisterLab Dashboard MCP Server
Monitoring dashboard for Continue IDE orchestration
Provides real-time status of API, Docker services, network, and agents
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

import httpx
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Server configuration
server = Server("twisterlab-dashboard")

# TwisterLab endpoints
API_BASE_URL = "http://192.168.0.30:8000"
PROMETHEUS_URL = "http://192.168.0.30:9090"
GRAFANA_URL = "http://192.168.0.30:3000"
TRAEFIK_URL = "http://192.168.0.30:8080"


class TwisterLabDashboard:
    """Dashboard for monitoring TwisterLab infrastructure"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_api_health(self) -> Dict[str, Any]:
        """Get TwisterLab API health status"""
        try:
            response = await self.client.get(f"{API_BASE_URL}/health")
            response.raise_for_status()
            data = response.json()
            return {
                "status": "healthy",
                "api": data,
                "endpoint": API_BASE_URL
            }
        except Exception as e:
            logger.error(f"API health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "endpoint": API_BASE_URL
            }

    async def get_agents_status(self) -> Dict[str, Any]:
        """Get status of all 7 Real agents"""
        try:
            response = await self.client.get(f"{API_BASE_URL}/agents/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Agents status failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agents": []
            }

    async def get_prometheus_targets(self) -> Dict[str, Any]:
        """Get Prometheus scrape targets status"""
        try:
            response = await self.client.get(f"{PROMETHEUS_URL}/api/v1/targets")
            response.raise_for_status()
            data = response.json()

            active_targets = data.get("data", {}).get("activeTargets", [])
            summary = {
                "total": len(active_targets),
                "up": sum(1 for t in active_targets if t.get("health") == "up"),
                "down": sum(1 for t in active_targets if t.get("health") == "down"),
                "targets": [
                    {
                        "job": t.get("labels", {}).get("job"),
                        "instance": t.get("labels", {}).get("instance"),
                        "health": t.get("health"),
                        "lastScrape": t.get("lastScrape")
                    }
                    for t in active_targets
                ]
            }
            return {
                "status": "healthy",
                "prometheus": summary,
                "endpoint": PROMETHEUS_URL
            }
        except Exception as e:
            logger.error(f"Prometheus check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "endpoint": PROMETHEUS_URL
            }

    async def get_traefik_services(self) -> Dict[str, Any]:
        """Get Traefik services and routes"""
        try:
            response = await self.client.get(f"{TRAEFIK_URL}/api/http/services")
            response.raise_for_status()
            services = response.json()

            summary = {
                "total": len(services),
                "services": [
                    {
                        "name": name,
                        "status": svc.get("status", "unknown"),
                        "serverStatus": svc.get("serverStatus", {})
                    }
                    for name, svc in services.items()
                ]
            }
            return {
                "status": "healthy",
                "traefik": summary,
                "endpoint": TRAEFIK_URL
            }
        except Exception as e:
            logger.error(f"Traefik check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "endpoint": TRAEFIK_URL
            }

    async def get_docker_services(self) -> Dict[str, Any]:
        """Get Docker Swarm services status via API"""
        try:
            # Use edgeserver SSH to query Docker
            import subprocess
            result = subprocess.run(
                ["ssh", "twister@192.168.0.30", "docker service ls --format '{{json .}}'"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                services = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        services.append(json.loads(line))

                return {
                    "status": "healthy",
                    "docker": {
                        "total": len(services),
                        "services": services
                    }
                }
            else:
                return {
                    "status": "error",
                    "error": result.stderr
                }
        except Exception as e:
            logger.error(f"Docker services check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def get_full_dashboard(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        results = await asyncio.gather(
            self.get_api_health(),
            self.get_agents_status(),
            self.get_prometheus_targets(),
            self.get_traefik_services(),
            self.get_docker_services(),
            return_exceptions=True
        )

        api_health, agents_status, prometheus, traefik, docker = results

        # Calculate overall health
        health_checks = [
            api_health.get("status") == "healthy",
            prometheus.get("status") == "healthy",
            traefik.get("status") == "healthy",
            docker.get("status") == "healthy"
        ]
        overall_health = "healthy" if all(health_checks) else "degraded" if any(health_checks) else "critical"

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": overall_health,
            "components": {
                "api": api_health,
                "agents": agents_status,
                "prometheus": prometheus,
                "traefik": traefik,
                "docker": docker
            },
            "summary": {
                "healthy": sum(health_checks),
                "total": len(health_checks),
                "uptime_percentage": (sum(health_checks) / len(health_checks)) * 100
            }
        }


# Global dashboard instance
dashboard = TwisterLabDashboard()


@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available dashboard resources"""
    return [
        Resource(
            uri="dashboard://status",
            name="TwisterLab Status",
            description="Current status of all TwisterLab components",
            mimeType="application/json"
        ),
        Resource(
            uri="dashboard://api",
            name="API Health",
            description="TwisterLab API health and status",
            mimeType="application/json"
        ),
        Resource(
            uri="dashboard://agents",
            name="Agents Status",
            description="Status of all 7 Real agents",
            mimeType="application/json"
        ),
        Resource(
            uri="dashboard://prometheus",
            name="Prometheus Targets",
            description="Prometheus scrape targets and metrics",
            mimeType="application/json"
        ),
        Resource(
            uri="dashboard://traefik",
            name="Traefik Services",
            description="Traefik routing and services",
            mimeType="application/json"
        ),
        Resource(
            uri="dashboard://docker",
            name="Docker Services",
            description="Docker Swarm services status",
            mimeType="application/json"
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read dashboard resource data"""
    logger.info(f"Reading resource: {uri}")

    if uri == "dashboard://status":
        data = await dashboard.get_full_dashboard()
    elif uri == "dashboard://api":
        data = await dashboard.get_api_health()
    elif uri == "dashboard://agents":
        data = await dashboard.get_agents_status()
    elif uri == "dashboard://prometheus":
        data = await dashboard.get_prometheus_targets()
    elif uri == "dashboard://traefik":
        data = await dashboard.get_traefik_services()
    elif uri == "dashboard://docker":
        data = await dashboard.get_docker_services()
    else:
        raise ValueError(f"Unknown resource URI: {uri}")

    return json.dumps(data, indent=2)


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available dashboard tools"""
    return [
        Tool(
            name="get_dashboard",
            description="Get complete TwisterLab infrastructure dashboard",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="check_api_health",
            description="Check TwisterLab API health status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_agents_status",
            description="Get status of all 7 Real agents",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_prometheus_targets",
            description="Get Prometheus monitoring targets",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_traefik_services",
            description="Get Traefik API Gateway services",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="restart_service",
            description="Restart a Docker Swarm service",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Name of the service to restart (e.g., twisterlab_api)"
                    }
                },
                "required": ["service_name"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle dashboard tool calls"""
    logger.info(f"Tool called: {name} with args: {arguments}")

    try:
        if name == "get_dashboard":
            result = await dashboard.get_full_dashboard()
        elif name == "check_api_health":
            result = await dashboard.get_api_health()
        elif name == "get_agents_status":
            result = await dashboard.get_agents_status()
        elif name == "get_prometheus_targets":
            result = await dashboard.get_prometheus_targets()
        elif name == "get_traefik_services":
            result = await dashboard.get_traefik_services()
        elif name == "restart_service":
            service_name = arguments.get("service_name")
            import subprocess
            cmd = f"docker service update --force {service_name}"
            result_proc = subprocess.run(
                ["ssh", "twister@192.168.0.30", cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            result = {
                "service": service_name,
                "status": "restarted" if result_proc.returncode == 0 else "failed",
                "output": result_proc.stdout,
                "error": result_proc.stderr
            }
        else:
            result = {"error": f"Unknown tool: {name}"}

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    except Exception as e:
        logger.error(f"Tool execution failed: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


async def main():
    """Run the MCP dashboard server"""
    logger.info("Starting TwisterLab Dashboard MCP Server")

    async with stdio_server() as (read_stream, write_stream):
        init_options = InitializationOptions(
            server_name="twisterlab-dashboard",
            server_version="1.0.0",
            capabilities=server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={}
            )
        )

        await server.run(
            read_stream,
            write_stream,
            init_options
        )


if __name__ == "__main__":
    asyncio.run(main())
