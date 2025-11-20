#!/usr/bin/env python3
"""
Agent Registration System for TwisterLab MCP

This script registers all real TwisterLab agents with the MCP communication system
and agent registry for unified access.

Registered Agents:
1. RealMonitoringAgent - System health monitoring
2. RealBackupAgent - Automated backups
3. RealSyncAgent - Cache/database synchronization
4. RealClassifierAgent - Ticket classification
5. RealResolverAgent - Issue resolution using SOPs
6. RealDesktopCommanderAgent - Remote system commands
7. RealMaestroAgent - Workflow orchestration
8. BrowserAgent - Web automation and scraping

Usage:
    python register_agents.py
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.mcp.agent_communication_system import MCPAgentCommunicationSystem, AgentRole
from agents.registry import agent_registry

# Import real agents
from agents.real.real_monitoring_agent import RealMonitoringAgent
from agents.real.real_backup_agent import RealBackupAgent
from agents.real.real_sync_agent import RealSyncAgent
from agents.real.real_classifier_agent import RealClassifierAgent
from agents.real.real_resolver_agent import RealResolverAgent
from agents.real.real_desktop_commander_agent import RealDesktopCommanderAgent
from agents.real.real_maestro_agent import RealMaestroAgent
from agents.real.BrowserAgent import BrowserAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentRegistrar:
    """Handles registration of real agents with MCP systems"""

    def __init__(self):
        self.comm_system = MCPAgentCommunicationSystem()
        self.real_agents = {}

        # Define agent configurations
        self.agent_configs = {
            "monitoring": {
                "class": RealMonitoringAgent,
                "capabilities": ["health_check", "metrics_collection", "system_monitoring", "alerting"],
                "role": AgentRole.MONITOR,
                "description": "System health monitoring and alerting"
            },
            "backup": {
                "class": RealBackupAgent,
                "capabilities": ["backup_creation", "data_protection", "disaster_recovery"],
                "role": AgentRole.WORKER,
                "description": "Automated backup and recovery operations"
            },
            "sync": {
                "class": RealSyncAgent,
                "capabilities": ["cache_sync", "data_synchronization", "consistency_check"],
                "role": AgentRole.WORKER,
                "description": "Cache and database synchronization"
            },
            "classifier": {
                "class": RealClassifierAgent,
                "capabilities": ["ticket_classification", "category_detection", "priority_assessment"],
                "role": AgentRole.SPECIALIST,
                "description": "IT ticket classification and routing"
            },
            "resolver": {
                "class": RealResolverAgent,
                "capabilities": ["issue_resolution", "sop_execution", "problem_solving", "knowledge_search"],
                "role": AgentRole.SPECIALIST,
                "description": "Automated issue resolution using SOPs"
            },
            "desktop_commander": {
                "class": RealDesktopCommanderAgent,
                "capabilities": ["remote_execution", "system_commands", "file_operations"],
                "role": AgentRole.WORKER,
                "description": "Remote system command execution"
            },
            "maestro": {
                "class": RealMaestroAgent,
                "capabilities": ["orchestration", "workflow_coordination", "load_balancing", "task_distribution"],
                "role": AgentRole.COORDINATOR,
                "description": "Multi-agent workflow orchestration"
            },
            "browser": {
                "class": BrowserAgent,
                "capabilities": ["web_automation", "data_scraping", "web_interaction"],
                "role": AgentRole.WORKER,
                "description": "Web automation and data extraction"
            }
        }

    async def initialize_systems(self):
        """Initialize MCP communication system"""
        logger.info("Initializing MCP communication system...")
        await self.comm_system.start()
        logger.info("MCP communication system initialized")

    async def register_agents(self):
        """Register all real agents with MCP systems"""
        logger.info("Registering real TwisterLab agents...")

        for agent_name, config in self.agent_configs.items():
            try:
                # Instantiate the agent
                agent_class = config["class"]
                agent_instance = agent_class()

                # Store reference
                self.real_agents[agent_name] = agent_instance

                # Register with MCP communication system
                await self._register_with_comm_system(agent_name, config, agent_instance)

                # Register with agent registry (if available)
                await self._register_with_agent_registry(agent_name, agent_instance)

                logger.info(f"✓ Registered agent: {agent_name} ({config['description']})")

            except Exception as e:
                logger.error(f"✗ Failed to register agent {agent_name}: {e}")

    async def _register_with_comm_system(self, agent_name: str, config: Dict[str, Any], agent_instance):
        """Register agent with MCP communication system"""
        try:
            # Get capabilities from agent if available, otherwise use config
            capabilities = getattr(agent_instance, 'capabilities', config['capabilities'])

            # Register with communication system
            self.comm_system.register_agent(
                agent_name=agent_name,
                capabilities=capabilities,
                role=config['role']
            )

            logger.debug(f"Registered {agent_name} with communication system")

        except Exception as e:
            logger.warning(f"Communication system registration failed for {agent_name}: {e}")

    async def _register_with_agent_registry(self, agent_name: str, agent_instance):
        """Register agent with agent registry"""
        try:
            # Try to register with agent registry
            if hasattr(agent_registry, 'register_agent'):
                agent_registry.register_agent(agent_name, agent_instance)
                logger.debug(f"Registered {agent_name} with agent registry")
            else:
                logger.debug(f"Agent registry registration skipped for {agent_name} (no register_agent method)")

        except Exception as e:
            logger.warning(f"Agent registry registration failed for {agent_name}: {e}")

    async def verify_registrations(self) -> Dict[str, Any]:
        """Verify that all agents are properly registered"""
        logger.info("Verifying agent registrations...")

        verification_results = {
            "communication_system": {},
            "agent_registry": {},
            "summary": {}
        }

        # Check communication system registrations
        comm_status = self.comm_system.get_network_status()
        verification_results["communication_system"] = {
            "total_agents": comm_status.get("total_agents", 0),
            "active_agents": comm_status.get("active_agents", 0),
            "agent_roles": comm_status.get("agent_roles", {})
        }

        # Check agent registry (if available)
        try:
            if hasattr(agent_registry, 'list_agents'):
                registry_agents = agent_registry.list_agents()
                verification_results["agent_registry"] = {
                    "registered_agents": list(registry_agents.keys()) if registry_agents else [],
                    "count": len(registry_agents) if registry_agents else 0
                }
            else:
                verification_results["agent_registry"] = {"status": "not_available"}
        except Exception as e:
            verification_results["agent_registry"] = {"error": str(e)}

        # Summary
        expected_agents = len(self.agent_configs)
        comm_registered = verification_results["communication_system"]["total_agents"]
        registry_registered = verification_results["agent_registry"].get("count", 0)

        verification_results["summary"] = {
            "expected_agents": expected_agents,
            "comm_system_registered": comm_registered,
            "registry_registered": registry_registered,
            "comm_system_success": comm_registered >= expected_agents,
            "registry_success": registry_registered >= 0  # Registry is optional
        }

        return verification_results

    async def test_agent_communication(self) -> bool:
        """Test basic agent communication"""
        logger.info("Testing agent communication...")

        try:
            # Send a test message from maestro to monitoring
            from agents.mcp.agent_communication_system import MCPMessage, MessageType

            test_message = MCPMessage(
                message_id="test_registration_001",
                sender_agent="maestro",
                receiver_agent="monitoring",
                message_type=MessageType.TASK_REQUEST,
                payload={
                    "task": "ping",
                    "description": "Test communication after registration"
                }
            )

            success = await self.comm_system.send_message(test_message)

            if success:
                logger.info("✓ Agent communication test successful")
                return True
            else:
                logger.error("✗ Agent communication test failed")
                return False

        except Exception as e:
            logger.error(f"✗ Agent communication test error: {e}")
            return False

    async def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up agent registration system...")
        await self.comm_system.stop()

    async def run_registration(self) -> Dict[str, Any]:
        """Run the complete agent registration process"""
        logger.info("Starting TwisterLab agent registration process...")

        try:
            # Initialize systems
            await self.initialize_systems()

            # Register agents
            await self.register_agents()

            # Verify registrations
            verification = await self.verify_registrations()

            # Test communication
            comm_test = await self.test_agent_communication()

            # Summary
            summary = {
                "success": verification["summary"]["comm_system_success"],
                "communication_test": comm_test,
                "registered_agents": verification["communication_system"]["total_agents"],
                "active_agents": verification["communication_system"]["active_agents"],
                "agent_roles": verification["communication_system"]["agent_roles"]
            }

            logger.info("Agent registration process completed")
            logger.info(f"Summary: {summary}")

            return summary

        except Exception as e:
            logger.error(f"Agent registration process failed: {e}")
            return {"success": False, "error": str(e)}

        finally:
            await self.cleanup()


async def main():
    """Main registration runner"""
    registrar = AgentRegistrar()
    results = await registrar.run_registration()

    # Exit with appropriate code
    success = results.get("success", False)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
