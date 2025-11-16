# 🚀 GUIDE DE DÉPLOIEMENT PRODUCTION - TwisterLab v1.0.0

## Vue d'ensemble
Ce guide détaille le déploiement en production du système TwisterLab v1.0.0, un système d'agents autonomes pour l'automatisation des helpdesks IT.

## Prérequis Système

### Infrastructure Requise
- **Windows Server 2022/2025** ou **Windows 11 Pro/Enterprise**
- **Docker Desktop** avec **Swarm activé**
- **Python 3.11+** installé
- **8GB RAM minimum** (16GB recommandé)
- **50GB espace disque** pour données et backups

### Réseau
- **Ports ouverts**: 8000 (API), 8083 (Traefik), 3001 (Grafana), 9090 (Prometheus)
- **Résolution DNS** configurée pour les services locaux

---

## 📋 CHECKLIST PRÉ-DÉPLOIEMENT

### [ ] 1. Validation Environnement
```powershell
# Vérifier Python
python --version  # Doit être 3.11+

# Vérifier Docker
docker --version
docker swarm init  # Si pas déjà fait

# Vérifier espace disque
Get-WmiObject -Class Win32_LogicalDisk | Select-Object Size,FreeSpace
```

### [ ] 2. Configuration Réseau
```powershell
# Ajouter au fichier hosts (C:\Windows\System32\drivers\etc\hosts)
# 127.0.0.1    api.twisterlab.local
# 127.0.0.1    webui.twisterlab.local
# 127.0.0.1    traefik.twisterlab.local
# 127.0.0.1    grafana.twisterlab.local
# 127.0.0.1    prometheus.twisterlab.local
```

### [ ] 3. Préparation Données
```powershell
# Créer répertoires de données
New-Item -ItemType Directory -Path "C:\TwisterLab\data" -Force
New-Item -ItemType Directory -Path "C:\TwisterLab\backups" -Force
New-Item -ItemType Directory -Path "C:\TwisterLab\logs" -Force
```

---

## 🚀 DÉPLOIEMENT ÉTAPE PAR ÉTAPE

### Étape 1: Déploiement Infrastructure Swarm
```powershell
cd C:\TwisterLab

# Déployer la stack de monitoring d'abord
docker stack deploy -c docker-compose.monitoring.yml twisterlab-monitoring

# Attendre que les services soient opérationnels
Start-Sleep -Seconds 30
docker stack services twisterlab-monitoring

# Déployer la stack principale
docker stack deploy -c docker-compose.production.yml twisterlab_prod

# Vérifier le déploiement
docker stack services twisterlab_prod
```

### Étape 2: Démarrage Service API Windows
```powershell
# Installer les dépendances Python si nécessaire
C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe -m pip install fastapi uvicorn pydantic

# Démarrer le service API
.\run_api_service.ps1 -Action start -PythonPath "C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe"
```

### Étape 3: Validation Déploiement
```powershell
# Test API
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# Test agents
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/autonomous/agents" -UseBasicParsing

# Test monitoring
Invoke-WebRequest -Uri "http://localhost:3001/api/health" -UseBasicParsing
```

---

## 📊 MONITORING & OBSERVABILITÉ

### Accès aux Interfaces
- **API TwisterLab**: http://localhost:8000/docs (documentation interactive)
- **Grafana**: http://localhost:3001 (admin account configured via GRAFANA_ADMIN_USER/GRAFANA_ADMIN_PASSWORD or Docker secret)
- **Prometheus**: http://localhost:9090
- **Traefik Dashboard**: http://localhost:8084

### Métriques Clés à Surveiller
- **API Response Time**: < 100ms moyenne
- **Agent Success Rate**: > 99%
- **Database Connections**: < 80% utilisation
- **Memory Usage**: < 70% par service

---

## 🔧 MAINTENANCE QUOTIDIENNE

### Sauvegardes Automatiques
```powershell
# Configurer Windows Task Scheduler
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\TwisterLab\backup_system.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At "02:00"
Register-ScheduledTask -TaskName "TwisterLab_Backup" -Action $action -Trigger $trigger -User "SYSTEM"
```

### Logs et Monitoring
```powershell
# Vérification quotidienne
.\debug_complete_system.ps1

# Nettoyage logs (mensuel)
Get-ChildItem "C:\TwisterLab\logs\*.log" | Where-Object LastWriteTime -lt (Get-Date).AddDays(-30) | Remove-Item
```

---

## 🚨 PROCÉDURES DE SECOURS

### Redémarrage d'Urgence
```powershell
# Redémarrer API
.\run_api_service.ps1 -Action restart

# Redémarrer Swarm
docker stack rm twisterlab_prod
Start-Sleep -Seconds 10
docker stack deploy -c docker-compose.production.yml twisterlab_prod
```

### Rollback
```powershell
# Version précédente (si disponible)
docker service update --image twisterlab/api:v0.9 twisterlab_prod_api
```

---

## 📈 SCALING & OPTIMISATION

### Scale Up
```powershell
# Augmenter les réplicas
docker service scale twisterlab_prod_api=3
docker service scale twisterlab_prod_postgres=2
```

### Optimisation Performance
- **Database**: Indexer les tables fréquemment utilisées
- **Cache**: Augmenter Redis memory limit si nécessaire
- **API**: Activer GZIP compression pour les réponses

---

## 🔒 SÉCURITÉ

### Configuration de Base
- Changer tous les mots de passe par défaut
- Activer l'authentification Traefik
- Configurer HTTPS avec Let's Encrypt
- Restreindre l'accès réseau aux ports nécessaires

### Audit Régulier
```powershell
# Scan sécurité mensuel
python -m bandit -r api/ agents/
python -m safety check
```

---

## 📞 SUPPORT & CONTACT

### Logs Importants
- `C:\TwisterLab\logs\api_service.log` - Logs API
- `C:\TwisterLab\debug_report_*.json` - Rapports diagnostic
- Docker logs: `docker service logs twisterlab_prod_api`

### Commandes de Diagnostic
```powershell
# Status complet
.\debug_complete_system.ps1

# Tests agents
python test_autonomous_agents.py

# Health check
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
```

---

## ✅ CHECKLIST POST-DÉPLOIEMENT

### [ ] Services Opérationnels
- [ ] API répond sur port 8000
- [ ] Tous les agents accessibles
- [ ] Base de données connectée
- [ ] Interface web accessible

### [ ] Monitoring Configuré
- [ ] Grafana dashboards créés
- [ ] Alertes configurées
- [ ] Métriques collectées

### [ ] Sécurité Activée
- [ ] Mots de passe changés
- [ ] Accès réseau restreint
- [ ] HTTPS configuré

### [ ] Sauvegardes Opérationnelles
- [ ] Script de backup testé
- [ ] Planification automatique active
- [ ] Récupération testée

---

**Document Version**: 1.0.0
**Date**: November 9, 2025
**Auteur**: TwisterLab Team
**Status**: PRODUCTION READY</content>
<parameter name="filePath">c:\TwisterLab\PRODUCTION_DEPLOYMENT_GUIDE.md
