"""
Integration tests for Ollama Client with Failover

Tests:
- Primary endpoint success
- Failover to secondary when primary down
- Health monitoring
- Metrics collection
- Model listing
"""

import os

import pytest

from agents.llm.ollama_client import OllamaClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ollama_generate_success_on_primary():
    """Test génération réussie sur endpoint primaire (edgeserver)."""
    client = OllamaClient()

    result = await client.generate(
        prompt="Hello, how are you?", model="llama3.2:1b", temperature=0.7
    )

    assert result["status"] == "success", f"Expected success, got: {result}"
    assert "response" in result
    assert result["response"], "Response should not be empty"
    assert result["model"] == "llama3.2:1b"
    assert result["endpoint"] == "http://192.168.0.30:11434"

    # Vérifier timing
    assert "timing" in result
    assert result["timing"]["total_seconds"] > 0
    assert result["timing"]["eval_count"] > 0

    # Vérifier métriques
    metrics = client.get_metrics()
    assert metrics["requests_total"] >= 1
    assert metrics["requests_success"] >= 1
    assert metrics["success_rate_percent"] > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ollama_failover_to_secondary_when_primary_down():
    """Test failover vers secondary si primary down."""
    client = OllamaClient()

    # Marquer primary comme down
    client.metrics["endpoint_health"]["http://192.168.0.30:11434"] = False

    result = await client.generate(
        prompt="Test failover", model="llama3.2:1b", max_retries=1  # Retry rapide
    )

    # Si secondary (corertx) est configuré et up, devrait réussir
    # Sinon, devrait échouer avec "All Ollama servers unavailable"
    if result["status"] == "success":
        # Secondary a répondu
        assert "192.168.0.31" in result["endpoint"], "Should use secondary endpoint"
        assert metrics["failovers"] >= 1, "Should have recorded failover"
    else:
        # Secondary pas disponible
        assert result["status"] == "error"
        assert "All Ollama servers unavailable" in result["error"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ollama_health_check():
    """Test health check de tous les endpoints."""
    client = OllamaClient()

    health = await client.health_check_all()

    assert isinstance(health, dict)
    assert len(health) == 2, "Should check both endpoints"

    # Primary (edgeserver) devrait être up
    assert "http://192.168.0.30:11434" in health
    assert health["http://192.168.0.30:11434"] is True, "Edgeserver should be healthy"

    # Secondary peut être up ou down selon config
    assert "http://192.168.0.31:11434" in health


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ollama_list_models():
    """Test listing des modèles disponibles."""
    client = OllamaClient()

    models = await client.list_models()

    assert isinstance(models, list)

    if models:  # Si endpoint up
        assert len(models) > 0

        # Vérifier structure
        for model in models:
            assert "name" in model
            assert "size" in model or "modified_at" in model

        # llama3.2:1b devrait être présent
        model_names = [m["name"] for m in models]
        assert "llama3.2:1b" in model_names, f"llama3.2:1b not found in {model_names}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ollama_metrics_accuracy():
    """Test précision des métriques."""
    client = OllamaClient()
    client.reset_metrics()  # Reset pour test propre

    # Faire 3 requêtes
    for i in range(3):
        result = await client.generate(prompt=f"Test request {i+1}", model="llama3.2:1b")

    metrics = client.get_metrics()

    # Vérifier compteurs
    assert metrics["requests_total"] == 3, "Should have 3 total requests"
    assert metrics["requests_success"] >= 2, "Should have at least 2 successes"

    # Vérifier latence
    assert metrics["avg_latency_seconds"] > 0
    assert len(client.metrics["latency_history"]) == metrics["requests_success"]

    # Vérifier percentiles
    assert metrics["latency_p50"] > 0
    assert metrics["latency_p95"] >= metrics["latency_p50"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ollama_timeout_handling():
    """Test gestion des timeouts."""
    client = OllamaClient()

    result = await client.generate(
        prompt="Very long prompt that might timeout" * 100,
        model="llama3.2:1b",
        timeout=1,  # Timeout très court (1 seconde)
        max_retries=1,
    )

    # Devrait soit réussir rapidement, soit timeout
    if result["status"] == "error":
        assert (
            "unavailable" in result["error"].lower() or "timeout" in result.get("error", "").lower()
        )


@pytest.mark.integration
def test_ollama_get_metrics_format():
    """Test format des métriques retournées."""
    client = OllamaClient()
    metrics = client.get_metrics()

    # Vérifier présence de toutes les clés
    required_keys = [
        "requests_total",
        "requests_success",
        "requests_failed",
        "success_rate_percent",
        "failovers",
        "current_endpoint",
        "endpoint_health",
        "avg_latency_seconds",
        "latency_p50",
        "latency_p95",
    ]

    for key in required_keys:
        assert key in metrics, f"Missing key: {key}"

    # Vérifier types
    assert isinstance(metrics["requests_total"], int)
    assert isinstance(metrics["success_rate_percent"], float)
    assert isinstance(metrics["endpoint_health"], dict)
    assert isinstance(metrics["current_endpoint"], str)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ollama_concurrent_requests():
    """Test requêtes concurrentes."""
    import asyncio

    client = OllamaClient()
    client.reset_metrics()

    # Lancer 5 requêtes en parallèle
    tasks = [client.generate(f"Concurrent test {i}", model="llama3.2:1b") for i in range(5)]

    results = await asyncio.gather(*tasks)

    # Vérifier que toutes ont répondu
    assert len(results) == 5

    # Compter succès
    successes = sum(1 for r in results if r["status"] == "success")
    assert successes >= 4, "Should have at least 4/5 successes"

    # Vérifier métriques
    metrics = client.get_metrics()
    assert metrics["requests_total"] == 5
