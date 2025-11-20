"""
TwisterLab - Maestro Orchestrator Agent
Central orchestrator routing tasks to specialized agents
with load balancing and failover
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from agents.base import BaseAgent

logger = logging.getLogger(__name__)


class TicketPriority(Enum):
    """Priorités des tickets"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketComplexity(Enum):
    """Complexité des tickets"""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class MaestroOrchestratorAgent(BaseAgent):
    # Orchestrateur central (Maestro) qui route les tâches vers les agents
    # spécialisés.
    # Gère l'équilibrage de charge, la tolérance aux pannes,
    # et l'agrégation des résultats.

    def __init__(self) -> None:
        super().__init__(
            name="maestro-orchestrator",
            display_name="Maestro Orchestrator",
            description=(
                "Central orchestrator routing tasks to specialized agents "
                "with load balancing and failover"
            ),
            role="orchestrator",
            instructions=(
                "You are the Maestro Orchestrator, the central coordinator "
                "for TwisterLab's IT helpdesk automation.\n"
                "Your role is to:\n"
                "1. Receive incoming tickets and route them to appropriate "
                "agents.\n"
                "2. Manage load balancing across multiple agent instances.\n"
                "3. Handle failover when agents are unavailable.\n"
                "4. Aggregate results and provide unified responses.\n"
                "5. Monitor agent health and performance.\n"
                "Routing Rules:\n"
                "- URGENT tickets → Human agents immediately.\n"
                "- High-confidence SIMPLE tickets → Auto-resolver.\n"
                "- Low-confidence or COMPLEX tickets → Human review.\n"
                "- All tickets start with classification.\n"
                "Always maintain audit trails and provide detailed logging."
            ),
            model="llama-3.2",
            temperature=0.2,  # Balanced pour les décisions de routage
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "route_ticket",
                        "description": ("Route a ticket through the automation workflow"),
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "ticket_id": {
                                    "type": "string",
                                    "description": "Unique ticket identifier",
                                },
                                "subject": {
                                    "type": "string",
                                    "description": "Ticket subject line",
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Ticket description",
                                },
                                "requestor": {
                                    "type": "string",
                                    "description": ("Person who submitted the ticket"),
                                },
                            },
                            "required": ["ticket_id", "subject", "description"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_agent_status",
                        "description": ("Check the status of all available agents"),
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "include_health": {
                                    "type": "boolean",
                                    "description": ("Include detailed health metrics"),
                                }
                            },
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "rebalance_load",
                        "description": "Rebalance workload across agents",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "strategy": {
                                    "type": "string",
                                    "enum": [
                                        "round_robin",
                                        "least_loaded",
                                        "priority_based",
                                    ],
                                    "description": "Load balancing strategy",
                                }
                            },
                        },
                    },
                },
            ],
        )

        # État des agents disponibles
        self.available_agents = {
            "classifier": {
                "name": "Ticket Classifier",
                "status": "available",
                "load": 0,
                "max_load": 10,
                "last_health_check": datetime.now(),
            },
            "resolver": {
                "name": "Helpdesk Resolver",
                "status": "available",
                "load": 0,
                "max_load": 5,
                "last_health_check": datetime.now(),
            },
            "desktop_commander": {
                "name": "Desktop Commander",
                "status": "available",
                "load": 0,
                "max_load": 3,
                "last_health_check": datetime.now(),
            },
        }

        # Métriques de performance
        self.metrics = {
            "tickets_processed": 0,
            "auto_resolved": 0,
            "escalated_to_human": 0,
            "average_resolution_time": 0,
            "agent_failures": 0,
        }

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Exécute une tâche d'orchestration.

        Args:
            task: Description de la tâche
            context: Contexte de la tâche (ticket_id, etc.)

        Returns:
            Résultat de l'orchestration
        """
        try:
            logger.info("Maestro orchestrating task: %s", task)
            # Extraire les paramètres
            operation = context.get("operation", "route_ticket") if context else "route_ticket"
            if operation == "route_ticket":
                result = await self.route_ticket(context)
            elif operation == "get_agent_status":
                include_health = context.get("include_health", False) if context else False
                result = await self.get_agent_status(include_health)
            elif operation == "rebalance_load":
                strategy = context.get("strategy", "round_robin") if context else "round_robin"
                result = await self.rebalance_load(strategy)
            else:
                result = {"status": "error", "error": f"Unknown operation: {operation}"}
            return {
                "orchestrator": "maestro",
                "timestamp": datetime.now().isoformat(),
                **result,
            }
        except Exception as exc:
            logger.error("Error in maestro orchestration: %s", exc)
            return {
                "status": "error",
                "error": str(exc),
                "orchestrator": "maestro",
                "timestamp": datetime.now().isoformat(),
            }

    async def route_ticket(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Route un ticket à travers le workflow d'automatisation.
        """
        try:
            if not context:
                return {
                    "status": "error",
                    "error": "Context required for ticket routing",
                }

            ticket_id = context.get("ticket_id")
            subject = context.get("subject", "")
            description = context.get("description", "")
            requestor = context.get("requestor", "unknown")

            if not ticket_id:
                return {"status": "error", "error": "ticket_id is required"}

            # Incrémenter le compteur de tickets traités
            self.metrics["tickets_processed"] += 1

            logger.info("Routing ticket %s from %s: %s", ticket_id, requestor, subject)

            # Étape 1: Classification du ticket
            classification_result = await self._classify_ticket(ticket_id, subject, description)

            if classification_result["status"] != "success":
                # Échec de classification → Escalade humaine
                return await self._escalate_to_human(
                    ticket_id, "classification_failed", classification_result
                )

            classification = classification_result["classification"]

            # Étape 2: Décision de routage basée sur la classification
            priority = TicketPriority(classification["priority"])
            complexity = TicketComplexity(classification["complexity"])
            confidence = classification["confidence"]

            # Règles de routage
            if priority == TicketPriority.URGENT:
                # Urgent → Humain immédiatement
                return await self._escalate_to_human(ticket_id, "urgent_priority", classification)

            elif complexity == TicketComplexity.SIMPLE and confidence > 0.8:
                # Simple + Haute confiance → Résolution automatique
                return await self._route_to_auto_resolver(ticket_id, classification)

            elif complexity == TicketComplexity.COMPLEX or confidence < 0.6:
                # Complexe ou faible confiance → Révision humaine
                return await self._escalate_to_human(
                    ticket_id, "complex_or_low_confidence", classification
                )

            else:
                # Modéré → Résolution automatique avec supervision
                return await self._route_to_auto_resolver(
                    ticket_id, classification, supervised=True
                )

        except Exception as exc:
            logger.error("Error routing ticket: %s", exc)
            return {
                "status": "error",
                "error": str(exc),
                "ticket_id": (ticket_id if "ticket_id" in locals() else "unknown"),
            }

    async def _classify_ticket(
        self, ticket_id: str, subject: str, description: str
    ) -> Dict[str, Any]:
        """
        Classifie un ticket en utilisant l'agent classifier.
        """
        try:
            # Import and use real classifier agent
            from agents.helpdesk.classifier import TicketClassifierAgent

            classifier = TicketClassifierAgent()
            ticket_data = {"subject": subject, "description": description}

            classification_result = await classifier.execute(
                f"Classify ticket {ticket_id}", {"ticket": ticket_data}
            )

            return {
                "status": "success",
                "classification": classification_result.get("classification", {}),
                "ticket_id": ticket_id,
            }

        except Exception as exc:
            logger.error("Error in ticket classification: %s", exc)
            # Fallback to simulation si échec
            return await self._simulate_classification(ticket_id, subject, description)

    async def _simulate_classification(
        self, ticket_id: str, subject: str, description: str
    ) -> Dict[str, Any]:
        """
        Simulation de classification basée sur les mots-clés (fallback).
        """
        try:
            logger.info(f"Simulating classification for ticket {ticket_id}")
            # Simulation basée sur les mots-clés
            text = f"{subject} {description}".lower()

            # Détection de catégorie
            if any(word in text for word in ["password", "mot de passe", "login", "connexion"]):
                category = "password"
                priority = "high"
                complexity = "simple"
                confidence = 0.9
            elif any(
                word in text
                for word in [
                    "install",
                    "installer",
                    "software",
                    "logiciel",
                    "office",
                    "application",
                    "app",
                ]
            ):
                category = "software"
                priority = "medium"
                complexity = "moderate"
                confidence = 0.8
            elif any(word in text for word in ["access", "accès", "permission", "autorisation"]):
                category = "access"
                priority = "high"
                complexity = "moderate"
                confidence = 0.7
            elif any(word in text for word in ["urgent", "urgence", "critical", "critique"]):
                category = "urgent"
                priority = "urgent"
                complexity = "complex"
                confidence = 0.95
            else:
                category = "other"
                priority = "medium"
                complexity = "moderate"
                confidence = 0.6

            return {
                "status": "success",
                "classification": {
                    "category": category,
                    "priority": priority,
                    "complexity": complexity,
                    "confidence": confidence,
                    "keywords_matched": [],
                    "suggested_agent": ("resolver" if complexity == "simple" else "human"),
                },
            }

        except Exception as exc:
            logger.error("Error in classification simulation: %s", exc)
            return {"status": "error", "error": str(exc)}

    async def _route_to_auto_resolver(
        self, ticket_id: str, classification: Dict[str, Any], supervised: bool = False
    ) -> Dict[str, Any]:
        """
        Route vers la résolution automatique.
        """
        try:
            # Vérifier la disponibilité de l'agent resolver
            if not self._is_agent_available("resolver"):
                return await self._escalate_to_human(
                    ticket_id, "resolver_unavailable", classification
                )

            # Use real resolver agent
            from agents.helpdesk.auto_resolver import HelpdeskResolverAgent

            resolver = HelpdeskResolverAgent()
            ticket_data = {
                "id": ticket_id,
                "subject": f"Ticket {ticket_id}",
                "description": (
                    f"Auto-classified ticket with category: "
                    f"{classification.get('category', 'unknown')}"
                ),
                "priority": classification.get("priority", "medium"),
                "category": classification.get("category", "general"),
            }

            context = {"ticket": ticket_data, "classification": classification}

            resolution_result = await resolver.execute(f"Resolve ticket {ticket_id}", context)

            if resolution_result["status"] == "success":
                self.metrics["auto_resolved"] += 1
                return {
                    "status": "auto_resolved",
                    "ticket_id": ticket_id,
                    "resolution": resolution_result,
                    "supervised": supervised,
                    "classification": classification,
                }
            else:
                # Échec de résolution → Escalade
                return await self._escalate_to_human(
                    ticket_id, "auto_resolution_failed", classification
                )

        except Exception as exc:
            logger.error("Error routing to auto resolver: %s", exc)
            return await self._escalate_to_human(ticket_id, "routing_error", classification)

    async def _escalate_to_human(
        self, ticket_id: str, reason: str, classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Escalade vers un agent humain.
        """
        try:
            self.metrics["escalated_to_human"] += 1

            # Simulation d'intégration avec système de tickets humains

            return {
                "status": "escalated_to_human",
                "ticket_id": ticket_id,
                "reason": reason,
                "classification": classification,
                "recommended_agent": "senior_helpdesk",
                "estimated_response_time": "30 minutes",
                "priority": classification.get("priority", "medium"),
            }

        except Exception as exc:
            logger.error("Error escalating ticket %s: %s", ticket_id, exc)
            return {"status": "error", "error": str(exc), "ticket_id": ticket_id}

    async def _simulate_auto_resolution(
        self, ticket_id: str, classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulation de résolution automatique.
        """
        try:
            logger.info(f"Simulating auto-resolution for ticket {ticket_id}")
            category = classification["category"]

            if category == "password":
                return {
                    "status": "success",
                    "action": "password_reset",
                    "details": "Password reset initiated for user",
                    "execution_time": "2 minutes",
                }
            elif category == "software":
                return {
                    "status": "success",
                    "action": "software_install",
                    "details": "Software installation initiated",
                    "execution_time": "5 minutes",
                }
            elif category == "access":
                return {
                    "status": "success",
                    "action": "access_grant",
                    "details": "Access permissions updated",
                    "execution_time": "1 minute",
                }
            else:
                return {
                    "status": "error",
                    "error": "Unsupported category for auto-resolution",
                }

        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    async def get_agent_status(self, include_health: bool = False) -> Dict[str, Any]:
        """
        Retourne le statut de tous les agents.
        """
        try:
            status: Dict[str, Any] = {
                "status": "success",
                "agents": {},
                "overall_health": "healthy",
            }

            unhealthy_count = 0

            for agent_name, agent_info in self.available_agents.items():
                agent_status = dict(agent_info)

                if include_health:
                    # Simulation de vérification de santé
                    agent_status["health_metrics"] = {
                        "response_time": "150ms",
                        "error_rate": "0.1%",
                        "uptime": "99.9%",
                    }

                status["agents"][agent_name] = agent_status

                if agent_info["status"] != "available":
                    unhealthy_count += 1

            if unhealthy_count > 0:
                status["overall_health"] = "degraded"

            return status

        except Exception as exc:
            logger.error("Error getting agent status: %s", exc)
            return {"status": "error", "error": str(exc)}

    async def rebalance_load(self, strategy: str = "round_robin") -> Dict[str, Any]:
        """
        Rééquilibre la charge entre les agents.
        """
        try:
            # Simulation de rééquilibrage

            return {
                "status": "success",
                "strategy": strategy,
                "action": "load_balanced",
                "agents_adjusted": len(self.available_agents),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as exc:
            logger.error("Error rebalancing load: %s", exc)
            return {"status": "error", "error": str(exc)}

    def _is_agent_available(self, agent_name: str) -> bool:
        """
        Vérifie si un agent est disponible.
        """
        agent = self.available_agents.get(agent_name)
        if not agent:
            return False
        try:
            load = int(str(agent.get("load", 0)))
            max_load = int(str(agent.get("max_load", 0)))
            return agent["status"] == "available" and load < max_load
        except (ValueError, TypeError):
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """
        Retourne les métriques de performance.
        """
        return dict(self.metrics)
