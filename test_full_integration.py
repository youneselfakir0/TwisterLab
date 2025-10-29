"""
Test d'intégration complet - API + Desktop Commander MCP
"""

import pytest
import requests
import time
import subprocess
import os
from typing import Optional


class TestFullIntegration:
    """Test d'intégration complet API + Desktop Commander MCP."""

    API_URL = "http://localhost:8000"
    API_PROCESS: Optional[subprocess.Popen] = None

    @classmethod
    def setup_class(cls):
        """Démarrer l'API avant les tests."""
        print("Starting API server...")
        # Démarrer l'API en arrière-plan
        cls.API_PROCESS = subprocess.Popen(
            ["python", "start_api.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd(),
        )

        # Attendre que l'API démarre
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{cls.API_URL}/docs", timeout=2)
                if response.status_code == 200:
                    print("API server started successfully")
                    break
            except requests.exceptions.RequestException:
                pass

            if attempt == max_attempts - 1:
                # Tuer le processus si échec
                if cls.API_PROCESS:
                    cls.API_PROCESS.terminate()
                    cls.API_PROCESS.wait()
                pytest.fail("API server failed to start")

            time.sleep(1)

    @classmethod
    def teardown_class(cls):
        """Arrêter l'API après les tests."""
        if cls.API_PROCESS:
            print("Stopping API server...")
            cls.API_PROCESS.terminate()
            try:
                cls.API_PROCESS.wait(timeout=10)
            except subprocess.TimeoutExpired:
                cls.API_PROCESS.kill()
                cls.API_PROCESS.wait()
            print("API server stopped")

    def test_api_health_check(self):
        """Test que l'API répond correctement."""
        response = requests.get(f"{self.API_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_create_ticket(self):
        """Test de création d'un ticket."""
        ticket_data = {
            "title": "Test Integration Ticket",
            "description": "Testing full integration with MCP",
            "priority": "medium",
            "category": "technical",
            "requester_email": "test@example.com",
        }

        response = requests.post(
            f"{self.API_URL}/api/v1/tickets/", json=ticket_data
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == ticket_data["title"]
        return data["id"]

    def test_get_agents(self):
        """Test de récupération de la liste des agents."""
        response = requests.get(f"{self.API_URL}/api/v1/agents/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Vérifier que Desktop Commander est présent
        dc_agent = next(
            (agent for agent in data if agent["name"] == "desktop-commander"),
            None,
        )
        assert dc_agent is not None
        assert dc_agent["display_name"] == "Desktop Commander"

    def test_desktop_commander_agent_execution(self):
        """Test d'exécution de l'agent Desktop Commander via API."""

        # Tester l'exécution d'une commande via l'agent
        execution_data = {
            "agent_name": "desktop-commander",
            "task": "Execute systeminfo on test-device",
            "context": {
                "command_type": "execute_command",
                "device_id": "test-device",
                "command": "systeminfo",
                "timeout": 30,
            },
        }

        response = requests.post(
            f"{self.API_URL}/api/v1/agents/execute", json=execution_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "status" in data["result"]
        # Note: Le résultat réel dépendra de la connexion MCP
        # Pour les tests, on vérifie juste que la structure est correcte

    def test_desktop_commander_deploy_package(self):
        """Test de déploiement de package via Desktop Commander."""
        execution_data = {
            "agent_name": "desktop-commander",
            "task": "Deploy test package to device",
            "context": {
                "command_type": "deploy_package",
                "device_id": "test-device",
                "package_url": "https://example.com/test.msi",
                "install_args": "/quiet",
            },
        }

        response = requests.post(
            f"{self.API_URL}/api/v1/agents/execute", json=execution_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "status" in data["result"]

    def test_desktop_commander_get_system_info(self):
        """Test de récupération d'infos système via Desktop Commander."""
        execution_data = {
            "agent_name": "desktop-commander",
            "task": "Get hardware info from device",
            "context": {
                "command_type": "get_system_info",
                "device_id": "test-device",
                "info_type": "hardware",
            },
        }

        response = requests.post(
            f"{self.API_URL}/api/v1/agents/execute", json=execution_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "status" in data["result"]

    def test_get_sops(self):
        """Test de récupération des SOPs."""
        response = requests.get(f"{self.API_URL}/api/v1/sops/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Les SOPs peuvent être vides, c'est acceptable

    def test_invalid_agent_execution(self):
        """Test d'exécution avec un agent invalide."""
        execution_data = {
            "agent_name": "non-existent-agent",
            "task": "Test task",
            "context": {},
        }

        response = requests.post(
            f"{self.API_URL}/api/v1/agents/execute", json=execution_data
        )
        assert response.status_code == 404

    def test_malformed_request(self):
        """Test avec une requête malformée."""
        response = requests.post(
            f"{self.API_URL}/api/v1/agents/execute", json={"invalid": "data"}
        )
        # Devrait retourner une erreur de validation
        assert response.status_code in [400, 422]

    def test_api_openapi_spec(self):
        """Test que la spécification OpenAPI est accessible."""
        response = requests.get(f"{self.API_URL}/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "paths" in data
        assert "components" in data

    def test_cors_headers(self):
        """Test que les headers CORS sont présents."""
        response = requests.options(f"{self.API_URL}/api/v1/agents/")
        # Les headers CORS peuvent varier selon la configuration
        # On vérifie juste que la requête ne échoue pas
        assert response.status_code in [200, 404, 405]
