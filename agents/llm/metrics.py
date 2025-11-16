"""
Prometheus Metrics for Ollama LLM Client

Provides observability for Ollama multi-endpoint failover system:
- Request counters (total, success, fail)
- Latency histograms
- Endpoint health gauges
- Failover counters
"""

from prometheus_client import Counter, Gauge, Histogram, Info

# ============================================================================
# Compteurs
# ============================================================================

ollama_requests_total = Counter(
    "ollama_requests_total",
    "Total number of requests sent to Ollama",
    ["endpoint", "model", "status"],
)

ollama_failovers_total = Counter(
    "ollama_failovers_total", "Total number of failovers between Ollama endpoints"
)


# ============================================================================
# Histogrammes (Latence)
# ============================================================================

ollama_request_duration_seconds = Histogram(
    "ollama_request_duration_seconds",
    "Duration of Ollama requests in seconds",
    ["endpoint", "model"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0],
)

ollama_tokens_generated = Histogram(
    "ollama_tokens_generated",
    "Number of tokens generated per request",
    ["endpoint", "model"],
    buckets=[10, 50, 100, 200, 500, 1000, 2000],
)


# ============================================================================
# Gauges (État)
# ============================================================================

ollama_endpoint_health = Gauge(
    "ollama_endpoint_health", "Health status of Ollama endpoint (1=healthy, 0=down)", ["endpoint"]
)

ollama_current_endpoint = Info("ollama_current_endpoint", "Currently active Ollama endpoint")

ollama_success_rate = Gauge(
    "ollama_success_rate_percent", "Success rate of Ollama requests in percent"
)


# ============================================================================
# Helper Functions
# ============================================================================


def record_request(endpoint: str, model: str, duration_seconds: float, tokens: int, status: str):
    """
    Record métriques pour une requête Ollama.

    Args:
        endpoint: URL de l'endpoint utilisé
        model: Modèle Ollama (ex: llama3.2:1b)
        duration_seconds: Durée de la requête
        tokens: Nombre de tokens générés
        status: "success" ou "error"
    """
    # Compteur requêtes
    ollama_requests_total.labels(endpoint=endpoint, model=model, status=status).inc()

    # Histogramme latence
    ollama_request_duration_seconds.labels(endpoint=endpoint, model=model).observe(duration_seconds)

    # Histogramme tokens
    if tokens > 0:
        ollama_tokens_generated.labels(endpoint=endpoint, model=model).observe(tokens)


def record_failover():
    """Record qu'un failover a eu lieu."""
    ollama_failovers_total.inc()


def update_endpoint_health(endpoint: str, is_healthy: bool):
    """
    Update le status de santé d'un endpoint.

    Args:
        endpoint: URL de l'endpoint
        is_healthy: True si healthy, False si down
    """
    ollama_endpoint_health.labels(endpoint=endpoint).set(1 if is_healthy else 0)


def update_current_endpoint(endpoint: str):
    """
    Update l'endpoint actuellement actif.

    Args:
        endpoint: URL de l'endpoint actif
    """
    ollama_current_endpoint.info({"endpoint": endpoint})


def update_success_rate(rate_percent: float):
    """
    Update le taux de succès global.

    Args:
        rate_percent: Taux de succès en %
    """
    ollama_success_rate.set(rate_percent)
