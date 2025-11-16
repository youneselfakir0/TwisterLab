#!/usr/bin/env python3
"""
Script de test de charge pour TwisterLab API
Utilise Locust pour simuler des utilisateurs et mesurer les performances
"""

import json
import random

from locust import HttpUser, between, task


class TwisterLabUser(HttpUser):
    """Utilisateur simulé pour les tests de charge"""

    # Temps d'attente entre les tâches (entre 1 et 3 secondes)
    wait_time = between(1, 3)

    def on_start(self):
        """Initialisation de l'utilisateur"""
        self.token = None

    @task(1)
    def health_check(self):
        """Test de l'endpoint health"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(2)
    def get_docs(self):
        """Test de l'endpoint documentation"""
        with self.client.get("/docs", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Docs endpoint failed: {response.status_code}")

    @task(3)
    def get_openapi(self):
        """Test de l'endpoint OpenAPI"""
        with self.client.get("/openapi.json", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"OpenAPI endpoint failed: {response.status_code}")

    @task(2)
    def list_tickets(self):
        """Test de récupération des tickets"""
        with self.client.get("/api/v1/tickets/", catch_response=True) as response:
            if response.status_code in [200, 404]:  # 404 si pas de données
                response.success()
            else:
                response.failure(f"Tickets list failed: {response.status_code}")

    @task(1)
    def list_agents(self):
        """Test de récupération des agents"""
        with self.client.get("/api/v1/agents/", catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Agents list failed: {response.status_code}")

    @task(1)
    def list_sops(self):
        """Test de récupération des SOPs"""
        with self.client.get("/api/v1/sops/", catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"SOPs list failed: {response.status_code}")

    @task(1)
    def orchestrator_status(self):
        """Test du statut de l'orchestrateur"""
        with self.client.get("/api/v1/orchestrator/status", catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Orchestrator status failed: {response.status_code}")


class TwisterLabWriteUser(HttpUser):
    """Utilisateur simulé pour les tests d'écriture (moins fréquent)"""

    wait_time = between(5, 15)  # Moins fréquent

    @task(1)
    def create_ticket(self):
        """Test de création de ticket (si autorisé)"""
        ticket_data = {
            "title": f"Test Ticket {random.randint(1, 1000)}",
            "description": "Ticket créé automatiquement pour test de charge",
            "priority": random.choice(["low", "medium", "high"]),
            "category": "test",
        }

        with self.client.post(
            "/api/v1/tickets/", json=ticket_data, catch_response=True
        ) as response:
            if response.status_code in [201, 401, 403]:  # 401/403 si auth requise
                response.success()
            else:
                response.failure(f"Ticket creation failed: {response.status_code}")
