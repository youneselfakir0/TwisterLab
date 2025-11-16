# Guide d'Utilisation - MCP Tools TwisterLab dans Continue

## Vue d'ensemble

Continue intègre les 7 agents TwisterLab via le protocole MCP (Model Context Protocol). Chaque agent expose des outils avec des **policies de sécurité** configurables.

## 📋 Outils Disponibles (7 agents)

### 1. 🔍 **Monitor System Health** (RealMonitoringAgent)
- **Endpoint**: `/v1/mcp/tools/monitor_system_health`
- **Policy**: `automatic` ✅
- **Description**: Surveillance système (CPU, RAM, disque, Docker)
- **Capabilities**: cpu_monitoring, ram_monitoring, disk_monitoring, docker_health

**Utilisation dans Continue**:
```
@mcp monitor_system_health {"include_docker": true, "threshold_cpu_percent": 80}
```

---

### 2. 💾 **Create Backup** (RealBackupAgent)
- **Endpoint**: `/v1/mcp/tools/create_backup`
- **Policy**: `ask` ⚠️ (demande confirmation)
- **Description**: Backup automatisé (PostgreSQL, Redis, configs)
- **Capabilities**: postgres_backup, redis_backup, config_backup, incremental_backup

**Utilisation dans Continue**:
```
@mcp create_backup {"backup_type": "incremental", "targets": ["database", "redis"], "encryption": true}
```

---

### 3. 🔄 **Sync Cache** (RealSyncAgent)
- **Endpoint**: `/v1/mcp/tools/sync_cache`
- **Policy**: `automatic` ✅
- **Description**: Synchronisation Redis ⇄ PostgreSQL
- **Capabilities**: redis_sync, postgres_sync, conflict_resolution

**Utilisation dans Continue**:
```
@mcp sync_cache {"direction": "bidirectional", "conflict_resolution": "latest_wins"}
```

---

### 4. 🎯 **Classify Ticket** (RealClassifierAgent)
- **Endpoint**: `/v1/mcp/tools/classify_ticket`
- **Policy**: `automatic` ✅
- **Description**: Classification LLM de tickets (llama3.2:1b)
- **Capabilities**: llm_classification, confidence_scoring, priority_assignment
- **Categories**: network, hardware, software, account, email

**Utilisation dans Continue**:
```
@mcp classify_ticket {"title": "Wi-Fi ne marche pas", "description": "Impossible de se connecter au réseau", "llm_model": "llama3.2:1b"}
```

---

### 5. ✅ **Resolve Ticket** (RealResolverAgent)
- **Endpoint**: `/v1/mcp/tools/resolve_ticket`
- **Policy**: `ask` ⚠️ (demande confirmation)
- **Description**: Résolution via SOPs (network, hardware, software)
- **Capabilities**: sop_execution, troubleshooting, guided_resolution

**Utilisation dans Continue**:
```
@mcp resolve_ticket {"ticket_id": "TKT-12345", "category": "network", "auto_execute": false}
```

---

### 6. 🖥️ **Execute Desktop Command** (RealDesktopCommanderAgent)
- **Endpoint**: `/v1/mcp/tools/execute_desktop_command`
- **Policy**: `ask` ⚠️ (demande confirmation + whitelist uniquement)
- **Security**: `whitelisted_commands_only`
- **Description**: Exécution distante de commandes (PowerShell, Bash, SSH)
- **Capabilities**: powershell_execution, bash_execution, ssh_commands

**Utilisation dans Continue**:
```
@mcp execute_desktop_command {"command": "Get-Process", "target_host": "192.168.0.30", "shell": "powershell"}
```

---

### 7. 📋 **List Autonomous Agents** (Registry)
- **Endpoint**: `/v1/mcp/tools/list_autonomous_agents`
- **Policy**: `automatic` ✅
- **Description**: Liste tous les agents disponibles
- **Capabilities**: agent_registry, status_monitoring

**Utilisation dans Continue**:
```
@mcp list_autonomous_agents
```

---

## 🔒 Policies de Sécurité

### ✅ **automatic** (Vert)
- S'exécute **immédiatement** sans demander confirmation
- Utilisé pour outils de lecture/monitoring
- **Outils concernés**:
  - `monitor_system_health`
  - `sync_cache`
  - `classify_ticket`
  - `list_autonomous_agents`

### ⚠️ **ask** (Orange)
- **Demande confirmation** avant exécution
- Utilisé pour outils d'écriture/modification
- Affiche un résumé de l'action avant validation
- **Outils concernés**:
  - `create_backup`
  - `resolve_ticket`
  - `execute_desktop_command`

### ❌ **disabled** (Rouge)
- Outil **désactivé**, ne peut pas être utilisé
- Utile pour désactiver temporairement des outils dangereux
- **Actuellement**: Aucun outil désactivé

---

## 🛠️ Configuration des Policies

### Fichier de configuration: `.continue/mcp-tools-config.json`

Pour **activer/désactiver** ou changer la policy d'un outil :

```json
{
  "tools": [
    {
      "name": "execute_desktop_command",
      "policy": "disabled",  // Désactiver l'outil
      "enabled": false
    },
    {
      "name": "create_backup",
      "policy": "automatic",  // Passer en automatique (DANGER !)
      "enabled": true
    }
  ]
}
```

**⚠️ ATTENTION**: Ne **JAMAIS** mettre `execute_desktop_command` en `automatic` sans validation stricte des commandes !

---

## 📊 Accès aux Outils dans Continue

### Méthode 1: Menu Tools
1. Ouvrir la palette Continue (`Ctrl+Shift+P` → "Continue")
2. Cliquer sur **"Tools"** dans la barre latérale
3. Section **"MCP Servers"** → "TwisterLab MCP"
4. Voir les **17 built-in tools** + **7 TwisterLab tools**

### Méthode 2: Commande @mcp
Dans le chat Continue, utiliser `@mcp <tool_name> <arguments>`

**Exemple**:
```
@mcp monitor_system_health {"include_docker": true}
```

### Méthode 3: REST API directe
```powershell
Invoke-WebRequest -Uri "http://192.168.0.30:8000/v1/mcp/tools/monitor_system_health" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"include_docker": true}'
```

---

## 🔍 Inspection des Outils

### Lister tous les agents disponibles
```powershell
Invoke-WebRequest -Uri "http://192.168.0.30:8000/v1/mcp/tools/list_autonomous_agents" -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### Vérifier la santé du système
```powershell
Invoke-WebRequest -Uri "http://192.168.0.30:8000/v1/mcp/tools/monitor_system_health" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"include_docker": true}' | Select-Object -ExpandProperty Content
```

### Classifier un ticket
```powershell
Invoke-WebRequest -Uri "http://192.168.0.30:8000/v1/mcp/tools/classify_ticket" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"title": "Imprimante ne fonctionne pas", "description": "Erreur lors de l impression"}' | Select-Object -ExpandProperty Content
```

---

## 📝 Logs et Audit

Les appels MCP sont loggés dans :
- **API Logs**: `docker service logs twisterlab_api`
- **Prometheus Metrics**: `http://192.168.0.30:9090`
- **Grafana Dashboards**: `http://192.168.0.30:3000`

Pour voir les logs en temps réel :
```bash
ssh twister@192.168.0.30 "docker service logs -f twisterlab_api"
```

---

## 🚨 Sécurité

### Commandes whitelistées uniquement
`RealDesktopCommanderAgent` utilise une **whitelist stricte** :
- Liste définie dans `agents/real/real_desktop_commander_agent.py`
- **Toute commande non whitelistée est rejetée**
- Audit logging de toutes les tentatives

### Credentials chiffrés
- Stored in encrypted vault (Fernet encryption)
- Tier-based access: `enterprise` vs `personal`
- Jamais exposés dans les logs

### Authentification hybride
- Azure AD (production)
- Local fallback (développement)
- JWT tokens avec expiration

---

## 📚 Références

- **API Documentation**: http://192.168.0.30:8000/docs
- **MCP Protocol**: https://modelcontextprotocol.io
- **Continue Docs**: https://docs.continue.dev
- **TwisterLab Guide**: `copilot-instructions.md`

---

## 🔧 Troubleshooting

### Outil ne répond pas
```bash
# Vérifier l'API
curl http://192.168.0.30:8000/health

# Vérifier les logs
ssh twister@192.168.0.30 "docker service logs twisterlab_api --tail 50"
```

### Policy "ask" ne demande pas confirmation
- Vérifier que Continue est à jour (>= v0.8.0)
- Recharger la configuration : `Ctrl+Shift+P` → "Continue: Reload Config"
- Vérifier `.continue/mcp-tools-config.json`

### Commande whitelistée rejetée
- Vérifier la whitelist dans `agents/real/real_desktop_commander_agent.py`
- Ajouter la commande si nécessaire
- Redéployer : `infrastructure/scripts/deploy.ps1 -Environment production`

---

**Version**: 1.0.0
**Last Updated**: 2025-11-12
**Status**: ✅ Operational (7/7 agents running)
