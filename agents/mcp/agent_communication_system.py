"""
MCP-based Agent Communication System

Innovative Features:
1. Agent-to-Agent Communication via MCP Protocol
2. Dynamic Agent Discovery and Registration
3. Semantic Message Routing
4. Real-time Event Streaming between Agents
5. Knowledge Graph Integration for Context Sharing
6. Adaptive Communication Patterns based on Agent Learning

This system transforms MCP from a client-server protocol into a
peer-to-peer agent communication framework.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages agents can exchange"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    EVENT_NOTIFICATION = "event_notification"
    KNOWLEDGE_SHARE = "knowledge_share"
    COLLABORATION_OFFER = "collaboration_offer"
    RESOURCE_REQUEST = "resource_request"
    LEARNING_UPDATE = "learning_update"


class AgentRole(Enum):
    """Roles agents can play in communication"""
    COORDINATOR = "coordinator"
    WORKER = "worker"
    SPECIALIST = "specialist"
    MONITOR = "monitor"
    LEARNER = "learner"


@dataclass
class MCPMessage:
    """MCP-based message structure for agent communication"""
    message_id: str
    sender_agent: str
    receiver_agent: str
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    priority: int = 1
    ttl_seconds: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "message_id": self.message_id,
            "sender_agent": self.sender_agent,
            "receiver_agent": self.receiver_agent,
            "message_type": self.message_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "priority": self.priority,
            "ttl_seconds": self.ttl_seconds,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPMessage':
        """Create message from dictionary"""
        return cls(
            message_id=data["message_id"],
            sender_agent=data["sender_agent"],
            receiver_agent=data["receiver_agent"],
            message_type=MessageType(data["message_type"]),
            payload=data["payload"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            correlation_id=data.get("correlation_id"),
            priority=data.get("priority", 1),
            ttl_seconds=data.get("ttl_seconds", 300),
            metadata=data.get("metadata", {})
        )


class AgentProfile:
    """Profile information for an agent in the communication network"""

    def __init__(self, agent_name: str, capabilities: List[str], role: AgentRole):
        self.agent_name = agent_name
        self.capabilities = capabilities
        self.role = role
        self.last_seen = datetime.now(timezone.utc)
        self.status = "active"
        self.knowledge_domains: Set[str] = set()
        self.communication_history: List[MCPMessage] = []
        self.trust_score = 1.0
        self.performance_metrics = {
            "messages_sent": 0,
            "messages_received": 0,
            "successful_collaborations": 0,
            "response_time_avg": 0.0
        }

    def update_activity(self):
        """Update last seen timestamp"""
        self.last_seen = datetime.now(timezone.utc)

    def add_knowledge_domain(self, domain: str):
        """Add a knowledge domain this agent specializes in"""
        self.knowledge_domains.add(domain)

    def record_message(self, message: MCPMessage, direction: str):
        """Record a message in communication history"""
        self.communication_history.append(message)
        if direction == "sent":
            self.performance_metrics["messages_sent"] += 1
        elif direction == "received":
            self.performance_metrics["messages_received"] += 1

        # Keep only recent history (last 100 messages)
        if len(self.communication_history) > 100:
            self.communication_history = self.communication_history[-100:]


class MCPAgentCommunicationSystem:
    """
    MCP-based Agent Communication System

    This innovative system allows agents to communicate peer-to-peer
    using MCP protocol, enabling:
    - Dynamic agent discovery
    - Semantic message routing
    - Collaborative problem solving
    - Knowledge sharing and learning
    - Real-time coordination
    """

    def __init__(self, performance_monitor=None):
        self.agents: Dict[str, AgentProfile] = {}
        self.message_queue: asyncio.Queue[MCPMessage] = asyncio.Queue()
        self.event_subscriptions: Dict[str, Set[str]] = {}
        self.knowledge_graph: Dict[str, Dict[str, Any]] = {}
        self.collaboration_sessions: Dict[str, Dict[str, Any]] = {}
        self.performance_monitor = performance_monitor

        # Message handlers
        self.message_handlers: Dict[MessageType, Callable] = {
            MessageType.TASK_REQUEST: self._handle_task_request,
            MessageType.TASK_RESPONSE: self._handle_task_response,
            MessageType.STATUS_UPDATE: self._handle_status_update,
            MessageType.EVENT_NOTIFICATION: self._handle_event_notification,
            MessageType.KNOWLEDGE_SHARE: self._handle_knowledge_share,
            MessageType.COLLABORATION_OFFER: self._handle_collaboration_offer,
            MessageType.RESOURCE_REQUEST: self._handle_resource_request,
            MessageType.LEARNING_UPDATE: self._handle_learning_update,
        }

        # Start background tasks
        self.running = False
        self.background_tasks: List[asyncio.Task] = []

    async def start(self):
        """Start the communication system"""
        self.running = True
        logger.info("Starting MCP Agent Communication System")

        # Start message processing
        self.background_tasks.append(
            asyncio.create_task(self._process_message_queue())
        )

        # Start agent health monitoring
        self.background_tasks.append(
            asyncio.create_task(self._monitor_agent_health())
        )

        # Start knowledge graph maintenance
        self.background_tasks.append(
            asyncio.create_task(self._maintain_knowledge_graph())
        )

    async def stop(self):
        """Stop the communication system"""
        self.running = False
        logger.info("Stopping MCP Agent Communication System")

        # Cancel all background tasks
        for task in self.background_tasks:
            task.cancel()

        await asyncio.gather(*self.background_tasks, return_exceptions=True)

    def register_agent(self, agent_name: str, capabilities: List[str],
                      role: AgentRole) -> AgentProfile:
        """Register a new agent in the communication network"""
        if agent_name in self.agents:
            raise ValueError(f"Agent {agent_name} already registered")

        profile = AgentProfile(agent_name, capabilities, role)
        self.agents[agent_name] = profile

        logger.info(f"Registered agent: {agent_name} with role {role.value}")
        return profile

    def unregister_agent(self, agent_name: str):
        """Unregister an agent from the communication network"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            logger.info(f"Unregistered agent: {agent_name}")

    async def send_message(self, message: MCPMessage) -> bool:
        """Send a message to another agent"""
        if not self.running:
            return False

        # Validate sender is registered
        if message.sender_agent not in self.agents:
            logger.warning(f"Unregistered sender: {message.sender_agent}")
            return False

        # Update sender activity
        self.agents[message.sender_agent].update_activity()
        self.agents[message.sender_agent].record_message(message, "sent")

        # Queue message for processing
        await self.message_queue.put(message)

        # Record performance metrics
        if self.performance_monitor:
            self.performance_monitor.record_mcp_message(message.message_type.value, 0.001)  # Minimal latency for send

        return True

    async def broadcast_message(self, sender: str, message_type: MessageType,
                               payload: Dict[str, Any], target_role: Optional[AgentRole] = None):
        """Broadcast a message to all agents or agents with specific role"""
        targets = []
        if target_role:
            targets = [name for name, profile in self.agents.items()
                      if profile.role == target_role and name != sender]
        else:
            targets = [name for name in self.agents.keys() if name != sender]

        for target in targets:
            message = MCPMessage(
                message_id=f"broadcast_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                sender_agent=sender,
                receiver_agent=target,
                message_type=message_type,
                payload=payload
            )
            await self.send_message(message)

    def subscribe_to_events(self, agent_name: str, event_types: List[str]):
        """Subscribe an agent to specific event types"""
        if agent_name not in self.event_subscriptions:
            self.event_subscriptions[agent_name] = set()

        self.event_subscriptions[agent_name].update(event_types)
        logger.info(f"Agent {agent_name} subscribed to events: {event_types}")

    def unsubscribe_from_events(self, agent_name: str, event_types: List[str]):
        """Unsubscribe an agent from specific event types"""
        if agent_name in self.event_subscriptions:
            self.event_subscriptions[agent_name].difference_update(event_types)

    async def _process_message_queue(self):
        """Process messages from the queue"""
        while self.running:
            try:
                message = await self.message_queue.get()

                # Check if message is still valid (TTL)
                age_seconds = (datetime.now(timezone.utc) - message.timestamp).total_seconds()
                if age_seconds > message.ttl_seconds:
                    logger.warning(f"Message {message.message_id} expired")
                    continue

                # Route message to appropriate handler
                if message.message_type in self.message_handlers:
                    await self.message_handlers[message.message_type](message)
                else:
                    logger.warning(f"No handler for message type: {message.message_type}")

                self.message_queue.task_done()

            except Exception as e:
                logger.error(f"Error processing message: {e}")

    async def _handle_task_request(self, message: MCPMessage):
        """Handle task request messages"""
        receiver = message.receiver_agent

        if receiver not in self.agents:
            logger.warning(f"Task request to unknown agent: {receiver}")
            return

        # Check if receiver has required capabilities
        required_capability = message.payload.get("required_capability")
        if required_capability and required_capability not in self.agents[receiver].capabilities:
            # Try to find alternative agent
            alternative = self._find_agent_with_capability(required_capability, exclude=[receiver])
            if alternative:
                logger.info(f"Redirecting task from {receiver} to {alternative}")
                redirected_message = MCPMessage(
                    message_id=f"redirect_{message.message_id}",
                    sender_agent=message.sender_agent,
                    receiver_agent=alternative,
                    message_type=MessageType.TASK_REQUEST,
                    payload=message.payload,
                    correlation_id=message.correlation_id
                )
                await self.send_message(redirected_message)
            return

        # Forward to receiver agent (in real implementation, this would call agent methods)
        logger.info(f"Task request from {message.sender_agent} to {receiver}: {message.payload}")

    async def _handle_task_response(self, message: MCPMessage):
        """Handle task response messages"""
        # Update performance metrics
        if message.sender_agent in self.agents:
            self.agents[message.sender_agent].performance_metrics["successful_collaborations"] += 1

        logger.info(f"Task response from {message.sender_agent}: {message.payload}")

    async def _handle_status_update(self, message: MCPMessage):
        """Handle status update messages"""
        sender = message.sender_agent
        if sender in self.agents:
            # Update agent status
            status = message.payload.get("status", "unknown")
            self.agents[sender].status = status
            self.agents[sender].update_activity()

            # Broadcast to subscribers
            await self._broadcast_to_subscribers("status_update", message.payload, sender)

    async def _handle_event_notification(self, message: MCPMessage):
        """Handle event notification messages"""
        event_type = message.payload.get("event_type")
        if event_type:
            await self._broadcast_to_subscribers(event_type, message.payload, message.sender_agent)

    async def _handle_knowledge_share(self, message: MCPMessage):
        """Handle knowledge sharing messages"""
        knowledge = message.payload.get("knowledge", {})
        domain = message.payload.get("domain")

        # Update knowledge graph
        if domain:
            if domain not in self.knowledge_graph:
                self.knowledge_graph[domain] = {}

            self.knowledge_graph[domain][message.sender_agent] = {
                "knowledge": knowledge,
                "timestamp": message.timestamp.isoformat(),
                "confidence": message.payload.get("confidence", 1.0)
            }

            # Update agent's knowledge domains
            if message.sender_agent in self.agents:
                self.agents[message.sender_agent].add_knowledge_domain(domain)

        logger.info(f"Knowledge shared by {message.sender_agent} in domain {domain}")

    async def _handle_collaboration_offer(self, message: MCPMessage):
        """Handle collaboration offer messages"""
        session_id = message.payload.get("session_id")
        if session_id:
            self.collaboration_sessions[session_id] = {
                "initiator": message.sender_agent,
                "participants": [message.sender_agent],
                "purpose": message.payload.get("purpose"),
                "created_at": message.timestamp.isoformat()
            }

            logger.info(f"Collaboration session {session_id} initiated by {message.sender_agent}")

    async def _handle_resource_request(self, message: MCPMessage):
        """Handle resource request messages"""
        resource_type = message.payload.get("resource_type")

        # Find agents that can provide this resource
        providers = []
        for name, profile in self.agents.items():
            if resource_type in profile.capabilities:
                providers.append(name)

        if providers:
            # Route to first available provider
            provider = providers[0]
            response_message = MCPMessage(
                message_id=f"resource_response_{message.message_id}",
                sender_agent=provider,
                receiver_agent=message.sender_agent,
                message_type=MessageType.TASK_RESPONSE,
                payload={
                    "resource_available": True,
                    "provider": provider,
                    "resource_type": resource_type
                },
                correlation_id=message.correlation_id
            )
            await self.send_message(response_message)

    async def _handle_learning_update(self, message: MCPMessage):
        """Handle learning update messages"""
        learning_type = message.payload.get("learning_type")
        model_updates = message.payload.get("model_updates", {})

        # Distribute learning updates to relevant agents
        for name, profile in self.agents.items():
            if profile.role == AgentRole.LEARNER or learning_type in profile.knowledge_domains:
                update_message = MCPMessage(
                    message_id=f"learning_dist_{message.message_id}_{name}",
                    sender_agent=message.sender_agent,
                    receiver_agent=name,
                    message_type=MessageType.LEARNING_UPDATE,
                    payload={
                        "learning_type": learning_type,
                        "model_updates": model_updates,
                        "source_agent": message.sender_agent
                    }
                )
                await self.send_message(update_message)

    async def _broadcast_to_subscribers(self, event_type: str, payload: Dict[str, Any], sender: str):
        """Broadcast event to subscribed agents"""
        for agent_name, subscriptions in self.event_subscriptions.items():
            if event_type in subscriptions and agent_name != sender:
                notification = MCPMessage(
                    message_id=f"event_{event_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                    sender_agent=sender,
                    receiver_agent=agent_name,
                    message_type=MessageType.EVENT_NOTIFICATION,
                    payload={"event_type": event_type, **payload}
                )
                await self.send_message(notification)

    def _find_agent_with_capability(self, capability: str, exclude: List[str] = None) -> Optional[str]:
        """Find an agent with a specific capability"""
        exclude = exclude or []

        for name, profile in self.agents.items():
            if name not in exclude and capability in profile.capabilities:
                return name

        return None

    async def _monitor_agent_health(self):
        """Monitor agent health and detect failures"""
        while self.running:
            try:
                await asyncio.sleep(60)  # Check every minute

                current_time = datetime.now(timezone.utc)
                unhealthy_agents = []

                for name, profile in self.agents.items():
                    # Check if agent has been seen recently (5 minutes)
                    time_since_last_seen = (current_time - profile.last_seen).total_seconds()
                    if time_since_last_seen > 300:  # 5 minutes
                        profile.status = "unhealthy"
                        unhealthy_agents.append(name)

                if unhealthy_agents:
                    logger.warning(f"Unhealthy agents detected: {unhealthy_agents}")

                    # Broadcast health alert
                    await self.broadcast_message(
                        sender="system",
                        message_type=MessageType.EVENT_NOTIFICATION,
                        payload={
                            "event_type": "agent_health_alert",
                            "unhealthy_agents": unhealthy_agents
                        }
                    )

            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")

    async def _maintain_knowledge_graph(self):
        """Maintain and optimize the knowledge graph"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes

                # Clean up old knowledge entries (older than 24 hours)
                cutoff_time = datetime.now(timezone.utc).timestamp() - 86400

                for domain in self.knowledge_graph:
                    to_remove = []
                    for agent, entry in self.knowledge_graph[domain].items():
                        entry_time = datetime.fromisoformat(entry["timestamp"]).timestamp()
                        if entry_time < cutoff_time:
                            to_remove.append(agent)

                    for agent in to_remove:
                        del self.knowledge_graph[domain][agent]

                # Optimize knowledge graph (merge similar entries, etc.)
                # This would contain sophisticated ML algorithms in production

                logger.info("Knowledge graph maintenance completed")

            except Exception as e:
                logger.error(f"Error in knowledge graph maintenance: {e}")

    def get_network_status(self) -> Dict[str, Any]:
        """Get current network status"""
        return {
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.status == "active"]),
            "agent_roles": {
                role.value: len([a for a in self.agents.values() if a.role == role])
                for role in AgentRole
            },
            "knowledge_domains": list(self.knowledge_graph.keys()),
            "active_collaborations": len(self.collaboration_sessions),
            "message_queue_size": self.message_queue.qsize()
        }

    def get_agent_insights(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get insights about a specific agent"""
        if agent_name not in self.agents:
            return None

        profile = self.agents[agent_name]
        return {
            "name": profile.agent_name,
            "role": profile.role.value,
            "capabilities": list(profile.capabilities),
            "knowledge_domains": list(profile.knowledge_domains),
            "status": profile.status,
            "trust_score": profile.trust_score,
            "performance_metrics": profile.performance_metrics,
            "last_seen": profile.last_seen.isoformat(),
            "communication_partners": list(set(
                msg.sender_agent if msg.receiver_agent == agent_name else msg.receiver_agent
                for msg in profile.communication_history[-50:]  # Last 50 messages
            ))
        }


# Global instance for easy access
communication_system = MCPAgentCommunicationSystem()


async def initialize_agent_communication():
    """Initialize the agent communication system"""
    await communication_system.start()

    # Register example agents (in real system, agents register themselves)
    communication_system.register_agent(
        "maestro_orchestrator",
        ["orchestration", "coordination", "monitoring"],
        AgentRole.COORDINATOR
    )

    communication_system.register_agent(
        "monitoring_agent",
        ["health_check", "metrics_collection", "alerting"],
        AgentRole.MONITOR
    )

    communication_system.register_agent(
        "resolver_agent",
        ["problem_resolution", "knowledge_search", "pattern_matching"],
        AgentRole.SPECIALIST
    )

    logger.info("Agent communication system initialized")


if __name__ == "__main__":
    # Example usage
    async def demo():
        await initialize_agent_communication()

        # Example: Send a task request
        task_message = MCPMessage(
            message_id="task_001",
            sender_agent="maestro_orchestrator",
            receiver_agent="resolver_agent",
            message_type=MessageType.TASK_REQUEST,
            payload={
                "task": "resolve_user_issue",
                "description": "User reports slow application performance",
                "required_capability": "problem_resolution"
            }
        )

        await communication_system.send_message(task_message)

        # Example: Share knowledge
        knowledge_message = MCPMessage(
            message_id="knowledge_001",
            sender_agent="resolver_agent",
            receiver_agent="maestro_orchestrator",
            message_type=MessageType.KNOWLEDGE_SHARE,
            payload={
                "domain": "performance_optimization",
                "knowledge": {
                    "pattern": "database_connection_pool_exhaustion",
                    "solution": "Increase connection pool size",
                    "confidence": 0.95
                }
            }
        )

        await communication_system.send_message(knowledge_message)

        # Keep running for a bit
        await asyncio.sleep(5)

        # Get network status
        status = communication_system.get_network_status()
        print(f"Network status: {status}")

        await communication_system.stop()

    asyncio.run(demo())
