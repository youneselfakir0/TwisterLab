"""
TwisterLab - Real Working Monitoring Agent (v2 - Unified)
Performs ACTUAL system monitoring with real metrics, aligned with the UnifiedAgentBase.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict

import psutil

from agents.base.unified_agent import AgentStatus, UnifiedAgentBase

logger = logging.getLogger(__name__)


class RealMonitoringAgent(UnifiedAgentBase):
    """
    Real monitoring agent that performs ACTUAL system checks. Inherits from UnifiedAgentBase.
    """

    def __init__(self):
        super().__init__(
            name="RealMonitoringAgent",
            version="2.0",
            description="Performs real system monitoring for health, services, ports, and GPU.",
        )
        # Thresholds for alerts
        self.thresholds = {"cpu_percent": 80, "memory_percent": 85, "disk_percent": 90}
        # Expected services - match Docker service names
        self.expected_services = [
            "twisterlab_api",
            "twisterlab_postgres",
            "twisterlab_redis",
            "twisterlab_prometheus",
            "twisterlab_grafana",
        ]
        # Expected ports
        self.expected_ports = {
            "8000": "API",
            "5432": "PostgreSQL",
            "6379": "Redis",
            "9090": "Prometheus",
            "3000": "Grafana",
            "11434": "Ollama",
        }
        # Map ports to hosts for container-to-container communication
        self.service_hosts = {
            "8000": "twisterlab_api",
            "5432": "twisterlab_postgres",
            "6379": "twisterlab_redis",
            "9090": "twisterlab_prometheus",
            "3000": "twisterlab_grafana",
            "11434": "ollama",
        }

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a monitoring operation based on the context.
        This method is called by the parent 'run' method, which handles status and error management.

        Args:
            context: Must contain an 'operation' key.
                Operations: health_check, check_services, check_ports, check_gpu, full_diagnostic

        Returns:
            A dictionary containing the monitoring results.
        """
        operation = context.get("operation", "health_check")
        logger.info(f"🔍 {self.name} executing: {operation}")

        if operation == "health_check":
            return await self._health_check(context)
        elif operation == "check_services":
            return await self._check_docker_services()
        elif operation == "check_ports":
            return await self._check_ports()
        elif operation == "check_gpu":
            return await self._check_nvidia_gpu()
        elif operation == "full_diagnostic":
            return await self._full_diagnostic()
        else:
            raise ValueError(f"Unknown operation for {self.name}: {operation}")

    async def _health_check(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Performs a REAL system health check using psutil."""
        logger.info("💓 Performing real health check...")
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net_io = psutil.net_io_counters()

        issues = []
        if cpu_percent > self.thresholds["cpu_percent"]:
            issues.append(f"High CPU usage: {cpu_percent}%")
        if memory.percent > self.thresholds["memory_percent"]:
            issues.append(f"High memory usage: {memory.percent}%")
        if disk.percent > self.thresholds["disk_percent"]:
            issues.append(f"High disk usage: {disk.percent}%")

        overall_status = "healthy" if not issues else "warning"

        result = {
            "status": "success",
            "health_status": overall_status,
            "issues": issues,
            "metrics": {
                "cpu_percent": round(cpu_percent, 2),
                "memory_percent": round(memory.percent, 2),
                "disk_percent": round(disk.percent, 2),
                "network_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                "network_received_mb": round(net_io.bytes_recv / (1024**2), 2),
                "processes": len(psutil.pids()),
            },
        }
        logger.info(f"✅ Health check complete: {overall_status}")
        return result

    async def _check_docker_services(self) -> Dict[str, Any]:
        """Checks the status of Docker services using the 'docker service ls' command."""
        logger.info("🐳 Checking Docker services...")
        try:
            process = await asyncio.create_subprocess_exec(
                "docker",
                "service",
                "ls",
                "--format",
                "{{.Name}}:{{.Replicas}}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise Exception(f"Docker command failed: {stderr.decode().strip()}")

            services = {}
            for line in stdout.decode().strip().split("\n"):
                if ":" in line:
                    name, replicas = line.split(":", 1)
                    current, desired = map(int, replicas.split("/"))
                    services[name] = {
                        "status": "running" if current == desired and current > 0 else "degraded"
                    }

            return {"status": "success", "services": services}
        except (FileNotFoundError, Exception) as e:
            logger.warning(
                f"Docker service check failed: {e}. This may be expected if not running in a Swarm manager."
            )
            return {"status": "error", "message": str(e)}

    async def _check_ports(self) -> Dict[str, Any]:
        """Checks if expected ports are listening."""
        logger.info("🔌 Checking ports...")
        import socket

        ports_status = {}
        for port, service_name in self.expected_ports.items():
            host = self.service_hosts.get(port, "127.0.0.1")
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    is_open = s.connect_ex((host, int(port))) == 0
                ports_status[port] = {
                    "service": service_name,
                    "host": host,
                    "status": "open" if is_open else "closed",
                }
            except Exception as e:
                ports_status[port] = {
                    "service": service_name,
                    "host": host,
                    "status": "error",
                    "error": str(e),
                }

        return {"status": "success", "ports": ports_status}

    async def _check_nvidia_gpu(self) -> Dict[str, Any]:
        """Checks NVIDIA GPU status using nvidia-smi."""
        logger.info("🎮 Checking NVIDIA GPU...")
        try:
            process = await asyncio.create_subprocess_exec(
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used,utilization.gpu,temperature.gpu",
                "--format=csv,noheader,nounits",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                return {"status": "not_available", "error": stderr.decode().strip()}

            gpu_data = stdout.decode().strip().split(", ")
            return {
                "status": "available",
                "gpu_name": gpu_data[0],
                "memory_total_mb": int(gpu_data[1]),
                "memory_used_mb": int(gpu_data[2]),
                "gpu_utilization_percent": int(gpu_data[3]),
                "temperature_celsius": int(gpu_data[4]),
            }
        except FileNotFoundError:
            return {"status": "not_available", "error": "nvidia-smi not found"}

    async def _full_diagnostic(self) -> Dict[str, Any]:
        """Runs all checks and aggregates the results."""
        logger.info("🔬 Running full diagnostic...")
        results = await asyncio.gather(
            self._health_check({}),
            self._check_docker_services(),
            self._check_ports(),
            self._check_nvidia_gpu(),
        )
        return {
            "status": "success",
            "health_check": results[0],
            "docker_services": results[1],
            "ports": results[2],
            "gpu": results[3],
        }
