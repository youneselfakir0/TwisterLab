# API Orchestrator - Documentation Complète

## Base URL

```
http://localhost:8000/api/v1/orchestrator
```

Production: `https://api.twisterlab.com/v1/orchestrator`

---

## Authentification

**Version actuelle**: Aucune authentification requise (dev/alpha)

**Version production**: Bearer token JWT
```http
Authorization: Bearer <your_jwt_token>
```

---

## Endpoints

### 1. Process Ticket (Traitement Complet)

Traite un ticket à travers le workflow complet: Classification → Routing → Résolution

**Endpoint**: `POST /process-ticket`

**Request**:
```json
{
  "ticket_id": "string (required)",
  "ticket_data": {
    "subject": "string (required)",
    "description": "string (required)",
    "requestor_email": "string (optional)",
    "priority": "string (optional: low|medium|high|urgent)",
    "category": "string (optional)"
  }
}
```

**Response 200** (Success):
```json
{
  "ticket_id": "TIX-001",
  "status": "auto_resolved",  // ou "escalated_to_human", "failed"
  "classification": {
    "category": "password",
    "priority": "high",
    "complexity": "simple",
    "confidence": 0.92
  },
  "resolution": {
    "status": "success",
    "sop_used": "Password Reset Procedure",
    "steps_executed": [
      {
        "step_number": 1,
        "description": "Verify user identity",
        "status": "success",
        "output": "User verified"
      }
    ],
    "total_steps": 3
  },
  "processing_time": 4.23,
  "created_at": "2025-10-28T10:30:00",
  "updated_at": "2025-10-28T10:30:04"
}
```

**Response 200** (Escalated):
```json
{
  "ticket_id": "TIX-002",
  "status": "escalated_to_human",
  "classification": {
    "category": "urgent",
    "priority": "urgent",
    "complexity": "complex",
    "confidence": 0.98
  },
  "resolution": {
    "status": "escalated",
    "reason": "urgent_priority",
    "recommended_agent": "senior_helpdesk",
    "estimated_response_time": "30 minutes"
  },
  "processing_time": 1.05,
  "created_at": "2025-10-28T10:35:00",
  "updated_at": "2025-10-28T10:35:01"
}
```

**Exemple cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/orchestrator/process-ticket \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TIX-123",
    "ticket_data": {
      "subject": "Password reset needed",
      "description": "User forgot password",
      "requestor_email": "john@company.com",
      "priority": "high"
    }
  }'
```

**Exemple Python**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/orchestrator/process-ticket",
    json={
        "ticket_id": "TIX-123",
        "ticket_data": {
            "subject": "Password reset needed",
            "description": "User forgot password",
            "requestor_email": "john@company.com"
        }
    }
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Processing time: {result['processing_time']}s")
```

---

### 2. Get Agent Status

Récupère le statut de tous les agents disponibles

**Endpoint**: `GET /agents/status`

**Query Parameters**:
- `include_health` (boolean, optional): Inclure les métriques de santé détaillées. Default: `false`

**Request**:
```http
GET /api/v1/orchestrator/agents/status?include_health=true
```

**Response 200**:
```json
{
  "status": "success",
  "agents": {
    "classifier": {
      "name": "Ticket Classifier",
      "status": "available",
      "load": 2,
      "max_load": 10,
      "last_health_check": "2025-10-28T10:45:00",
      "health_metrics": {
        "response_time": "150ms",
        "error_rate": "0.1%",
        "uptime": "99.9%"
      }
    },
    "resolver": {
      "name": "Helpdesk Resolver",
      "status": "available",
      "load": 1,
      "max_load": 5,
      "last_health_check": "2025-10-28T10:45:00",
      "health_metrics": {
        "response_time": "320ms",
        "error_rate": "0.2%",
        "uptime": "99.8%"
      }
    },
    "desktop_commander": {
      "name": "Desktop Commander",
      "status": "available",
      "load": 0,
      "max_load": 3,
      "last_health_check": "2025-10-28T10:45:00",
      "health_metrics": {
        "response_time": "450ms",
        "error_rate": "0.3%",
        "uptime": "99.5%"
      }
    }
  },
  "overall_health": "healthy"  // "healthy", "degraded", "critical"
}
```

**Exemple cURL**:
```bash
curl http://localhost:8000/api/v1/orchestrator/agents/status?include_health=true
```

**Exemple Python**:
```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/orchestrator/agents/status",
    params={"include_health": True}
)

status = response.json()
for agent_name, agent_info in status["agents"].items():
    print(f"{agent_name}: {agent_info['load']}/{agent_info['max_load']}")
```

---

### 3. Get Metrics

Récupère les métriques de performance de l'orchestrateur

**Endpoint**: `GET /metrics`

**Request**:
```http
GET /api/v1/orchestrator/metrics
```

**Response 200**:
```json
{
  "status": "success",
  "metrics": {
    "tickets_processed": 1247,
    "auto_resolved": 892,
    "escalated_to_human": 355,
    "average_resolution_time": 6.4,
    "agent_failures": 3
  },
  "timestamp": "2025-10-28T10:50:00"
}
```

**Métriques Calculées**:
- `auto_resolution_rate`: `(auto_resolved / tickets_processed) * 100` → **71.5%**
- `escalation_rate`: `(escalated_to_human / tickets_processed) * 100` → **28.5%**
- `failure_rate`: `(agent_failures / tickets_processed) * 100` → **0.24%**

**Exemple cURL**:
```bash
curl http://localhost:8000/api/v1/orchestrator/metrics
```

**Exemple Python**:
```python
import requests

response = requests.get("http://localhost:8000/api/v1/orchestrator/metrics")
metrics = response.json()["metrics"]

auto_rate = (metrics["auto_resolved"] / metrics["tickets_processed"]) * 100
print(f"Taux de résolution automatique: {auto_rate:.1f}%")
print(f"Temps moyen de résolution: {metrics['average_resolution_time']} minutes")
```

---

### 4. Rebalance Load

Rééquilibre la charge entre les agents

**Endpoint**: `POST /rebalance`

**Query Parameters**:
- `strategy` (string, required): Stratégie de load balancing
  - `round_robin` - Distribution uniforme
  - `least_loaded` - Vers agent le moins chargé
  - `priority_based` - Selon priorité du ticket

**Request**:
```http
POST /api/v1/orchestrator/rebalance?strategy=round_robin
```

**Response 200**:
```json
{
  "status": "success",
  "strategy": "round_robin",
  "action": "load_balanced",
  "agents_adjusted": 3,
  "timestamp": "2025-10-28T11:00:00"
}
```

**Response 400** (Invalid Strategy):
```json
{
  "detail": "Invalid strategy. Must be one of: round_robin, least_loaded, priority_based"
}
```

**Exemple cURL**:
```bash
# Round Robin
curl -X POST "http://localhost:8000/api/v1/orchestrator/rebalance?strategy=round_robin"

# Least Loaded
curl -X POST "http://localhost:8000/api/v1/orchestrator/rebalance?strategy=least_loaded"

# Priority Based
curl -X POST "http://localhost:8000/api/v1/orchestrator/rebalance?strategy=priority_based"
```

**Exemple Python**:
```python
import requests

strategies = ["round_robin", "least_loaded", "priority_based"]

for strategy in strategies:
    response = requests.post(
        "http://localhost:8000/api/v1/orchestrator/rebalance",
        params={"strategy": strategy}
    )
    result = response.json()
    print(f"{strategy}: {result['agents_adjusted']} agents adjusted")
```

---

### 5. Get Results (Single Ticket)

Récupère les résultats de traitement pour un ticket spécifique

**Endpoint**: `GET /results/{ticket_id}`

**Request**:
```http
GET /api/v1/orchestrator/results/TIX-123
```

**Response 200**:
```json
{
  "ticket_id": "TIX-123",
  "status": "auto_resolved",
  "classification": { ... },
  "resolution": { ... },
  "processing_time": 4.23,
  "created_at": "2025-10-28T10:30:00",
  "updated_at": "2025-10-28T10:30:04"
}
```

**Response 404**:
```json
{
  "detail": "No orchestrator results found for this ticket"
}
```

**Exemple cURL**:
```bash
curl http://localhost:8000/api/v1/orchestrator/results/TIX-123
```

---

### 6. List All Results

Liste tous les résultats de traitement de tickets

**Endpoint**: `GET /results`

**Request**:
```http
GET /api/v1/orchestrator/results
```

**Response 200**:
```json
{
  "total_results": 1247,
  "results": [
    {
      "ticket_id": "TIX-123",
      "status": "auto_resolved",
      "created_at": "2025-10-28T10:30:00"
    },
    {
      "ticket_id": "TIX-124",
      "status": "escalated_to_human",
      "created_at": "2025-10-28T10:35:00"
    }
  ]
}
```

**Exemple cURL**:
```bash
curl http://localhost:8000/api/v1/orchestrator/results
```

---

## Codes d'Erreur HTTP

| Code | Signification | Description |
|------|--------------|-------------|
| 200 | OK | Requête réussie |
| 400 | Bad Request | Paramètres invalides |
| 404 | Not Found | Ressource non trouvée |
| 500 | Internal Server Error | Erreur serveur |
| 503 | Service Unavailable | Service temporairement indisponible |

---

## Exemples d'Intégration

### Intégration JavaScript/Node.js

```javascript
const axios = require('axios');

const orchestrator = {
  baseURL: 'http://localhost:8000/api/v1/orchestrator',

  async processTicket(ticketId, ticketData) {
    const response = await axios.post(`${this.baseURL}/process-ticket`, {
      ticket_id: ticketId,
      ticket_data: ticketData
    });
    return response.data;
  },

  async getMetrics() {
    const response = await axios.get(`${this.baseURL}/metrics`);
    return response.data.metrics;
  },

  async getAgentStatus(includeHealth = true) {
    const response = await axios.get(`${this.baseURL}/agents/status`, {
      params: { include_health: includeHealth }
    });
    return response.data;
  }
};

// Utilisation
(async () => {
  const result = await orchestrator.processTicket('TIX-456', {
    subject: 'Cannot access email',
    description: 'Getting authentication errors',
    requestor_email: 'jane@company.com'
  });

  console.log(`Ticket ${result.ticket_id} ${result.status}`);
})();
```

---

### Intégration Python/FastAPI

```python
import httpx
from typing import Dict, Any

class TwisterLabClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def process_ticket(
        self,
        ticket_id: str,
        subject: str,
        description: str,
        requestor_email: str = None
    ) -> Dict[str, Any]:
        response = await self.client.post(
            f"{self.base_url}/api/v1/orchestrator/process-ticket",
            json={
                "ticket_id": ticket_id,
                "ticket_data": {
                    "subject": subject,
                    "description": description,
                    "requestor_email": requestor_email
                }
            }
        )
        return response.json()

    async def get_metrics(self) -> Dict[str, Any]:
        response = await self.client.get(
            f"{self.base_url}/api/v1/orchestrator/metrics"
        )
        return response.json()["metrics"]

# Utilisation
import asyncio

async def main():
    client = TwisterLabClient()

    result = await client.process_ticket(
        ticket_id="TIX-789",
        subject="Install Zoom",
        description="Need Zoom for remote meetings"
    )

    print(f"Status: {result['status']}")
    print(f"Processing time: {result['processing_time']}s")

asyncio.run(main())
```

---

### Intégration PowerShell

```powershell
# TwisterLab API Client
$baseURL = "http://localhost:8000/api/v1/orchestrator"

function Invoke-ProcessTicket {
    param(
        [string]$TicketId,
        [string]$Subject,
        [string]$Description,
        [string]$RequestorEmail
    )

    $body = @{
        ticket_id = $TicketId
        ticket_data = @{
            subject = $Subject
            description = $Description
            requestor_email = $RequestorEmail
        }
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Method Post -Uri "$baseURL/process-ticket" `
        -ContentType "application/json" -Body $body

    return $response
}

function Get-OrchestratorMetrics {
    $response = Invoke-RestMethod -Method Get -Uri "$baseURL/metrics"
    return $response.metrics
}

# Utilisation
$result = Invoke-ProcessTicket -TicketId "TIX-001" `
    -Subject "Password reset" `
    -Description "Forgot password" `
    -RequestorEmail "user@company.com"

Write-Host "Status: $($result.status)"
Write-Host "Processing time: $($result.processing_time)s"
```

---

## Rate Limiting (Future)

**Version production**:
- 100 requêtes/minute par IP
- 1000 requêtes/heure par API key
- Header de réponse: `X-RateLimit-Remaining: 95`

---

## Webhooks (Future)

Recevoir des notifications lors d'événements:

```json
{
  "event": "ticket.escalated",
  "ticket_id": "TIX-123",
  "timestamp": "2025-10-28T11:30:00",
  "data": {
    "reason": "urgent_priority",
    "assigned_to": "senior_helpdesk"
  }
}
```

**Events disponibles**:
- `ticket.classified`
- `ticket.auto_resolved`
- `ticket.escalated`
- `agent.failure`

---

## Support & Contact

- **Documentation**: https://docs.twisterlab.com
- **Support**: support@twisterlab.com
- **GitHub**: https://github.com/twisterlab/api
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

**Version API**: 1.0.0-alpha.1
**Dernière mise à jour**: 2025-10-28
