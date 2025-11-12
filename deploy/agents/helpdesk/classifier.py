"""
TwisterLab - Ticket Classifier Agent
Classifies incoming helpdesk tickets by category, priority, and complexity
"""

import importlib.util
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

# Import TwisterAgent directly from base.py file
base_file_path = os.path.join(os.path.dirname(__file__), "..", "base.py")
spec = importlib.util.spec_from_file_location("base_module", base_file_path)
base_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base_module)
TwisterAgent = base_module.TwisterAgent
from ..database.config import get_db
from ..database.services import SOPService

logger = logging.getLogger(__name__)


class TicketClassifierAgent(TwisterAgent):
    """
    Agent spécialisé dans la classification des tickets IT helpdesk.

    Utilise la base de données SOPs pour déterminer:
    - Catégorie (password, software, access, hardware, network, other)
    - Priorité (low, medium, high, urgent)
    - Complexité (simple, moderate, complex)
    - Confiance (0.0-1.0)
    """

    def __init__(self):
        super().__init__(
            name="classifier",
            display_name="Ticket Classifier",
            description="Classifies incoming helpdesk tickets by category, priority, and complexity",
            role="classifier",
            instructions="""
            You are a Ticket Classifier Agent. Analyze incoming helpdesk tickets and classify them by:
            1. Category (password, software, access, hardware, network, other)
            2. Priority (low, medium, high, urgent)
            3. Complexity (simple, moderate, complex)
            4. Confidence score (0.0-1.0)

            Use the SOP database to inform your classification decisions.
            Provide structured output for routing decisions.
            """,
            model="deepseek-r1",
            temperature=0.2,  # Précision pour classification
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "classify_ticket",
                        "description": "Classify a helpdesk ticket",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "ticket_id": {
                                    "type": "string",
                                    "description": "Ticket identifier",
                                },
                                "subject": {
                                    "type": "string",
                                    "description": "Ticket subject",
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Ticket description",
                                },
                            },
                            "required": ["ticket_id", "subject", "description"],
                        },
                    },
                }
            ],
        )

        # Plus besoin de session persistante - on obtient des sessions à la demande

    async def execute(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Exécute la classification d'un ticket.

        Args:
            task: Description de la tâche (contient les détails du ticket)
            context: Contexte additionnel (optionnel)

        Returns:
            Dict avec la classification du ticket
        """
        try:
            logger.info(f"Classifier agent executing task: {task}")

            # Extraire les informations du ticket depuis le contexte
            ticket_data = context.get("ticket", {}) if context else {}
            ticket_id = ticket_data.get("id") or context.get("ticket_id", "unknown")
            subject = ticket_data.get("subject", "")
            description = ticket_data.get("description", "")

            # Si pas de données spécifiques, utiliser le task comme description
            if not subject and not description:
                description = task

            # Classifier le ticket
            classification = await self._classify_ticket(
                ticket_id, subject, description
            )

            logger.info(f"Ticket {ticket_id} classified: {classification}")

            return {
                "status": "success",
                "ticket_id": ticket_id,
                "classification": classification,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in classifier execution: {e}")
            return {
                "status": "error",
                "error": str(e),
                "ticket_id": context.get("ticket_id", "unknown")
                if context
                else "unknown",
            }

    async def _classify_ticket(
        self, ticket_id: str, subject: str, description: str
    ) -> Dict[str, Any]:
        """
        Logique de classification principale.

        Utilise les SOPs existants pour informer la classification.
        """
        # Combiner subject et description pour analyse
        full_text = f"{subject} {description}".lower()

        # Récupérer tous les SOPs pour analyse
        sops = await self._get_all_sops()

        # Classification par catégorie
        category = self._determine_category(full_text, sops)

        # Classification par priorité
        priority = self._determine_priority(full_text, category)

        # Classification par complexité
        complexity = self._determine_complexity(full_text, sops)

        # Score de confiance
        confidence = self._calculate_confidence(full_text, category, sops)

        return {
            "category": category,
            "priority": priority,
            "complexity": complexity,
            "confidence": confidence,
            "routing_recommendation": self._get_routing_recommendation(
                category, priority, complexity, confidence
            ),
        }

    async def _get_all_sops(self) -> list:
        """Récupère tous les SOPs depuis la base de données."""
        try:
            # Obtenir une nouvelle session pour cette opération
            async for session in get_db():
                sop_service = SOPService(session)
                sops = await sop_service.list_sops(limit=100)
                return sops
        except Exception as e:
            logger.warning(f"Could not retrieve SOPs: {e}")
            return []

    def _determine_category(self, text: str, sops: list) -> str:
        """Détermine la catégorie du ticket."""
        # Mots-clés par catégorie
        categories = {
            "password": [
                "password",
                "mot de passe",
                "mdp",
                "login",
                "connexion",
                "authentification",
            ],
            "software": [
                "software",
                "logiciel",
                "installer",
                "installation",
                "programme",
                "application",
                "install",
                "office",
                "app",
            ],
            "access": [
                "access",
                "accès",
                "permission",
                "droits",
                "autorisation",
                "partage",
            ],
            "hardware": [
                "hardware",
                "matériel",
                "ordinateur",
                "écran",
                "clavier",
                "souris",
                "imprimante",
            ],
            "network": [
                "network",
                "réseau",
                "internet",
                "wifi",
                "connexion",
                "vpn",
                "mail",
            ],
            "other": [],
        }

        # Compter les correspondances
        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[category] = score

        # Catégorie avec le plus haut score
        best_category = max(scores, key=scores.get)

        # Si score = 0, utiliser "other"
        if scores[best_category] == 0:
            return "other"

        return best_category

    def _determine_priority(self, text: str, category: str) -> str:
        """Détermine la priorité du ticket."""
        # Mots-clés d'urgence
        urgent_keywords = [
            "urgent",
            "urgence",
            "critique",
            "bloquant",
            "ne fonctionne pas",
            "cassé",
        ]
        high_keywords = ["important", "vite", "rapidement", "problème", "erreur"]
        medium_keywords = ["question", "aide", "comment", "besoin"]

        if any(keyword in text for keyword in urgent_keywords):
            return "urgent"
        elif any(keyword in text for keyword in high_keywords):
            return "high"
        elif any(keyword in text for keyword in medium_keywords):
            return "medium"
        else:
            return "low"

    def _determine_complexity(self, text: str, sops: list) -> str:
        """Détermine la complexité du ticket."""
        # Si on a des SOPs correspondants, c'est probablement simple
        # Sinon, c'est plus complexe

        # Pour l'instant, logique simple basée sur la longueur et les mots-clés
        if len(text.split()) < 10:
            return "simple"
        elif len(text.split()) < 50:
            return "moderate"
        else:
            return "complex"

    def _calculate_confidence(self, text: str, category: str, sops: list) -> float:
        """Calcule le score de confiance de la classification."""
        # Base confidence
        confidence = 0.5

        # +0.3 si catégorie claire
        if category != "other":
            confidence += 0.3

        # +0.2 si texte détaillé
        if len(text.split()) > 20:
            confidence += 0.2

        return min(confidence, 1.0)

    def _get_routing_recommendation(
        self, category: str, priority: str, complexity: str, confidence: float
    ) -> str:
        """Détermine la recommandation de routing."""
        if priority == "urgent":
            return "route_to_human_immediate"
        elif confidence > 0.8 and complexity == "simple":
            return "route_to_auto_resolution"
        elif confidence > 0.6:
            return "route_to_ai_agent"
        else:
            return "route_to_human_supervisor"
