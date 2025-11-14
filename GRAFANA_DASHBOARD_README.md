# TwisterLab Monitoring Dashboard

## Vue d'ensemble

Ce dashboard Grafana complet fournit une surveillance en temps réel de l'infrastructure TwisterLab, incluant tous les services, agents autonomes et métriques de performance.

## Accès au Dashboard

- **URL**: http://192.168.0.30:3000
- **Utilisateur**: admin
- **Mot de passe**: admin
- **Dashboard**: "TwisterLab - Complete Monitoring Dashboard"

## Métriques Monitorées

### 🔧 Système
- **CPU Usage**: Utilisation processeur en %
- **Memory Usage**: Utilisation mémoire RAM en %
- **Disk Usage**: Utilisation espace disque par partition
- **Network I/O**: Trafic réseau entrant/sortant

### 🐳 Services Docker
- **Service Status**: État de santé de tous les services (up/down)
- **Response Time**: Temps de réponse des services (P50, P95)
- **HTTP Status Codes**: Répartition des codes de statut HTTP

### 🤖 Agents Autonomes
- **Agent Activity**: Nombre de requêtes par agent
- **Success Rate**: Taux de succès des opérations (%)
- **Ticket Processing**: Tickets traités (succès/échec)
- **Agent Performance**: Temps d'exécution des agents

### 🐘 Base de Données PostgreSQL
- **Active Connections**: Nombre de connexions actives
- **Query Rate**: Taux de requêtes (scans séquentiels/index)
- **Database Size**: Taille des bases de données

### 🔴 Cache Redis
- **Memory Usage**: Utilisation mémoire Redis
- **Hit Rate**: Taux de succès du cache
- **Operations**: Nombre d'opérations par commande

### 🤖 IA/LLM (Ollama)
- **Requests**: Nombre de requêtes vers Ollama
- **Response Time**: Temps de réponse (P50, P95)
- **Model Usage**: Utilisation par modèle

### 🚨 Alertes & Incidents
- **Active Alerts**: Alertes actuellement actives
- **Alert History**: Historique des alertes

## Configuration Requise

### Data Sources
- **Prometheus**: http://192.168.0.30:9090 (principale)
- **Node Exporter**: Métriques système
- **PostgreSQL Exporter**: Métriques base de données
- **Redis Exporter**: Métriques cache
- **Custom Exporters**: Pour les agents et API

### Métriques Personnalisées

Pour activer toutes les métriques, configurez ces exporters:

#### Agents TwisterLab
```prometheus
# Métriques des agents
agent_requests_total{agent_name="RealMonitoringAgent", status="success"} 150
agent_execution_time_seconds{agent_name="RealMonitoringAgent"} 2.5

# Tickets traités
tickets_processed_total{status="success"} 45
tickets_failed_total 3
```

#### API Métriques
```prometheus
# Métriques HTTP
http_requests_total{method="GET", endpoint="/health", status="200"} 1250
http_request_duration_seconds{quantile="0.95", method="POST"} 0.15
```

#### Services Santé
```prometheus
# État des services
up{job="twisterlab-api", service="api"} 1
up{job="twisterlab-postgres", service="database"} 1
up{job="twisterlab-ollama", service="llm"} 1
```

## Utilisation

### Navigation
1. **Time Range**: Utilisez le sélecteur de temps en haut pour zoomer
2. **Refresh**: Auto-refresh toutes les 30 secondes
3. **Panels**: Cliquez sur le titre d'un panel pour voir les options

### Alertes
Configurez des alertes dans Grafana pour:
- CPU > 80%
- Mémoire > 90%
- Services down
- Erreurs API > 5%
- Cache hit rate < 80%

### Personnalisation
- **Variables**: Ajoutez des variables pour filtrer par service/agent
- **Annotations**: Marquez des événements importants
- **Thresholds**: Définissez des seuils visuels sur les graphs

## Architecture Monitorée

```
TwisterLab Infrastructure
├── API FastAPI (port 8000)
├── PostgreSQL (port 5432)
├── Redis (port 6379)
├── Ollama (port 11434)
├── Open WebUI (port 8083)
├── Grafana (port 3000)
└── Agents Autonomes
    ├── RealMonitoringAgent
    ├── RealBackupAgent
    ├── RealSyncAgent
    ├── RealClassifierAgent
    ├── RealResolverAgent
    ├── RealDesktopCommanderAgent
    └── RealMaestroAgent
```

## Scripts de Déploiement

- `deploy-monitoring.ps1`: Script principal de déploiement
- `setup-grafana-datasource.ps1`: Configuration data source
- `import-grafana-dashboard.ps1`: Import du dashboard

## Support

Pour des métriques manquantes ou des problèmes:
1. Vérifiez que Prometheus est configuré
2. Vérifiez les exporters des services
3. Consultez les logs des services
4. Vérifiez la configuration réseau

---

**Dashboard Version**: 1.0.0
**Grafana Version**: Compatible 8.x+
**Prometheus Version**: Compatible 2.x+
