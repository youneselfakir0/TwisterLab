# 🎯 TwisterLab MCP Tools - Quick Reference

## 🔍 Distinction Importante

### 🛠️ Built-in Tools (17 tools Continue)
- **Source**: Continue.dev natif
- **Config**: Automatique, pas de JSON
- **Exemples**: file_search, grep_search, run_terminal, etc.
- **Affichage**: Section "Built-in Tools" dans Continue

### 🤖 TwisterLab MCP Tools (7 agents)
- **Source**: API TwisterLab (`http://192.168.0.30:8000`)
- **Config**: `.continue/mcpServers/twisterlab-mcp.json`
- **Serveur**: `agents/mcp/mcp_server_continue_sync.py` (v2.1.0)
- **Exemples**: monitor_system_health, classify_ticket, resolve_ticket
- **Affichage**: Section "MCP Servers" → "TwisterLab MCP"

---

## 🔧 Architecture Unifiée (v2.1.0)

### Serveur MCP Actif
- **Fichier**: `agents/mcp/mcp_server_continue_sync.py`
- **Version**: 2.1.0 (Enhanced error handling & API health checks)
- **Mode**: REAL (appels HTTP à l'API TwisterLab)
- **Protocole**: MCP 2024-11-05
- **Transport**: stdio (JSON-RPC 2.0)

### Améliorations v2.1.0
- ✅ **Vérification santé API** au démarrage
- ✅ **Gestion d'erreur spécifique** (httpx.TimeoutException, HTTPStatusError, etc.)
- ✅ **Fallback automatique** vers mode MOCK si API indisponible
- ✅ **Logs détaillés** pour debugging
- ✅ **Timeout configurable** (60s pour opérations LLM)

---

## 📋 Liste des 7 Outils TwisterLab

## 📋 Liste des 7 Outils TwisterLab

| # | Outil | Agent | Policy | Action |
|---|-------|-------|--------|--------|
| 1 | 🔍 Monitor System Health | RealMonitoringAgent | ✅ automatic | Surveillance CPU/RAM/Disk/Docker |
| 2 | 💾 Create Backup | RealBackupAgent | ⚠️ ask | Backup PostgreSQL/Redis/configs |
| 3 | 🔄 Sync Cache | RealSyncAgent | ✅ automatic | Sync Redis ⇄ PostgreSQL |
| 4 | 🎯 Classify Ticket | RealClassifierAgent | ✅ automatic | Classification LLM (llama3.2:1b) |
| 5 | ✅ Resolve Ticket | RealResolverAgent | ⚠️ ask | Résolution via SOPs |
| 6 | 🖥️ Execute Desktop Command | RealDesktopCommanderAgent | ⚠️ ask | Commandes distantes (whitelist) |
| 7 | 📋 List Agents | Registry | ✅ automatic | Liste tous les agents |

---

## 🔧 Comment Voir les Outils dans Continue

### 1️⃣ Ouvrir le Menu Tools
```
Ctrl+Shift+P → "Continue: Open Tools"
```

### 2️⃣ Sections Affichées
- **Built-in Tools (17)**: Outils Continue natifs
- **MCP Servers**:
  - **TwisterLab MCP (7)**: Vos agents autonomes

### 3️⃣ Actions Possibles
- ✅ **Activer/Désactiver** un outil
- ⚙️ **Changer la policy**: automatic ⇄ ask ⇄ disabled
- 📊 **Voir les détails**: description, capabilities, input schema

---

## 🎮 Utilisation dans le Chat Continue

### Syntaxe
```
@mcp <tool_name> <json_arguments>
```

### Exemples

#### Surveiller le système
```
@mcp monitor_system_health {"include_docker": true, "threshold_cpu_percent": 80}
```

#### Classifier un ticket
```
@mcp classify_ticket {"title": "Wi-Fi ne fonctionne pas", "description": "Impossible de se connecter au réseau sans fil depuis ce matin"}
```

#### Créer un backup (demande confirmation)
```
@mcp create_backup {"backup_type": "incremental", "targets": ["database", "redis"], "encryption": true}
```

#### Lister les agents
```
@mcp list_autonomous_agents
```

---

## ⚙️ Modifier les Policies

### Fichier: `.continue/mcp-tools-config.json`

#### Désactiver un outil dangereux
```json
{
  "name": "execute_desktop_command",
  "policy": "disabled",
  "enabled": false
}
```

#### Passer un outil en automatique (prudence !)
```json
{
  "name": "create_backup",
  "policy": "automatic",
  "enabled": true
}
```

#### Passer un outil en mode confirmation
```json
{
  "name": "sync_cache",
  "policy": "ask",
  "enabled": true
}
```

### Recharger la Configuration
```
Ctrl+Shift+P → "Continue: Reload Config"
```

---

## 🔒 Policies de Sécurité

| Policy | Icône | Comportement | Outils Concernés |
|--------|-------|--------------|------------------|
| **automatic** | ✅ | Exécution immédiate sans confirmation | monitor_system_health, sync_cache, classify_ticket, list_agents |
| **ask** | ⚠️ | Demande confirmation avant exécution | create_backup, resolve_ticket, execute_desktop_command |
| **disabled** | ❌ | Outil désactivé, ne peut pas être utilisé | Aucun (configurable) |

---

## 📊 Architecture MCP

```
┌─────────────────────────────────────────┐
│  Continue.dev (VS Code Extension)       │
│  - 17 Built-in Tools                    │
│  - Chat Interface                       │
└─────────────────┬───────────────────────┘
                  │ MCP Protocol
                  ▼
┌─────────────────────────────────────────┐
│  TwisterLab MCP Server                  │
│  (agents/mcp/mcp_server_continue_sync.py)│
│  - Routes vers API REST                 │
└─────────────────┬───────────────────────┘
                  │ HTTP REST
                  ▼
┌─────────────────────────────────────────┐
│  TwisterLab API (Docker Swarm)          │
│  http://192.168.0.30:8000               │
│  - 7 Real Agents                        │
│  - PostgreSQL + Redis                   │
│  - Ollama LLM (CoreRTX)                 │
└─────────────────────────────────────────┘
```

---

## 🧪 Tester les Outils

### Via Continue Chat
```
@mcp list_autonomous_agents
```

### Via PowerShell (API REST directe)
```powershell
# Lister les agents
Invoke-WebRequest -Uri "http://192.168.0.30:8000/v1/mcp/tools/list_autonomous_agents" -UseBasicParsing

# Surveiller le système
Invoke-WebRequest -Uri "http://192.168.0.30:8000/v1/mcp/tools/monitor_system_health" `
  -Method POST -ContentType "application/json" `
  -Body '{"include_docker": true}'
```

---

## 📚 Documentation Complète

- **Guide Détaillé**: `.continue/MCP_TOOLS_GUIDE.md`
- **Configuration**: `.continue/mcp-tools-config.json`
- **API Docs**: http://192.168.0.30:8000/docs
- **TwisterLab Guide**: `copilot-instructions.md`

---

**Status**: ✅ Operational
**API**: http://192.168.0.30:8000
**Agents**: 7/7 running
**Version**: 1.0.1
