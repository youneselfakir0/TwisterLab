"""
Tests d'Intégration MCP Desktop Commander
Tests du workflow complet: Registration → Command Execution → Monitoring
"""

import asyncio

import pytest

from agents.mcp.desktop_commander_server import (
    CommandStatus,
    DesktopCommanderMCPServer,
    DeviceStatus,
)


@pytest.fixture
def mcp_server():
    """Fixture pour créer un serveur MCP"""
    return DesktopCommanderMCPServer()


@pytest.fixture
def sample_client_info():
    """Fixture pour informations client de test"""
    return {
        "device_id": "CLIENT-TEST-001",
        "hostname": "DESKTOP-TEST01",
        "ip_address": "192.168.1.100",
        "os_info": {"name": "Windows 11 Pro", "version": "10.0.22621", "build": "22621"},
        "metadata": {"department": "IT", "location": "Building A"},
    }


@pytest.mark.asyncio
async def test_register_client(mcp_server, sample_client_info):
    """Test l'enregistrement d'un client"""
    result = await mcp_server.register_client(**sample_client_info)

    assert result["status"] == "success"
    assert result["device_id"] == "CLIENT-TEST-001"
    assert "server_time" in result

    # Vérifier que le client est dans la liste
    assert "CLIENT-TEST-001" in mcp_server.connected_clients


@pytest.mark.asyncio
async def test_unregister_client(mcp_server, sample_client_info):
    """Test le désenregistrement d'un client"""
    # Enregistrer d'abord
    await mcp_server.register_client(**sample_client_info)

    # Désenregistrer
    result = await mcp_server.unregister_client("CLIENT-TEST-001")

    assert result["status"] == "success"
    assert "CLIENT-TEST-001" not in mcp_server.connected_clients


@pytest.mark.asyncio
async def test_execute_allowed_command(mcp_server, sample_client_info):
    """Test l'exécution d'une commande autorisée"""
    # Enregistrer le client
    await mcp_server.register_client(**sample_client_info)

    # Exécuter une commande autorisée
    result = await mcp_server.execute_command(device_id="CLIENT-TEST-001", command="systeminfo")

    assert result["status"] == "success"
    assert result["device_id"] == "CLIENT-TEST-001"
    assert "output" in result
    assert "DESKTOP" in result["output"]  # Vérifier la simulation


@pytest.mark.asyncio
async def test_execute_denied_command(mcp_server, sample_client_info):
    """Test qu'une commande non autorisée est refusée"""
    # Enregistrer le client
    await mcp_server.register_client(**sample_client_info)

    # Tenter d'exécuter une commande dangereuse
    result = await mcp_server.execute_command(
        device_id="CLIENT-TEST-001", command="del C:\\Windows"  # Commande interdite
    )

    assert result["status"] == CommandStatus.DENIED.value
    assert "not in whitelist" in result["error"]
    assert "allowed_commands" in result


@pytest.mark.asyncio
async def test_execute_on_nonexistent_client(mcp_server):
    """Test l'exécution sur un client qui n'existe pas"""
    result = await mcp_server.execute_command(device_id="NONEXISTENT", command="systeminfo")

    assert result["status"] == CommandStatus.FAILED.value
    assert "not connected" in result["error"]


@pytest.mark.asyncio
async def test_get_client_status(mcp_server, sample_client_info):
    """Test la récupération du statut d'un client"""
    # Enregistrer le client
    await mcp_server.register_client(**sample_client_info)

    # Récupérer le statut
    result = await mcp_server.get_client_status("CLIENT-TEST-001")

    assert result["status"] == "success"
    assert result["client"]["hostname"] == "DESKTOP-TEST01"
    assert result["client"]["status"] == DeviceStatus.CONNECTED.value


@pytest.mark.asyncio
async def test_list_clients(mcp_server, sample_client_info):
    """Test la liste de tous les clients"""
    # Enregistrer plusieurs clients
    await mcp_server.register_client(**sample_client_info)

    client_2 = sample_client_info.copy()
    client_2["device_id"] = "CLIENT-TEST-002"
    client_2["hostname"] = "DESKTOP-TEST02"
    await mcp_server.register_client(**client_2)

    # Lister les clients
    result = await mcp_server.list_clients()

    assert result["status"] == "success"
    assert result["total_clients"] == 2
    assert len(result["clients"]) == 2


@pytest.mark.asyncio
async def test_command_history(mcp_server, sample_client_info):
    """Test l'historique des commandes"""
    # Enregistrer le client
    await mcp_server.register_client(**sample_client_info)

    # Exécuter plusieurs commandes
    await mcp_server.execute_command("CLIENT-TEST-001", "systeminfo")
    await mcp_server.execute_command("CLIENT-TEST-001", "ipconfig")
    await mcp_server.execute_command("CLIENT-TEST-001", "ping 8.8.8.8")

    # Récupérer l'historique
    history = await mcp_server.get_command_history()

    assert history["status"] == "success"
    assert history["total_commands"] >= 3


@pytest.mark.asyncio
async def test_healthcheck(mcp_server, sample_client_info):
    """Test le healthcheck du serveur"""
    # Enregistrer un client
    await mcp_server.register_client(**sample_client_info)

    # Vérifier la santé
    health = await mcp_server.healthcheck()

    assert health["status"] == "healthy"
    assert health["total_clients"] == 1
    assert health["connected_clients"] == 1
    assert health["whitelist_commands"] > 0


@pytest.mark.asyncio
async def test_multiple_commands_update_client_stats(mcp_server, sample_client_info):
    """Test que l'exécution de commandes met à jour les stats du client"""
    # Enregistrer le client
    await mcp_server.register_client(**sample_client_info)

    # Exécuter plusieurs commandes
    for i in range(5):
        await mcp_server.execute_command("CLIENT-TEST-001", "systeminfo")

    # Vérifier les stats
    status = await mcp_server.get_client_status("CLIENT-TEST-001")
    client = status["client"]

    assert client["commands_executed"] == 5
    assert client["last_command"] is not None
    assert client["last_command"]["command"] == "systeminfo"


@pytest.mark.asyncio
async def test_whitelist_validation():
    """Test la validation de la whitelist"""
    server = DesktopCommanderMCPServer()

    # Commandes autorisées
    assert server._is_command_allowed("systeminfo") is True
    assert server._is_command_allowed("ipconfig /all") is True
    assert server._is_command_allowed("ping 8.8.8.8") is True

    # Commandes interdites
    assert server._is_command_allowed("del C:\\Windows") is False
    assert server._is_command_allowed("format C:") is False
    assert server._is_command_allowed("shutdown /s /t 0") is False


# Test du workflow complet
@pytest.mark.asyncio
async def test_complete_workflow():
    """Test du workflow complet: Registration → Execution → Monitoring"""
    server = DesktopCommanderMCPServer()

    # Étape 1: Enregistrer un client
    print("\n=== Étape 1: Registration ===")
    reg_result = await server.register_client(
        device_id="WORKFLOW-CLIENT",
        hostname="WORKFLOW-TEST",
        ip_address="10.0.0.100",
        os_info={"name": "Windows 11", "version": "22H2"},
    )
    print(f"Registration: {reg_result['status']}")
    assert reg_result["status"] == "success"

    # Étape 2: Vérifier le statut
    print("\n=== Étape 2: Status Check ===")
    status = await server.get_client_status("WORKFLOW-CLIENT")
    print(f"Client status: {status['client']['status']}")
    assert status["client"]["status"] == DeviceStatus.CONNECTED.value

    # Étape 3: Exécuter des commandes
    print("\n=== Étape 3: Command Execution ===")
    commands = ["systeminfo", "ipconfig", "ping 8.8.8.8"]

    for cmd in commands:
        result = await server.execute_command("WORKFLOW-CLIENT", cmd)
        print(f"Command '{cmd}': {result['status']}")
        assert result["status"] == "success"

    # Étape 4: Vérifier l'historique
    print("\n=== Étape 4: History Check ===")
    history = await server.get_command_history(device_id="WORKFLOW-CLIENT")
    print(f"Total commands executed: {history['total_commands']}")
    assert history["total_commands"] >= 3

    # Étape 5: Healthcheck
    print("\n=== Étape 5: Healthcheck ===")
    health = await server.healthcheck()
    print(f"Server health: {health['status']}")
    print(f"Connected clients: {health['connected_clients']}")
    assert health["status"] == "healthy"

    # Étape 6: Désenregistrer
    print("\n=== Étape 6: Unregistration ===")
    unreg_result = await server.unregister_client("WORKFLOW-CLIENT")
    print(f"Unregistration: {unreg_result['status']}")
    assert unreg_result["status"] == "success"

    print("\n=== Workflow Complete ===")


if __name__ == "__main__":
    # Exécuter le test du workflow complet
    print("=" * 60)
    print("  MCP Desktop Commander Integration Tests")
    print("=" * 60)

    asyncio.run(test_complete_workflow())

    print("\n" + "=" * 60)
    print("  All Tests Passed!")
    print("=" * 60)
