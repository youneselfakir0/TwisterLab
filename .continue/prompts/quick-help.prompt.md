---
description: "Aide rapide et commandes courantes TwisterLab"
---

# 🚀 TwisterLab - Aide Rapide

Guide ultra-rapide des commandes et outils TwisterLab les plus utilisés.

## 📋 Prompts Système Disponibles

```bash
@prompt troubleshoot-system   # Diagnostic infrastructure (90 min)
@prompt debug-mcp              # Fix connexion MCP (10 min)
@prompt optimize-pc            # Nettoyage PC (2h)
@prompt simulate-tickets-6h    # Test agents 6h (overnight)
@prompt quick-help             # Ce guide
```

## 🔧 MCP Tools (7 agents)

```bash
# État système
@mcp list_autonomous_agents     # Liste 7 agents actifs
@mcp monitor_system_health      # CPU/RAM/Disk/Docker metrics

# Maintenance
@mcp create_backup              # Backup PostgreSQL + configs
@mcp sync_cache                 # Sync Redis ↔ PostgreSQL

# Helpdesk
@mcp classify_ticket            # Classifier ticket avec LLM
@mcp resolve_ticket             # Exécuter SOP automatique
@mcp execute_desktop_command    # Commande système Windows/Linux
```

## 🌐 Infrastructure

```yaml
CoreRTX (192.168.0.20):
  - Ollama GPU         : http://192.168.0.20:11434
  - Models             : llama3.2:1b, llama3:8b, deepseek-r1, codellama, qwen3:8b
  - GPU                : RTX 3060 12GB

edgeserver (192.168.0.30):
  - TwisterLab API     : http://192.168.0.30:8000
  - Open WebUI         : http://192.168.0.30:8083
  - Grafana            : http://192.168.0.30:3000
  - Prometheus         : http://192.168.0.30:9090
  - PostgreSQL         : 192.168.0.30:5432
  - Redis              : 192.168.0.30:6379
```

## ⚡ Commandes Rapides PowerShell

### Status Check (2 min)
```powershell
# API Health
curl http://192.168.0.30:8000/health

# Ollama Health
curl http://192.168.0.20:11434/api/tags

# Docker Services
ssh twister@192.168.0.30 "docker service ls"

# MCP Test
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test"}}}' | python agents/mcp/mcp_server_continue_sync.py
```

### Logs (1 min)
```powershell
# API Logs (dernières 100 lignes)
ssh twister@192.168.0.30 "docker service logs twisterlab_api --tail 100"

# PostgreSQL Logs
ssh twister@192.168.0.30 "docker service logs twisterlab_postgres --tail 50"

# Redis Logs
ssh twister@192.168.0.30 "docker service logs twisterlab_redis --tail 50"
```

### Déploiement (5 min)
```powershell
# Déployer staging
.\infrastructure\scripts\deploy.ps1 -Environment staging

# Déployer production
.\infrastructure\scripts\deploy.ps1 -Environment production

# Force redéploiement
.\infrastructure\scripts\deploy.ps1 -Environment production -Force
```

### Tests (3 min)
```powershell
# Tous les tests
pytest tests/ -v

# Tests avec coverage
pytest tests/ -v --cov=agents --cov-report=html

# Test agent spécifique
pytest tests/test_monitoring_agent.py -v

# Tests async seulement
pytest tests/ -v -m asyncio
```

### Cleanup (5 min)
```powershell
# Docker cleanup local
docker system prune -a -f

# Cleanup Python
pip cache purge
Get-ChildItem -Path . -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

# Cleanup logs anciens
Get-ChildItem -Filter "*.log" | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | Remove-Item -Force
```

## 🐛 Troubleshooting Express (5 min)

### Problème : "Connection refused (errno 111)"
```powershell
# 1. Test MCP server
python agents/mcp/mcp_server_continue_sync.py

# 2. Test API
curl http://192.168.0.30:8000/health

# 3. Si API down → mode MOCK (normal)
# MCP server bascule automatiquement en MOCK

# 4. Fix complet
@prompt debug-mcp
```

### Problème : Services Docker down
```powershell
# 1. Vérifier services
ssh twister@192.168.0.30 "docker service ls"

# 2. Redémarrer service spécifique
ssh twister@192.168.0.30 "docker service update --force twisterlab_api"

# 3. Redéployer stack complète
ssh twister@192.168.0.30 "cd /home/twister && docker stack deploy -c docker-compose.yml twisterlab"
```

### Problème : Ollama GPU lent
```powershell
# 1. Vérifier GPU
ssh twister@192.168.0.20 "nvidia-smi"

# 2. Vérifier Ollama
curl http://192.168.0.20:11434/api/tags

# 3. Redémarrer Ollama
ssh twister@192.168.0.20 "sudo systemctl restart ollama"
```

### Problème : PostgreSQL queries lentes
```powershell
# 1. Connexion PostgreSQL
ssh twister@192.168.0.30
docker exec -it $(docker ps -q -f name=twisterlab_postgres) psql -U twisterlab

# 2. Queries actives
SELECT pid, query, state, wait_event_type FROM pg_stat_activity WHERE state = 'active';

# 3. Tuer query bloquante
SELECT pg_terminate_backend(PID);

# 4. Vacuum + Analyze
VACUUM ANALYZE;
```

## 📊 Monitoring Rapide

### Grafana (2 min)
```
1. Ouvrir http://192.168.0.30:3000
2. Dashboard "TwisterLab Overview"
3. Vérifier :
   - CPU < 70%
   - RAM < 80%
   - Disk < 85%
   - Tous services UP
```

### CLI Monitoring (1 min)
```powershell
# Métriques système via MCP
@mcp monitor_system_health

# Docker stats
ssh twister@192.168.0.30 "docker stats --no-stream"

# PostgreSQL connections
ssh twister@192.168.0.30 'docker exec $(docker ps -q -f name=postgres) psql -U twisterlab -c "SELECT count(*) FROM pg_stat_activity;"'

# Redis memory
ssh twister@192.168.0.30 'docker exec $(docker ps -q -f name=redis) redis-cli INFO memory | grep used_memory_human'
```

## 🔑 Credentials & Secrets

```yaml
⚠️  JAMAIS commit credentials dans Git !

Localisation:
  - Production : /home/twister/.env.production (edgeserver)
  - Staging    : /home/twister/.env.staging (edgeserver)
  - Local      : C:\TwisterLab\.env.local (TwisterLab PC)

Accès via:
  - os.getenv("VARIABLE_NAME")
  - Docker secrets (mode Swarm)

Variables clés:
  - POSTGRES_PASSWORD
  - REDIS_PASSWORD
  - API_SECRET_KEY
  - OLLAMA_API_BASE
```

## 📖 Documentation Complète

```bash
# README principal
cat README.md

# Guide infrastructure
cat infrastructure/README.md

# Guide agents
cat agents/README.md

# Guide MCP
cat agents/mcp/README.md

# Prompts système
cat .continue/prompts/README.md

# Changelog
cat CHANGELOG.md
```

## 🆘 Aide Contexte-Spécifique

```bash
# Diagnostic complet infrastructure
@prompt troubleshoot-system

# Debug MCP Continue
@prompt debug-mcp

# Nettoyage et optimisation PC
@prompt optimize-pc

# Test charge 6h
@prompt simulate-tickets-6h

# Aide rapide (ce guide)
@prompt quick-help
```

## 🎯 Workflows Courants

### Morning Check (5 min)
```powershell
# 1. Status services
@mcp list_autonomous_agents

# 2. Métriques système
@mcp monitor_system_health

# 3. Logs erreurs
ssh twister@192.168.0.30 "docker service logs twisterlab_api --tail 100 | grep -i error"

# 4. Grafana overview
Start-Process "http://192.168.0.30:3000"
```

### Avant Déploiement (10 min)
```powershell
# 1. Tests complets
pytest tests/ -v --cov=agents

# 2. Backup production
@mcp create_backup

# 3. Staging deploy
.\infrastructure\scripts\deploy.ps1 -Environment staging

# 4. Smoke tests staging
curl http://localhost:8000/health

# 5. Production deploy
.\infrastructure\scripts\deploy.ps1 -Environment production
```

### Debug Session (30 min)
```powershell
# 1. Reproduire problème
# [actions manuelles]

# 2. Collecter logs
ssh twister@192.168.0.30 "docker service logs twisterlab_api --tail 500" > debug_api.log

# 3. Analyser avec agent
@mcp monitor_system_health

# 4. Diagnostic complet
@prompt troubleshoot-system

# 5. Fix et redeploy
git commit -am "fix: [description]"
git push
.\infrastructure\scripts\deploy.ps1 -Environment production
```

### Overnight Test (6h)
```powershell
# 1. Backup avant test
@mcp create_backup

# 2. Lancer simulation
@prompt simulate-tickets-6h

# 3. Laisser tourner 6h
# (aller dormir 😴)

# 4. Matin : consulter rapport
# Continue génère rapport automatique

# 5. Analyser résultats
# Tickets résolus, taux succès, performance agents
```

---

## 📞 Contact & Support

**Documentation** : `.continue/prompts/README.md`  
**Config Continue** : `.continue/config.yaml`  
**MCP Config** : `.continue/mcpServers/twisterlab-mcp.json`  
**MCP Server** : `agents/mcp/mcp_server_continue_sync.py`

**GitHub** : https://github.com/youneselfakir0/TwisterLab  
**Version** : 1.0.0  
**Date** : 2025-11-12

---

**💡 Tip** : Ajouter ce fichier aux favoris Continue pour accès rapide !
