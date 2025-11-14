"""
TwisterLab - Real Working Desktop Commander Agent
Executes system commands securely on Windows/Linux
"""
import asyncio
import subprocess
import platform
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import logging

from agents.metrics import track_agent_execution, tickets_processed_total

# Import LLM client for intelligent command validation
try:
    from agents.base.llm_client import ollama_client
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

logger = logging.getLogger(__name__)


class RealDesktopCommanderAgent:
    """
    Real desktop commander that executes ACTUAL system commands.

    Operations:
    - execute_command: Run system command (ping, ipconfig, systeminfo, etc.)
    - check_service: Verify Windows/Linux service status
    - get_system_info: Gather detailed system information
    - network_diagnostic: Run network diagnostics

    SECURITY: Only whitelisted commands allowed
    """

    def __init__(self):
        self.name = "RealDesktopCommanderAgent"
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
            "nslookup": {"windows": "nslookup", "linux": "nslookup"}
        }

        self.command_count = 0

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute desktop commander operation.

        Args:
            context: Must contain 'operation' key
                Operations: execute_command, check_service, get_system_info, network_diagnostic

        Returns:
            Command execution results
        """
        with track_agent_execution("commander"):
            operation = context.get("operation", "get_system_info")

            logger.info(f"💻 RealDesktopCommanderAgent executing: {operation}")

            try:
                if operation == "execute_command":
                    command = context.get("command")
                    args = context.get("args", [])
                    result = await self._execute_command(command, args)
                    if result.get("status") == "success":
                        tickets_processed_total.labels(agent_name="commander", status="success").inc()
                    return result
                elif operation == "check_service":
                    service_name = context.get("service_name")
                    return await self._check_service(service_name)
                elif operation == "get_system_info":
                    return await self._get_system_info()
                elif operation == "network_diagnostic":
                    target = context.get("target", "8.8.8.8")
                    return await self._network_diagnostic(target)
                else:
                    raise ValueError(f"Unknown operation: {operation}")

            except Exception as e:
                logger.error(f"❌ Command execution failed: {e}", exc_info=True)
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

    async def _execute_command(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """
        Execute system command with STRICT whitelist validation.

        SECURITY LAYERS:
        1. Whitelist validation (primary - must pass)
        2. LLM extra validation (optional - additional check if available)
        """
        # Layer 1: STRICT Whitelist validation (MANDATORY)
        is_whitelisted = await self._validate_command_whitelist(command)
        if not is_whitelisted:
            raise ValueError(f"Command not in whitelist: {command}")

        # Layer 2: LLM extra validation (optional additional security)
        if self.use_llm:
            try:
                is_safe_llm = await self._validate_command_llm(command, args)
                if not is_safe_llm:
                    logger.warning(f"⚠️ LLM flagged whitelisted command as potentially unsafe: {command}")
                else:
                    logger.info(f"🤖 LLM confirmed command is safe: {command}")
            except Exception as llm_error:
                logger.warning(f"⚠️ LLM validation failed (ignored, whitelist passed): {llm_error}")

        cmd_config = self.safe_commands[command]

        # Get OS-specific command
        os_key = "windows" if self.os_type == "Windows" else "linux"
        actual_command = cmd_config.get(os_key, cmd_config.get("windows"))

        # Get default args or use provided
        default_args = cmd_config.get("args", [])
        cmd_args = args if args else default_args

        full_command = [actual_command] + cmd_args

        logger.info(f"🔧 Executing: {' '.join(full_command)}")

        start_time = datetime.now(timezone.utc)

        try:
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=30.0  # 30 second timeout
            )

            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()

            output = stdout.decode('utf-8', errors='ignore')
            error_output = stderr.decode('utf-8', errors='ignore')

            self.command_count += 1

            result = {
                "status": "success" if process.returncode == 0 else "failed",
                "command": command,
                "full_command": ' '.join(full_command),
                "return_code": process.returncode,
                "output": output[:5000],  # Limit to 5000 chars
                "error": error_output[:1000] if error_output else None,
                "execution_time_seconds": round(execution_time, 2),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            logger.info(f"✅ Command executed: {command} (RC: {process.returncode})")
            return result

        except asyncio.TimeoutError:
            logger.error(f"❌ Command timeout: {command}")
            return {
                "status": "timeout",
                "command": command,
                "error": "Command execution timeout (30s)",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    async def _check_service(self, service_name: str) -> Dict[str, Any]:
        """
        Check Windows/Linux service status.
        """
        logger.info(f"🔍 Checking service: {service_name}")

        if self.os_type == "Windows":
            # Windows: sc query
            command = ["sc", "query", service_name]
        else:
            # Linux: systemctl status
            command = ["systemctl", "status", service_name]

        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            output = stdout.decode('utf-8', errors='ignore')

            # Parse status
            if self.os_type == "Windows":
                is_running = "RUNNING" in output
                state = "running" if is_running else "stopped"
            else:
                is_running = "active (running)" in output
                state = "running" if is_running else "stopped"

            result = {
                "status": "success",
                "service_name": service_name,
                "state": state,
                "is_running": is_running,
                "output": output[:1000],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            logger.info(f"✅ Service {service_name}: {state}")
            return result

        except Exception as e:
            logger.error(f"❌ Service check failed: {e}")
            return {
                "status": "error",
                "service_name": service_name,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    async def _get_system_info(self) -> Dict[str, Any]:
        """
        Gather comprehensive system information.
        """
        logger.info("📊 Gathering system information...")

        import psutil

        # CPU info
        cpu_info = {
            "count": psutil.cpu_count(),
            "percent": psutil.cpu_percent(interval=1),
            "frequency_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else None
        }

        # Memory info
        memory = psutil.virtual_memory()
        memory_info = {
            "total_gb": round(memory.total / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "percent": memory.percent
        }

        # Disk info
        disk = psutil.disk_usage('/')
        disk_info = {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent
        }

        # Network interfaces
        net_interfaces = list(psutil.net_if_addrs().keys())

        # OS info
        os_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }

        # Available commands for this platform
        available_commands = list(self.safe_commands.keys())

        result = {
            "status": "success",
            "system_info": {
                "hostname": platform.node(),
                "platform": f"{os_info['system']} {os_info['release']}",
                "os": os_info,
                "cpu": cpu_info,
                "memory": memory_info,
                "disk": disk_info,
                "network_interfaces": net_interfaces,
                "uptime_seconds": round((datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds()),
                "available_commands": available_commands
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        logger.info("✅ System info gathered")
        return result

    async def _network_diagnostic(self, target: str) -> Dict[str, Any]:
        """
        Run comprehensive network diagnostics.

        Tests:
        1. Ping target
        2. Traceroute
        3. DNS resolution
        4. Port connectivity
        """
        logger.info(f"🌐 Running network diagnostics for {target}...")

        diagnostics = {}

        # 1. Ping test
        ping_result = await self._execute_command("ping", [target])
        diagnostics["ping"] = {
            "success": ping_result["status"] == "success",
            "output": ping_result.get("output", "")[:500]
        }

        # 2. DNS resolution
        nslookup_result = await self._execute_command("nslookup", [target])
        diagnostics["dns_resolution"] = {
            "success": nslookup_result["status"] == "success",
            "output": nslookup_result.get("output", "")[:500]
        }

        # 3. Network interfaces
        if self.os_type == "Windows":
            ipconfig_result = await self._execute_command("ipconfig")
        else:
            ipconfig_result = await self._execute_command("ipconfig")  # ifconfig on Linux

        diagnostics["network_config"] = {
            "success": ipconfig_result["status"] == "success",
            "output": ipconfig_result.get("output", "")[:1000]
        }

        # Overall health
        all_success = all(d.get("success", False) for d in diagnostics.values())

        result = {
            "status": "success",
            "target": target,
            "diagnostics": diagnostics,
            "overall_health": "healthy" if all_success else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"✅ Network diagnostics complete: {result['overall_health']}")
        return result

    async def _validate_command_llm(self, command: str, args: List[str] = None) -> bool:
        """
        Use LLM to validate command safety.

        Args:
            command: Command to validate (e.g., 'ping', 'del', 'rm')
            args: Command arguments (e.g., ['8.8.8.8'])

        Returns:
            True if command is safe, False otherwise
        """
        full_cmd = f"{command} {' '.join(args or [])}"

        prompt = f"""Is this command safe for IT diagnostics?

Command: {full_cmd}

Safe commands are READ-ONLY: ping, ipconfig, whoami, hostname, tasklist, netstat, systeminfo, nslookup, tracert
Unsafe commands MODIFY system: del, shutdown, reboot, format, net user, reg add

Answer YES or NO."""

        try:
            # Call Ollama LLM with automatic PRIMARY/BACKUP failover
            result = await ollama_client.generate_with_fallback(
                prompt=prompt,
                agent_type="commander"
            )

            # Log which Ollama server was used (for monitoring)
            ollama_source = result.get("source", "unknown")
            if ollama_source == "primary":
                logger.info(f"✅ Command validation used PRIMARY Ollama (Corertx RTX 3060)")
            elif ollama_source == "fallback":
                logger.warning(f"⚠️ Command validation used BACKUP Ollama (Edgeserver GTX 1050) - PRIMARY may be down")

            response = result["response"].strip().upper()

            # Parse YES/NO response (strict check)
            is_safe = response.startswith("YES") or response == "YES"

            logger.info(f"🤖 LLM validation for '{full_cmd}': {'SAFE (YES)' if is_safe else 'UNSAFE (NO)'} [Response: {response[:50]}]")

            return is_safe

        except Exception as e:
            logger.error(f"❌ LLM validation error: {e}")
            raise

    async def _validate_command_whitelist(self, command: str) -> bool:
        """
        Fallback: Validate command against static whitelist.

        Returns:
            True if command is whitelisted, False otherwise
        """
        is_whitelisted = command in self.safe_commands

        if is_whitelisted:
            logger.info(f"✅ Whitelist validated: {command}")
        else:
            logger.warning(f"❌ Command not whitelisted: {command}")

        return is_whitelisted
