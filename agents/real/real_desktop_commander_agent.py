"""
TwisterLab - Real Working Desktop Commander Agent (v2 - Unified)
Executes system commands securely on Windows/Linux, aligned with the UnifiedAgentBase.
"""

import asyncio
import logging
import platform
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agents.base.unified_agent import AgentStatus, UnifiedAgentBase

# Import LLM client for intelligent command validation
try:
    from agents.base.llm_client import ollama_client

    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

logger = logging.getLogger(__name__)


class RealDesktopCommanderAgent(UnifiedAgentBase):
    """
    Real desktop commander that executes ACTUAL system commands. Inherits from UnifiedAgentBase.
    """

    def __init__(self):
        super().__init__(
            name="RealDesktopCommanderAgent",
            version="2.0",
            description="Executes system commands securely on remote Windows/Linux desktops.",
        )
        self.os_type = platform.system()  # Windows, Linux, Darwin
        self.use_llm = LLM_AVAILABLE  # Enable LLM validation if available

        # Whitelisted safe commands (security fallback)
        self.safe_commands = {
            "ping": {"windows": "ping", "linux": "ping", "args": ["-n", "4"]},
            "ipconfig": {"windows": "ipconfig", "linux": "ifconfig"},
            "netstat": {"windows": "netstat", "linux": "netstat", "args": ["-an"]},
            "systeminfo": {"windows": "systeminfo", "linux": "uname", "args": ["-a"]},
            "tasklist": {"windows": "tasklist", "linux": "ps", "args": ["aux"]},
            "whoami": {"windows": "whoami", "linux": "whoami"},
            "hostname": {"windows": "hostname", "linux": "hostname"},
            "route": {"windows": "route", "linux": "route", "args": ["print"]},
            "nslookup": {"windows": "nslookup", "linux": "nslookup"},
        }

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute desktop commander operation.
        This method is called by the parent 'run' method, which handles status and error management.

        Args:
            context: Must contain 'operation' key
                Operations: execute_command, check_service, get_system_info, network_diagnostic

        Returns:
            Command execution results
        """
        operation = context.get("operation", "get_system_info")
        logger.info(f"💻 {self.name} executing: {operation}")

        if operation == "execute_command":
            command = context.get("command")
            args = context.get("args", [])
            return await self._execute_command(command, args)
        elif operation == "check_service":
            service_name = context.get("service_name")
            return await self._check_service(service_name)
        elif operation == "get_system_info":
            return await self._get_system_info()
        elif operation == "network_diagnostic":
            target = context.get("target", "8.8.8.8")
            return await self._network_diagnostic(target)
        else:
            raise ValueError(f"Unknown operation for {self.name}: {operation}")

    async def _execute_command(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """
        Execute system command with STRICT whitelist validation.
        """
        is_whitelisted = await self._validate_command_whitelist(command)
        if not is_whitelisted:
            raise ValueError(f"Command not in whitelist: {command}")

        if self.use_llm:
            try:
                is_safe_llm = await self._validate_command_llm(command, args)
                if not is_safe_llm:
                    logger.warning(
                        f"⚠️ LLM flagged whitelisted command as potentially unsafe: {command}"
                    )
            except Exception as llm_error:
                logger.warning(f"⚠️ LLM validation failed (ignored, whitelist passed): {llm_error}")

        cmd_config = self.safe_commands[command]
        os_key = "windows" if self.os_type == "Windows" else "linux"
        actual_command = cmd_config.get(os_key, cmd_config.get("windows"))
        cmd_args = args if args else cmd_config.get("args", [])
        full_command = [actual_command] + cmd_args

        logger.info(f"🔧 Executing: {' '.join(full_command)}")
        start_time = datetime.now(timezone.utc)

        try:
            process = await asyncio.create_subprocess_exec(
                *full_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()

            return {
                "status": "success" if process.returncode == 0 else "failed",
                "command": command,
                "full_command": " ".join(full_command),
                "return_code": process.returncode,
                "output": stdout.decode("utf-8", errors="ignore")[:5000],
                "error": stderr.decode("utf-8", errors="ignore")[:1000] if stderr else None,
                "execution_time_seconds": round(execution_time, 2),
            }
        except asyncio.TimeoutError:
            raise TimeoutError(f"Command execution timeout (30s) for {command}")
        except Exception as e:
            raise RuntimeError(f"Command execution failed for {command}: {e}")

    async def _check_service(self, service_name: str) -> Dict[str, Any]:
        """Checks Windows/Linux service status."""
        logger.info(f"🔍 Checking service: {service_name}")
        command = (
            ["sc", "query", service_name]
            if self.os_type == "Windows"
            else ["systemctl", "status", service_name]
        )
        try:
            process = await asyncio.create_subprocess_exec(
                *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            output = stdout.decode("utf-8", errors="ignore")
            is_running = (
                ("RUNNING" in output)
                if self.os_type == "Windows"
                else ("active (running)" in output)
            )
            return {
                "status": "success",
                "service_name": service_name,
                "is_running": is_running,
                "output": output[:1000],
            }
        except Exception as e:
            raise RuntimeError(f"Service check failed for {service_name}: {e}")

    async def _get_system_info(self) -> Dict[str, Any]:
        """Gathers comprehensive system information."""
        logger.info("📊 Gathering system information...")
        import psutil

        return {
            "status": "success",
            "system_info": {
                "hostname": platform.node(),
                "os": {"system": platform.system(), "release": platform.release()},
                "cpu": {"count": psutil.cpu_count(), "percent": psutil.cpu_percent(interval=1)},
                "memory": {
                    "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                    "percent": psutil.virtual_memory().percent,
                },
                "disk": {
                    "total_gb": round(psutil.disk_usage("/").total / (1024**3), 2),
                    "percent": psutil.disk_usage("/").percent,
                },
                "available_commands": list(self.safe_commands.keys()),
            },
        }

    async def _network_diagnostic(self, target: str) -> Dict[str, Any]:
        """Runs comprehensive network diagnostics."""
        logger.info(f"🌐 Running network diagnostics for {target}...")
        diagnostics = {}
        ping_result = await self._execute_command("ping", [target])
        diagnostics["ping"] = {
            "success": ping_result["status"] == "success",
            "output": ping_result.get("output", "")[:500],
        }
        nslookup_result = await self._execute_command("nslookup", [target])
        diagnostics["dns_resolution"] = {
            "success": nslookup_result["status"] == "success",
            "output": nslookup_result.get("output", "")[:500],
        }

        overall_health = (
            "healthy" if all(d.get("success", False) for d in diagnostics.values()) else "degraded"
        )
        return {
            "status": "success",
            "target": target,
            "diagnostics": diagnostics,
            "overall_health": overall_health,
        }

    async def _validate_command_llm(self, command: str, args: List[str] = None) -> bool:
        """Uses LLM to validate command safety."""
        full_cmd = f"{command} {' '.join(args or [])}"
        prompt = f"""Is this command safe for IT diagnostics? Command: {full_cmd}. Safe commands are READ-ONLY. Unsafe commands MODIFY system. Answer YES or NO."""
        try:
            result = await ollama_client.generate_with_fallback(
                prompt=prompt, agent_type="commander"
            )
            is_safe = result["response"].strip().upper().startswith("YES")
            logger.info(f"🤖 LLM validation for '{full_cmd}': {'SAFE' if is_safe else 'UNSAFE'}")
            return is_safe
        except Exception as e:
            logger.error(f"❌ LLM validation error: {e}")
            return False  # Default to unsafe if LLM validation fails

    async def _validate_command_whitelist(self, command: str) -> bool:
        """Validates command against static whitelist."""
        is_whitelisted = command in self.safe_commands
        logger.info(
            f"✅ Whitelist validated: {command}"
            if is_whitelisted
            else f"❌ Command not whitelisted: {command}"
        )
        return is_whitelisted
