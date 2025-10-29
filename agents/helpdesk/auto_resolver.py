"""
TwisterLab - Helpdesk Resolver Agent
Automatically resolves common IT helpdesk tickets using SOPs
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..base import TwisterAgent
from ..database.config import get_db
from ..database.services import SOPService

logger = logging.getLogger(__name__)


class HelpdeskResolverAgent(TwisterAgent):
    """
    Agent spécialisé dans la résolution automatique des tickets IT helpdesk.

    Utilise les SOPs (Standard Operating Procedures) pour:
    - Réinitialiser les mots de passe
    - Installer des logiciels
    - Accorder des accès
    - Résoudre des problèmes courants
    """

    def __init__(self):
        super().__init__(
            name="helpdesk-resolver",
            display_name="IT Helpdesk Resolver",
            description="Resolves common IT helpdesk tickets automatically (password resets, software installs, access requests)",
            role="helpdesk",
            instructions="""
            You are an IT Helpdesk Agent specializing in resolving common IT support tickets.
            You can automatically handle password resets, software installations, access requests, and basic troubleshooting.
            For complex issues, escalate to human agents.

            Always use the SOP database to find the appropriate resolution procedure.
            Execute steps systematically and report progress.
            """,
            model="llama-3.2",
            temperature=0.3,  # Précision pour les opérations IT
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "reset_password",
                        "description": "Reset user password in Active Directory",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "username": {
                                    "type": "string",
                                    "description": "Username to reset password for"
                                },
                                "temporary_password": {
                                    "type": "string",
                                    "description": "Temporary password to set"
                                }
                            },
                            "required": ["username"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "install_software",
                        "description": "Install software via Desktop Commander on user's machine",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "device_id": {
                                    "type": "string",
                                    "description": "Target device identifier"
                                },
                                "software_name": {
                                    "type": "string",
                                    "description": "Name of software to install"
                                },
                                "version": {
                                    "type": "string",
                                    "description": "Software version (optional)"
                                }
                            },
                            "required": ["device_id", "software_name"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "grant_access",
                        "description": "Grant user access to a resource or group",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "username": {
                                    "type": "string",
                                    "description": "Username to grant access to"
                                },
                                "resource": {
                                    "type": "string",
                                    "description": "Resource or group name"
                                }
                            },
                            "required": ["username", "resource"]
                        }
                    }
                }
            ]
        )

        # Plus besoin de session persistante - on obtient des sessions à la demande

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Exécute la résolution d'un ticket IT.

        Args:
            task: Description de la tâche (contient les détails du ticket)
            context: Contexte additionnel (classification, SOPs, etc.)

        Returns:
            Dict avec le résultat de la résolution
        """
        try:
            logger.info(f"Helpdesk resolver executing task: {task}")

            # Extraire les informations du ticket
            ticket_data = context.get("ticket", {}) if context else {}
            ticket_id = ticket_data.get("id") or context.get("ticket_id", "unknown")
            category = context.get("classification", {}).get("category", "unknown") if context else "unknown"

            # Trouver le SOP approprié
            sop = await self._find_appropriate_sop(category, task)

            if not sop:
                return {
                    "status": "escalation_required",
                    "ticket_id": ticket_id,
                    "reason": f"No SOP found for category: {category}",
                    "timestamp": datetime.now().isoformat()
                }

            # Exécuter le SOP
            execution_result = await self._execute_sop(sop, ticket_data)

            logger.info(f"Ticket {ticket_id} resolution: {execution_result['status']}")

            return {
                "status": execution_result["status"],
                "ticket_id": ticket_id,
                "sop_used": sop["title"],
                "steps_executed": execution_result.get("steps_executed", []),
                "timestamp": datetime.now().isoformat(),
                **execution_result
            }

        except Exception as e:
            logger.error(f"Error in helpdesk resolver execution: {e}")
            return {
                "status": "error",
                "error": str(e),
                "ticket_id": context.get("ticket_id", "unknown") if context else "unknown"
            }

    async def _find_appropriate_sop(self, category: str, task_description: str) -> Optional[Dict[str, Any]]:
        """
        Trouve le SOP approprié pour la catégorie et description du ticket.
        """
        try:
            # Obtenir une nouvelle session pour cette opération
            async for session in get_db():
                sop_service = SOPService(session)

                # Rechercher par catégorie
                sops = await sop_service.list_sops(
                    category=category,
                    limit=10
                )

                if not sops:
                    logger.warning(f"No SOPs found for category: {category}")
                    return None

                # Pour l'instant, retourner le premier SOP trouvé
                # TODO: Implémenter une logique de matching plus sophistiquée
                sop = sops[0]
                logger.info(f"Selected SOP: {sop.title} for category: {category}")
                return {
                    "id": sop.id,
                    "title": sop.title,
                    "description": sop.description,
                    "category": sop.category,
                    "steps": sop.steps,
                    "applicable_issues": sop.applicable_issues
                }

        except Exception as e:
            logger.error(f"Error finding SOP: {e}")
            return None

    async def _execute_sop(self, sop: Dict[str, Any], ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute les étapes du SOP.

        Pour l'instant, simule l'exécution (pas d'actions réelles sur AD, etc.)
        """
        try:
            steps = sop.get("steps", [])
            executed_steps = []

            logger.info(f"Executing SOP: {sop['title']} with {len(steps)} steps")

            for i, step in enumerate(steps, 1):
                step_result = await self._execute_step(step, ticket_data)
                executed_steps.append({
                    "step_number": i,
                    "description": step,
                    "status": step_result["status"],
                    "output": step_result.get("output", "")
                })

                # Si une étape échoue, arrêter l'exécution
                if step_result["status"] == "failed":
                    return {
                        "status": "failed",
                        "steps_executed": executed_steps,
                        "failure_step": i,
                        "error": step_result.get("error", "Unknown error")
                    }

            return {
                "status": "success",
                "steps_executed": executed_steps,
                "total_steps": len(steps)
            }

        except Exception as e:
            logger.error(f"Error executing SOP: {e}")
            return {
                "status": "error",
                "error": str(e),
                "steps_executed": executed_steps if 'executed_steps' in locals() else []
            }

    async def _execute_step(self, step: str, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute une étape individuelle du SOP.

        Pour l'instant, simule l'exécution.
        """
        try:
            logger.info(f"Executing step: {step}")

            # Simulation basée sur le contenu de l'étape
            step_lower = step.lower()

            if "password" in step_lower or "mot de passe" in step_lower:
                # Simuler reset password
                return {
                    "status": "success",
                    "output": "Password reset completed successfully"
                }

            elif "install" in step_lower or "installer" in step_lower:
                # Simuler installation software
                return {
                    "status": "success",
                    "output": "Software installation completed"
                }

            elif "access" in step_lower or "accès" in step_lower:
                # Simuler grant access
                return {
                    "status": "success",
                    "output": "Access granted successfully"
                }

            else:
                # Étape générique
                return {
                    "status": "success",
                    "output": f"Step completed: {step}"
                }

        except Exception as e:
            logger.error(f"Error executing step '{step}': {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    # Tool implementations (pour intégration MCP future)

    async def reset_password(self, username: str, temporary_password: Optional[str] = None) -> Dict[str, Any]:
        """Reset user password in Active Directory."""
        try:
            # TODO: Intégration réelle avec AD via MCP
            logger.info(f"Resetting password for user: {username}")

            return {
                "status": "success",
                "username": username,
                "temporary_password": temporary_password or "TempPass123!",
                "message": "Password reset completed"
            }

        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def install_software(self, device_id: str, software_name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """Install software via Desktop Commander."""
        try:
            # TODO: Intégration avec Desktop Commander MCP
            logger.info(f"Installing {software_name} on device: {device_id}")

            return {
                "status": "success",
                "device_id": device_id,
                "software": software_name,
                "version": version,
                "message": "Software installation initiated"
            }

        except Exception as e:
            logger.error(f"Error installing software: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def grant_access(self, username: str, resource: str) -> Dict[str, Any]:
        """Grant user access to a resource or group."""
        try:
            # TODO: Intégration avec AD via MCP
            logger.info(f"Granting access to {resource} for user: {username}")

            return {
                "status": "success",
                "username": username,
                "resource": resource,
                "message": "Access granted successfully"
            }

        except Exception as e:
            logger.error(f"Error granting access: {e}")
            return {
                "status": "error",
                "error": str(e)
            }