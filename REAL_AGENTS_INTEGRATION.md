# 🚀 TwisterLab Real Agents - Integration Complete

## Vue d'Ensemble

Ce document décrit l'intégration complète des **7 agents réels** dans l'infrastructure TwisterLab, incluant le déploiement, la planification automatique, le monitoring et les tests d'intégration.

---

## 📋 Agents Déployés

### 1. **RealMonitoringAgent**
- **Opérations**: `health_check`, `full_diagnostic`, `check_services`, `check_ports`, `check_gpu`
- **Planification**: Toutes les minutes (health_check), toutes les 5 minutes (diagnostic)
- **Métriques**: CPU, RAM, Disk, Network, Processes, Docker services, GPU

### 2. **RealBackupAgent**
- **Opérations**: `create_backup`, `list_backups`, `verify_backup`, `cleanup_old`
- **Planification**: Toutes les 6 heures
- **Composants**: PostgreSQL dump, Redis snapshot, Docker configs

### 3. **RealSyncAgent**
- **Opérations**: `sync_all`, `verify_consistency`, `clear_stale_cache`, `warm_cache`
- **Planification**: Vérification toutes les 15 minutes, nettoyage toutes les heures
- **Cibles**: Redis ↔ PostgreSQL synchronization

### 4. **RealClassifierAgent**
- **Opérations**: `classify_ticket`, `analyze_logs`, `detect_patterns`
- **Catégories**: network, software, hardware, security, performance, database
- **Planification**: Sur demande (via API ou workflow)

### 5. **RealResolverAgent**
- **Opérations**: `resolve_ticket`, `list_sops`, `execute_sop`
- **SOPs**: 5 procédures (network, software, disk, password, database)
- **Planification**: Sur demande (tickets classifiés)

### 6. **RealDesktopCommanderAgent**
- **Opérations**: `execute_command`, `check_service`, `get_system_info`, `network_diagnostic`
- **Commandes**: 9 commandes whitelistées (ping, ipconfig, systeminfo, etc.)
- **Planification**: Sur demande (résolution de tickets)

### 7. **RealMaestroAgent**
- **Opérations**: `orchestrate_workflow`, `coordinate_agents`, `health_check_all`, `load_balance`
- **Planification**: Health check toutes les 3 minutes
- **Rôle**: Orchestration de workflows multi-agents

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     API (FastAPI)                           │
│                   http://edgeserver:8000                    │
├─────────────────────────────────────────────────────────────┤
│            AutonomousAgentOrchestrator                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              AgentScheduler                          │  │
│  │  - Periodic execution (cron-like)                    │  │
│  │  - Task history tracking                             │  │
│  │  - Automatic retry on failure                        │  │
│  └──────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  7 Real Agents:                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │Monitoring│ │  Backup  │ │   Sync   │ │Classifier│      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                   │
│  │ Resolver │ │Commander │ │ Maestro  │                   │
│  └──────────┘ └──────────┘ └──────────┘                   │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure:                                            │
│  - PostgreSQL (twisterlab DB)                               │
│  - Redis (cache + state)                                    │
│  - Docker Swarm (orchestration)                             │
│  - Prometheus (metrics collection)                          │
│  - Grafana (visualization)                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📅 Scheduler Configuration

Le scheduler automatique exécute les agents selon cette planification:

| Agent | Opération | Intervalle | Utilité |
|-------|-----------|------------|---------|
| MonitoringAgent | `health_check` | 1 minute | Surveillance système en temps réel |
| MonitoringAgent | `full_diagnostic` | 5 minutes | Rapport complet du système |
| BackupAgent | `create_backup` | 6 heures | Sauvegarde automatique |
| SyncAgent | `verify_consistency` | 15 minutes | Vérification cache/DB |
| SyncAgent | `clear_stale_cache` | 1 heure | Nettoyage cache obsolète |
| MaestroAgent | `health_check_all` | 3 minutes | Santé de tous les agents |

### Modifier la Planification

Éditez `deploy/agents/orchestrator/agent_scheduler.py`:

```python
self.schedules = {
    "monitoring_health_check": {
        "agent": "monitoring",
        "operation": "health_check",
        "interval": 120,  # Changé à 2 minutes
        "enabled": True
    }
}
```

---

## 🚀 Déploiement

### Déploiement Complet (Recommandé)

Exécute tout le pipeline: déploiement, import dashboard, tests d'intégration.

```powershell
.\scripts\deploy_and_test_all.ps1
```

**Ce script fait**:
1. ✅ Déploie les agents sur edgeserver
2. ✅ Import le dashboard Grafana
3. ✅ Vérifie l'API
4. ✅ Exécute les tests d'intégration
5. ✅ Affiche les points d'accès

### Déploiement Manuel (Étapes Individuelles)

#### Étape 1: Déployer les Agents

```powershell
.\scripts\deploy_real_agents.ps1
```

#### Étape 2: Redémarrer l'API

```bash
ssh root@192.168.0.30
docker service update --force twisterlab_api
```

#### Étape 3: Vérifier les Agents

```bash
curl -X POST http://192.168.0.30:8000/agents/monitoring/execute \
  -H 'Content-Type: application/json' \
  -d '{"operation":"health_check"}'
```

---

## 🧪 Tests

### Tests Locaux (Développement)

Test tous les agents localement (sans infrastructure Docker):

```powershell
python scripts\test_all_agents.py
```

**Résultat attendu**:
```
[+] SUCCESS    MonitoringAgent
[+] SUCCESS    BackupAgent
[+] SUCCESS    SyncAgent
[+] SUCCESS    ClassifierAgent
[+] SUCCESS    ResolverAgent
[+] SUCCESS    DesktopCommanderAgent
[+] SUCCESS    MaestroAgent

Overall Success Rate: 100.0%
```

### Tests d'Intégration (Production)

Test avec l'infrastructure réelle (Redis, PostgreSQL, Docker):

```powershell
python tests\test_integration_real_agents.py
```

**Tests effectués** (10 total):
1. MonitoringAgent - Health Check
2. MonitoringAgent - Full Diagnostic
3. BackupAgent - List Backups
4. BackupAgent - Create Backup
5. SyncAgent - Verify Consistency
6. ClassifierAgent - Classify Ticket
7. ResolverAgent - List SOPs
8. ResolverAgent - Execute SOP
9. DesktopCommanderAgent - System Info
10. MaestroAgent - Health Check All

---

## 📊 Monitoring & Dashboards

### Grafana Dashboard

**URL**: `http://192.168.0.30:3000/d/twisterlab-real-agents`
**Login**: `admin / admin`

**Panels Disponibles**:
- 📈 Agent Execution Count (Last Hour)
- 🎯 Agent Success Rate (Gauge)
- ✅ Active Agents (Stat)
- ⏱️ Average Execution Time
- 📊 Executions by Agent (Timeseries)
- 🏥 Agent Health Status (Table)
- 🔥 Execution Duration by Agent (Heatmap)
- ✅/❌ Success vs Error Rate
- 💻 MonitoringAgent - System Metrics
- 💾 BackupAgent - Backup Statistics
- 🔄 SyncAgent - Consistency Status
- 🎯 ClassifierAgent - Classification Distribution
- ⚙️ ResolverAgent - SOP Success Rate
- 🎭 MaestroAgent - Orchestration Workflows
- 📅 Scheduler Statistics (Table)

### Métriques Prometheus

Les agents exposent des métriques via l'API:

```
# Exemple de métriques
agent_executions_total{agent_name="monitoring"} 142
agent_executions_success_total{agent_name="monitoring"} 140
agent_execution_duration_seconds{agent_name="monitoring"} 0.23
agent_health_status{agent_name="monitoring"} 1

monitoring_agent_cpu_percent 15.2
monitoring_agent_memory_percent 45.8
monitoring_agent_disk_percent 52.3

backup_agent_total_backups 24
backup_agent_last_backup_size_mb 125.4

sync_agent_consistency_percentage 99.8

classifier_agent_classifications_total{category="network"} 45
resolver_agent_sop_executions_total{sop_id="SOP-001"} 23
```

---

## 🔍 Surveillance et Debugging

### Logs du Scheduler

Voir les exécutions automatiques des agents:

```bash
ssh root@192.168.0.30
docker logs -f twisterlab_api | grep "scheduler"
```

**Exemple de sortie**:
```
[INFO] 📅 Task 'monitoring_health_check' completed (0.45s)
[INFO] ✅ Task 'sync_verify_consistency' completed (1.23s)
[INFO] ⏰ Executing scheduled task: backup_create
```

### Logs des Agents

```bash
docker logs -f twisterlab_api | grep "RealMonitoringAgent"
```

### Santé Globale

Vérifier la santé de tous les agents via MaestroAgent:

```bash
curl -X POST http://192.168.0.30:8000/agents/maestro/execute \
  -H 'Content-Type: application/json' \
  -d '{"operation":"health_check_all"}' | jq
```

**Résultat**:
```json
{
  "status": "success",
  "total_agents": 6,
  "healthy_agents": 6,
  "unhealthy_agents": 0,
  "agents": {
    "monitoring": {"status": "healthy"},
    "backup": {"status": "healthy"},
    "sync": {"status": "healthy"},
    "classifier": {"status": "healthy"},
    "resolver": {"status": "healthy"},
    "desktop_commander": {"status": "healthy"}
  }
}
```

---

## 🔧 Troubleshooting

### Agent ne répond pas

1. Vérifier l'API:
   ```bash
   curl http://192.168.0.30:8000/health
   ```

2. Vérifier le container:
   ```bash
   docker ps | grep twisterlab_api
   docker logs twisterlab_api --tail 50
   ```

3. Redémarrer le service:
   ```bash
   docker service update --force twisterlab_api
   ```

### Scheduler ne s'exécute pas

1. Vérifier les logs:
   ```bash
   docker logs twisterlab_api | grep "AgentScheduler"
   ```

2. Vérifier la configuration:
   ```bash
   docker exec twisterlab_api cat /opt/twisterlab/deploy/agents/orchestrator/agent_scheduler.py | grep "self.schedules"
   ```

### Tests d'intégration échouent

1. Vérifier la connectivité:
   ```bash
   ping 192.168.0.30
   curl http://192.168.0.30:8000/health
   ```

2. Vérifier Redis/PostgreSQL:
   ```bash
   docker service ls | grep -E "redis|postgres"
   ```

3. Tester manuellement un agent:
   ```bash
   curl -X POST http://192.168.0.30:8000/agents/monitoring/execute \
     -H 'Content-Type: application/json' \
     -d '{"operation":"health_check"}' | jq
   ```

---

## 📈 Performance & Optimisation

### Ajuster les Intervalles

Pour réduire la charge:

```python
# deploy/agents/orchestrator/agent_scheduler.py
"monitoring_health_check": {
    "interval": 300,  # 5 minutes au lieu de 1
}
```

### Désactiver un Task

```python
"backup_create": {
    "enabled": False,  # Désactive le backup automatique
}
```

### Timeout Personnalisé

```python
# Dans _run_scheduled_task()
result = await asyncio.wait_for(
    agent.execute({...}),
    timeout=600  # 10 minutes au lieu de 5
)
```

---

## 🎯 Prochaines Étapes

### Court Terme
- [ ] Ajouter alerting Prometheus (seuils critiques)
- [ ] Exporter métriques agents vers Prometheus
- [ ] Créer dashboard agent-spécifiques (1 par agent)

### Moyen Terme
- [ ] Implémenter retry automatique sur échec
- [ ] Ajouter webhook notifications (Discord/Slack)
- [ ] Créer API endpoint pour modifier schedules dynamiquement

### Long Terme
- [ ] Machine Learning pour prédiction de pannes
- [ ] Auto-scaling des agents selon la charge
- [ ] Distributed agents sur plusieurs nœuds

---

## 📚 Références

- [Architecture Document](REAL_AGENTS_COMPLETE.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Grafana Dashboards](monitoring/grafana/dashboards/)
- [Agent Source Code](agents/real/)
- [Tests](tests/test_integration_real_agents.py)

---

**Version**: 1.0.0
**Dernière mise à jour**: 2025-11-11
**Status**: ✅ Production Ready

🎉 **Tous les agents sont déployés et fonctionnent de manière autonome!**
