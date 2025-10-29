# TwisterLab - Guide d'Architecture

## Vue d'Ensemble

TwisterLab est une plateforme d'automatisation des helpdesks IT utilisant des agents IA spécialisés et le protocole MCP (Model Context Protocol). L'architecture suit les principes de conception modulaire, asynchrone et orientée événements.

## Architecture Générale

```text
┌─────────────────────────────────────────────────────────────┐
│                    TwisterLab Platform                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │   Agents    │ │  API REST  │ │   Orchestrateur     │   │
│  │             │ │             │ │   (Maestro)        │   │
│  │ • Classifier│ │ • FastAPI  │ │                     │   │
│  │ • Resolver  │ │ • Pydantic │ │ • Coordination      │   │
│  │ • Desktop   │ │ • Async    │ │ • Load Balancing    │   │
│  │   Commander │ │             │ │ • Error Handling   │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │ PostgreSQL  │ │    Redis   │ │      Ollama        │   │
│  │             │ │             │ │                    │   │
│  │ • Tickets   │ │ • Cache    │ │ • Local AI Models  │   │
│  │ • SOPs      │ │ • Sessions │ │ • DeepSeek-R1      │   │
│  │ • History   │ │             │ │                    │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Composants Principaux

### 1. Agents IA

#### TwisterAgent (Classe de Base)

```python
class TwisterAgent:
    name: str                    # Identifiant kebab-case
    display_name: str           # Nom d'affichage
    tools: List[Tool]           # Outils MCP
    model: str                  # Modèle IA utilisé
    temperature: float          # Créativité (0.0-1.0)

    async def execute(self, task: dict) -> dict:
        # Logique d'exécution asynchrone
        pass
```

#### Agents Spécialisés

##### Classifier Agent

- **Rôle**: Classification automatique des tickets
- **Entrée**: Texte du ticket (sujet + description)
- **Sortie**: Catégorie, priorité, urgence
- **Modèle**: deepseek-r1 (température 0.2)

##### Helpdesk Resolver Agent

- **Rôle**: Résolution automatisée des problèmes courants
- **Entrée**: Ticket classifié + contexte
- **Sortie**: Solution proposée ou escalade
- **Outils**: Base de connaissances SOPs

##### Desktop Commander Agent

- **Rôle**: Exécution de commandes système à distance
- **Protocole**: MCP (Model Context Protocol)
- **Sécurité**: Authentification requise, audit complet
- **Limites**: Actions approuvées uniquement

### 2. API REST (FastAPI)

#### Structure des Routes

```text
agents/api/
├── main.py              # Application FastAPI principale
├── routes_tickets.py    # Gestion des tickets
├── routes_agents.py     # Gestion des agents
├── routes_sops.py       # Gestion des SOPs
└── routes_*.py          # Routes spécialisées
```

#### Fonctionnalités Clés

- **Async/Await**: Toutes les opérations I/O
- **Validation**: Pydantic pour tous les modèles
- **Documentation**: Swagger/OpenAPI automatique
- **Middleware**: Logging, CORS, rate limiting
- **Gestion d'Erreurs**: Exceptions structurées

### 3. Orchestrateur Maestro

#### Architecture

```python
class MaestroOrchestrator:
    agents: Dict[str, TwisterAgent]
    queue: AsyncQueue
    metrics: MetricsCollector

    async def process_ticket(self, ticket: Ticket) -> ProcessingResult:
        # 1. Classification
        # 2. Routage vers agent approprié
        # 3. Exécution et monitoring
        # 4. Résultat final
        pass
```

#### Algorithme de Routage

1. **Réception**: Ticket entrant via API
2. **Classification**: Agent Classifier détermine la catégorie
3. **Sélection**: Routage vers agent spécialisé
4. **Exécution**: Traitement asynchrone avec timeout
5. **Validation**: Vérification des résultats
6. **Retour**: Réponse structurée à l'utilisateur

### 4. Base de Données

#### Modèle de Données

```sql
-- Tickets
CREATE TABLE tickets (
    id UUID PRIMARY KEY,
    subject VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    category VARCHAR(50) DEFAULT 'general',
    status VARCHAR(20) DEFAULT 'new',
    requestor_email VARCHAR(255) NOT NULL,
    assigned_agent VARCHAR(50),
    resolution TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- SOPs (Standard Operating Procedures)
CREATE TABLE sops (
    id UUID PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    applicable_issues TEXT[],  -- Array de problèmes couverts
    steps JSONB NOT NULL,      -- Étapes détaillées
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Migrations

- **Alembic**: Gestion des migrations SQLAlchemy
- **Versionnée**: Historique complet des changements
- **Environnement**: Séparation dev/prod/test

### 5. Cache et État (Redis)

#### Utilisations

- **Session Management**: États des agents actifs
- **Cache de Résultats**: Réponses IA fréquentes
- **File d'Attente**: Traitement asynchrone des tickets
- **Métriques**: Collecte de statistiques temps réel

#### Structure des Clés

```text
twisterlab:
├── agents:{agent_name}:status    # État de l'agent
├── tickets:{id}:processing       # État du traitement
├── cache:ai:{hash}:response      # Cache des réponses IA
└── metrics:{timestamp}:data      # Métriques collectées
```

## Flux de Données

### Création d'un Ticket

```text
1. API REST → Validation Pydantic
2. Base de données → Insertion ticket
3. Orchestrateur → File d'attente Redis
4. Classification → Agent IA
5. Résolution → Agent spécialisé
6. Mise à jour → Base de données
7. Notification → Client API
```

### Traitement Automatique

```text
Ticket Entrant
      ↓
[Classifier Agent]
      ↓
Catégorie + Priorité
      ↓
[Resolver Agent]
      ↓
Solution proposée
      ↓
[Desktop Commander]
      ↓
Exécution distante
      ↓
Résultat final
```

## Sécurité et Conformité

### Authentification

- **Phase Alpha**: Aucune authentification
- **Phase Beta**: JWT tokens
- **Production**: OAuth2 + RBAC

### Autorisation

- **RBAC**: Role-Based Access Control
- **Agent Scoping**: Isolation des actions par agent
- **Audit Logging**: Traçabilité complète des actions

### Chiffrement

- **Données**: AES-256 en transit et au repos
- **Clés**: Gestion via Azure Key Vault (futur)
- **Secrets**: Variables d'environnement uniquement

## Performance et Scalabilité

### Métriques Clés

- **Latence**: < 2s pour classification, < 30s pour résolution
- **Débit**: 100 tickets/heure par agent
- **Disponibilité**: 99.9% SLA cible
- **Précision**: > 85% pour classification automatique

### Optimisations

- **Async Processing**: Toutes les opérations I/O
- **Connection Pooling**: PostgreSQL et Redis
- **Caching**: Résultats IA et métadonnées
- **Load Balancing**: Distribution automatique des agents

### Monitoring

- **Health Checks**: Endpoints dédiés
- **Métriques**: Prometheus/Grafana (futur)
- **Logging**: Structured logging avec context
- **Alerting**: Seuils configurables

## Déploiement

### Environnements

```text
Development: Docker Compose local
Staging: Azure Container Apps
Production: AKS + Azure Database
```

### Configuration

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://...
      - OLLAMA_URL=http://ollama:11434
    depends_on:
      - postgres
      - redis
      - ollama
```

### CI/CD Pipeline

1. **Tests**: pytest avec couverture
2. **Build**: Docker image
3. **Security Scan**: Snyk/Trivy
4. **Deploy**: Azure DevOps/GitHub Actions

## Évolutivité

### Phase 2 (Courant)

- ✅ API REST complète
- ✅ 3 agents de base
- ✅ Orchestrateur Maestro
- 🔄 Intégration MCP Desktop Commander
- 🔄 Tests d'intégration complets

### Phase 3 (Futur)

- 🤔 Interface utilisateur web
- 🤔 Authentification avancée
- 🤔 Métriques temps réel
- 🤔 Intégration Azure
- 🤔 Multi-tenancy

### Extensions Possibles

- **Nouveaux Agents**: Support client, inventaire IT
- **Intégrations**: ServiceNow, Jira, Teams
- **IA Avancée**: Fine-tuning, RAG, multi-modèle
- **Edge Computing**: Traitement décentralisé

## Recommandations

### Développement

- **Tests First**: TDD pour toutes les fonctionnalités
- **Code Reviews**: Pull requests obligatoires
- **Documentation**: Mise à jour automatique des docs

### Production

- **Monitoring**: Observabilité complète
- **Backups**: Stratégie RTO/RPO définie
- **Disaster Recovery**: Plan de continuité
- **Security**: Audits réguliers

### Maintenance

- **Dependencies**: Mises à jour régulières
- **Performance**: Monitoring continu
- **Logs**: Rotation et archivage
- **Metrics**: Alertes proactives
