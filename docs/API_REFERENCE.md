# TwisterLab - Documentation API REST

## Vue d'Ensemble

L'API TwisterLab fournit une interface REST complète pour l'automatisation des helpdesks IT utilisant des agents IA.

**Base URL**: `http://localhost:8000`
**Version**: 1.0.0-alpha.1
**Format**: JSON
**Authentification**: Aucune (pour la phase alpha)

## Endpoints Disponibles

### Système

#### GET `/health`

Vérifie l'état de santé de l'API.

**Réponse**:

```json
{
  "status": "healthy",
  "version": "1.0.0-alpha.1"
}
```

#### GET `/`

Informations générales sur l'API.

**Réponse**:

```json
{
  "name": "TwisterLab API",
  "description": "AI-powered IT Helpdesk automation platform",
  "version": "1.0.0-alpha.1",
  "docs": "/docs",
  "health": "/health"
}
```

### Tickets

#### POST `/api/v1/tickets/`

Crée un nouveau ticket.

**Corps de la requête**:

```json
{
  "subject": "string (1-200 chars)",
  "description": "string (1-2000 chars)",
  "priority": "low|medium|high|urgent (default: medium)",
  "category": "string (default: general)",
  "requestor_email": "string (required)"
}
```

**Réponse** (201 Created):

```json
{
  "id": "uuid",
  "subject": "string",
  "description": "string",
  "priority": "string",
  "category": "string",
  "status": "new",
  "requestor_email": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### GET `/api/v1/tickets/`

Liste tous les tickets avec pagination.

**Paramètres de requête**:

- `skip`: integer (default: 0)
- `limit`: integer (default: 100, max: 1000)
- `status`: string (filtre par statut)
- `priority`: string (filtre par priorité)

**Réponse**:

```json
{
  "tickets": [...],
  "total": 42,
  "skip": 0,
  "limit": 100
}
```

#### GET `/api/v1/tickets/{ticket_id}`

Récupère les détails d'un ticket spécifique.

**Paramètres**:

- `ticket_id`: UUID du ticket

**Réponse** (200 OK):

```json
{
  "id": "uuid",
  "subject": "string",
  "description": "string",
  "priority": "string",
  "category": "string",
  "status": "string",
  "requestor_email": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "assigned_agent": "string|null",
  "resolution": "string|null"
}
```

#### PUT `/api/v1/tickets/{ticket_id}`

Met à jour un ticket existant.

**Corps de la requête** (tous les champs optionnels):

```json
{
  "subject": "string",
  "description": "string",
  "priority": "string",
  "category": "string",
  "status": "string"
}
```

### Agents

#### GET `/api/v1/agents/`

Liste tous les agents disponibles.

**Réponse**:

```json
{
  "agents": [
    {
      "name": "classifier",
      "display_name": "Ticket Classifier",
      "status": "available",
      "load": 0,
      "response_time_ms": 150,
      "error_rate": 0.001,
      "uptime_percent": 99.9
    }
  ]
}
```

#### GET `/api/v1/agents/{agent_name}`

Détails d'un agent spécifique.

#### POST `/api/v1/agents/{agent_name}/execute`

Exécute un agent avec des paramètres spécifiques.

### Orchestrateur

#### POST `/api/v1/orchestrator/process-ticket`

Traite un ticket complet via l'orchestrateur Maestro.

**Corps de la requête**:

```json
{
  "ticket_id": "uuid",
  "ticket_data": {
    "subject": "string",
    "description": "string",
    "requestor_email": "string"
  }
}
```

**Réponse**:

```json
{
  "ticket_id": "uuid",
  "status": "completed|processing|failed",
  "classification": {...},
  "resolution": {...},
  "processing_time_ms": 1250
}
```

#### GET `/api/v1/orchestrator/results/{ticket_id}`

Récupère les résultats de traitement pour un ticket.

#### GET `/api/v1/orchestrator/agents/status`

Statut de tous les agents de l'orchestrateur.

#### POST `/api/v1/orchestrator/rebalance`

Rééquilibre la charge entre les agents.

### SOPs (Standard Operating Procedures)

#### GET `/api/v1/sops/`

Liste toutes les procédures opérationnelles standard.

#### POST `/api/v1/sops/`

Crée une nouvelle SOP.

#### GET `/api/v1/sops/{sop_id}`

Détails d'une SOP spécifique.

## Codes d'Erreur

### 400 Bad Request

Requête malformée ou données invalides.

```json
{
  "detail": [
    {
      "loc": ["body", "subject"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 404 Not Found

Ressource non trouvée.

```json
{
  "detail": "Ticket not found"
}
```

### 422 Unprocessable Entity

Données valides mais ne respectant pas les règles métier.

### 500 Internal Server Error

Erreur interne du serveur.

## Exemples d'Utilisation

### Créer un Ticket

```bash
curl -X POST "http://localhost:8000/api/v1/tickets/" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Ordinateur ne démarre pas",
    "description": "Mon ordinateur portable ne veut pas s'allumer ce matin",
    "requestor_email": "user@company.com"
  }'
```

### Traiter un Ticket Automatiquement

```bash
curl -X POST "http://localhost:8000/api/v1/orchestrator/process-ticket" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "550e8400-e29b-41d4-a716-446655440000",
    "ticket_data": {
      "subject": "Mot de passe oublié",
      "description": "Je ne me souviens plus de mon mot de passe Windows",
      "requestor_email": "user@company.com"
    }
  }'
```

## Limites et Quotas

- **Rate Limiting**: Non implémenté (phase alpha)
- **Pagination**: Maximum 1000 éléments par page
- **Timeout**: 30 secondes par défaut
- **Payload**: Maximum 1MB par requête

## Versionnage

L'API suit le versionnage sémantique :

- `/api/v1/` : Version stable actuelle
- `/api/v2/` : Version future (non implémentée)

## Documentation Interactive

La documentation complète Swagger/OpenAPI est disponible sur :

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`
