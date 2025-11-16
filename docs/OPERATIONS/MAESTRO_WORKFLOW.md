# Maestro Orchestrator - Workflow Documentation

## Vue d'Ensemble

Le **Maestro Orchestrator** est le cerveau central de TwisterLab. Il orchestre intelligemment le routage des tickets IT helpdesk vers les agents appropriés basé sur une classification multi-critères.

### Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      INCOMING TICKET                             │
│  (ticket_id, subject, description, requestor, priority)          │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                   MAESTRO ORCHESTRATOR                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  STEP 1: CLASSIFICATION                                    │ │
│  │  Agent: TicketClassifierAgent                              │ │
│  │  ─────────────────────────────────────────────────────────  │ │
│  │  Input: subject + description                              │ │
│  │  Output:                                                    │ │
│  │    - category  (password, software, access, etc.)          │ │
│  │    - priority  (low, medium, high, urgent)                 │ │
│  │    - complexity (simple, moderate, complex)                │ │
│  │    - confidence (0.0-1.0)                                  │ │
│  └────────────────┬───────────────────────────────────────────┘ │
│                   │                                             │
│                   ▼                                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  STEP 2: ROUTING DECISION                                  │ │
│  │  Based on priority + complexity + confidence               │ │
│  └────────┬────────────┬──────────────┬─────────────────────┘  │
│           │            │              │                         │
│     ┌─────▼─────┐ ┌────▼────┐  ┌─────▼──────┐                │
│     │  URGENT   │ │ SIMPLE  │  │  COMPLEX   │                │
│     │ priority  │ │conf>0.8 │  │ OR conf<0.6│                │
│     └─────┬─────┘ └────┬────┘  └─────┬──────┘                │
│           │            │              │                         │
│           ▼            ▼              ▼                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  STEP 3: ROUTE TO AGENT                                  │  │
│  └──────┬────────────┬──────────────┬───────────────────────┘  │
│         │            │              │                          │
└─────────┼────────────┼──────────────┼──────────────────────────┘
          │            │              │
          ▼            ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │  HUMAN   │  │   AUTO   │  │  HUMAN   │
    │  AGENT   │  │ RESOLVER │  │  REVIEW  │
    │          │  │          │  │          │
    │ Escalate │  │ Execute  │  │ Escalate │
    │Immediate │  │   SOP    │  │ Complex  │
    └──────────┘  └──────────┘  └──────────┘
```

---

## Règles de Routage

Le Maestro applique les règles suivantes pour router les tickets:

| Priority | Complexity | Confidence | Decision                         | Agent              | Temps Estimé |
|----------|-----------|-----------|----------------------------------|--------------------|--------------|
| URGENT   | *         | *         | Escalade immédiate              | senior_helpdesk    | 30 min       |
| *        | SIMPLE    | > 0.8     | Résolution automatique          | HelpdeskResolver   | 5 min        |
| *        | MODERATE  | > 0.6     | Résolution auto (supervisée)    | HelpdeskResolver   | 10 min       |
| *        | COMPLEX   | *         | Révision humaine                | senior_helpdesk    | 2 heures     |
| *        | *         | < 0.6     | Révision humaine                | senior_helpdesk    | 1 heure      |

### Logique de Décision

```python
if priority == URGENT:
    → route_to_human("urgent_priority")

elif complexity == SIMPLE and confidence > 0.8:
    → route_to_auto_resolver()

elif complexity == MODERATE and confidence > 0.6:
    → route_to_auto_resolver(supervised=True)

elif complexity == COMPLEX or confidence < 0.6:
    → route_to_human("complex_or_low_confidence")
```

---

## Catégories de Tickets

### 1. Password (Mot de passe)
**Mots-clés**: password, mot de passe, mdp, login, connexion, authentification

**Caractéristiques**:
- Priorité: `high`
- Complexité: `simple`
- Confidence typique: `0.9`
- Résolution: Généralement auto-résolue

**Exemple**:
```json
{
  "ticket_id": "PASS-001",
  "subject": "Password reset needed",
  "description": "I forgot my Active Directory password"
}
→ Classification: password / high / simple / 0.9
→ Decision: AUTO-RESOLVE
→ SOP: Password Reset Procedure
```

---

### 2. Software (Logiciel)
**Mots-clés**: software, logiciel, install, installer, office, application, app

**Caractéristiques**:
- Priorité: `medium`
- Complexité: `moderate`
- Confidence typique: `0.8`
- Résolution: Auto-résolue si standard, sinon escalade

**Exemple**:
```json
{
  "ticket_id": "SOFT-001",
  "subject": "Install Microsoft Office",
  "description": "Need Office 365 on new laptop"
}
→ Classification: software / medium / moderate / 0.8
→ Decision: AUTO-RESOLVE (supervised)
→ SOP: Software Installation via Desktop Commander
```

---

### 3. Access (Accès)
**Mots-clés**: access, accès, permission, droits, autorisation, partage

**Caractéristiques**:
- Priorité: `high`
- Complexité: `moderate`
- Confidence typique: `0.7`
- Résolution: Auto-résolue si permissions simples

**Exemple**:
```json
{
  "ticket_id": "ACCESS-001",
  "subject": "Access to shared folder",
  "description": "Need read access to Finance folder"
}
→ Classification: access / high / moderate / 0.7
→ Decision: AUTO-RESOLVE (supervised)
→ SOP: Grant Folder Access
```

---

### 4. Urgent
**Mots-clés**: urgent, urgence, critical, critique, down, panne

**Caractéristiques**:
- Priorité: `urgent`
- Complexité: `complex`
- Confidence typique: `0.95`
- Résolution: TOUJOURS escaladé à un humain

**Exemple**:
```json
{
  "ticket_id": "URGENT-001",
  "subject": "URGENT: Production server down",
  "description": "Main application server is completely offline"
}
→ Classification: urgent / urgent / complex / 0.95
→ Decision: ESCALATE TO HUMAN (immediate)
→ Agent: senior_helpdesk
→ Response Time: 30 minutes
```

---

## Flux de Travail Détaillé

### Phase 1: Classification

```python
async def _classify_ticket(ticket_id, subject, description):
    # Utilise TicketClassifierAgent
    classifier = TicketClassifierAgent()
    result = await classifier.execute(
        task=f"Classify ticket {ticket_id}",
        context={"ticket": {"subject": subject, "description": description}}
    )

    return {
        "category": "password",      # password, software, access, etc.
        "priority": "high",           # low, medium, high, urgent
        "complexity": "simple",       # simple, moderate, complex
        "confidence": 0.9             # 0.0 - 1.0
    }
```

### Phase 2: Décision de Routage

```python
async def route_ticket(context):
    # Classification
    classification = await _classify_ticket(...)

    # Extraction des critères
    priority = TicketPriority(classification["priority"])
    complexity = TicketComplexity(classification["complexity"])
    confidence = classification["confidence"]

    # Règles de routage
    if priority == TicketPriority.URGENT:
        return await _escalate_to_human(ticket_id, "urgent_priority")

    elif complexity == TicketComplexity.SIMPLE and confidence > 0.8:
        return await _route_to_auto_resolver(ticket_id, classification)

    elif complexity == TicketComplexity.COMPLEX or confidence < 0.6:
        return await _escalate_to_human(ticket_id, "complex_or_low_confidence")
```

### Phase 3: Résolution

#### A) Auto-Résolution

```python
async def _route_to_auto_resolver(ticket_id, classification):
    # Vérifier disponibilité
    if not _is_agent_available("resolver"):
        return await _escalate_to_human(ticket_id, "resolver_unavailable")

    # Créer l'agent resolver
    resolver = HelpdeskResolverAgent()

    # Exécuter la résolution
    result = await resolver.execute(
        task=f"Resolve ticket {ticket_id}",
        context={
            "ticket": ticket_data,
            "classification": classification
        }
    )

    if result["status"] == "success":
        metrics["auto_resolved"] += 1
        return {"status": "auto_resolved", "resolution": result}
    else:
        return await _escalate_to_human(ticket_id, "auto_resolution_failed")
```

#### B) Escalade Humaine

```python
async def _escalate_to_human(ticket_id, reason, classification):
    metrics["escalated_to_human"] += 1

    return {
        "status": "escalated_to_human",
        "ticket_id": ticket_id,
        "reason": reason,
        "classification": classification,
        "recommended_agent": "senior_helpdesk",
        "estimated_response_time": "30 minutes",
        "priority": classification.get("priority", "medium")
    }
```

---

## Métriques de Performance

Le Maestro suit les métriques suivantes en temps réel:

### Métriques Principales

| Métrique | Description | Cible |
|----------|-------------|-------|
| `tickets_processed` | Total tickets traités | - |
| `auto_resolved` | Tickets résolus automatiquement | > 60% |
| `escalated_to_human` | Tickets escaladés | < 40% |
| `average_resolution_time` | Temps moyen de résolution | < 10 min |
| `agent_failures` | Échecs d'agents | < 1% |

### Métriques de Santé des Agents

```json
{
  "classifier": {
    "status": "available",
    "load": "2/10",
    "health_metrics": {
      "response_time": "150ms",
      "error_rate": "0.1%",
      "uptime": "99.9%"
    }
  },
  "resolver": {
    "status": "available",
    "load": "1/5",
    "health_metrics": {
      "response_time": "320ms",
      "error_rate": "0.2%",
      "uptime": "99.8%"
    }
  }
}
```

---

## Exemples Pratiques

### Exemple Complet 1: Password Reset

**Ticket Entrant**:
```json
{
  "ticket_id": "TIX-2024-001",
  "subject": "Cannot log in to workstation",
  "description": "Forgot my password after vacation. Need immediate reset.",
  "requestor": "john.doe@company.com",
  "priority": "high"
}
```

**Étape 1 - Classification**:
```json
{
  "category": "password",
  "priority": "high",
  "complexity": "simple",
  "confidence": 0.92,
  "routing_recommendation": "route_to_auto_resolution"
}
```

**Étape 2 - Décision**:
- Priority: HIGH (mais pas URGENT)
- Complexity: SIMPLE
- Confidence: 0.92 > 0.8
- **Decision**: AUTO-RESOLVE

**Étape 3 - Résolution**:
```json
{
  "status": "auto_resolved",
  "sop_used": "Password Reset Procedure",
  "steps_executed": [
    {"step": 1, "action": "Verify user identity", "status": "success"},
    {"step": 2, "action": "Reset password in AD", "status": "success"},
    {"step": 3, "action": "Send temp password via email", "status": "success"}
  ],
  "resolution_time": "4.2 minutes",
  "sla_met": true
}
```

---

### Exemple Complet 2: Server Outage (Escalade)

**Ticket Entrant**:
```json
{
  "ticket_id": "TIX-2024-099",
  "subject": "URGENT: Email server completely down",
  "description": "All users cannot access email. Business critical.",
  "requestor": "admin@company.com",
  "priority": "urgent"
}
```

**Étape 1 - Classification**:
```json
{
  "category": "urgent",
  "priority": "urgent",
  "complexity": "complex",
  "confidence": 0.98
}
```

**Étape 2 - Décision**:
- Priority: URGENT
- **Decision**: ESCALATE TO HUMAN (immediate)

**Étape 3 - Escalade**:
```json
{
  "status": "escalated_to_human",
  "reason": "urgent_priority",
  "recommended_agent": "senior_helpdesk",
  "escalation_time": "immediate",
  "estimated_response": "15-30 minutes",
  "notification_sent": ["sms", "email", "teams"],
  "on_call_engineer": "Sarah Chen"
}
```

---

## Load Balancing & Failover

### Stratégies de Load Balancing

#### 1. Round Robin
- Distribue les tickets uniformément entre agents disponibles
- Bon pour charge uniforme

#### 2. Least Loaded
- Route vers l'agent avec la charge la plus faible
- Optimal pour charge variable

#### 3. Priority Based
- Agents spécialisés selon catégorie de ticket
- Maximum d'efficacité

### Gestion des Échecs

```python
# Si agent principal échoue
if agent_result["status"] == "error":
    # Tenter failover
    backup_agent = get_backup_agent(agent_type)
    if backup_agent:
        result = await backup_agent.execute(task)
    else:
        # Escalade si aucun backup
        result = await _escalate_to_human(ticket_id, "agent_failure")
```

---

## API Endpoints

Voir [API_ORCHESTRATOR.md](./API_ORCHESTRATOR.md) pour la documentation complète des endpoints REST.

**Endpoints principaux**:
- `POST /api/v1/orchestrator/process-ticket` - Traiter un ticket
- `GET /api/v1/orchestrator/agents/status` - Statut des agents
- `GET /api/v1/orchestrator/metrics` - Métriques de performance
- `POST /api/v1/orchestrator/rebalance` - Rééquilibrer la charge

---

## Guide de Dépannage

### Problème: Tous les tickets sont escaladés

**Cause**: Confidence scores trop bas

**Solution**:
1. Vérifier que les SOPs sont bien chargés en base
2. Améliorer les mots-clés de classification
3. Entraîner le modèle de classification

### Problème: Agents marqués comme unavailable

**Cause**: Charge maximale atteinte

**Solution**:
```bash
curl -X POST "http://localhost:8000/api/v1/orchestrator/rebalance?strategy=least_loaded"
```

### Problème: Temps de résolution trop élevé

**Cause**: Agents surchargés ou SOPs inefficaces

**Solution**:
1. Augmenter `max_load` des agents
2. Optimiser les SOPs
3. Ajouter plus d'instances d'agents

---

## Prochaines Améliorations

- [ ] Machine Learning pour classification dynamique
- [ ] Intégration avec système de tickets externe (Jira, ServiceNow)
- [ ] Dashboard temps réel des métriques
- [ ] Auto-scaling des agents
- [ ] Apprentissage à partir des résolutions passées

---

**Version**: 1.0.0
**Dernière mise à jour**: 2025-10-28
**Auteur**: TwisterLab Team
