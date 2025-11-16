# 🎯 TwisterLab MCP Tools - Configuration Complète

## ✅ Ce qui a été créé

### 📄 Fichiers de Configuration

| Fichier | Description | Usage |
|---------|-------------|-------|
| **mcp-tools-config.json** | Configuration JSON des 7 outils TwisterLab avec policies | Défini automatic/ask/disabled pour chaque outil |
| **MCP_TOOLS_GUIDE.md** | Guide complet d'utilisation (8 Ko) | Documentation détaillée de tous les outils |
| **README.md** | Quick reference visuel (5.8 Ko) | Guide de démarrage rapide |
| **config.yaml** | Configuration Continue principale | Référence le fichier mcp-tools-config.json |

---

## 🎯 Distinction Essentielle

### ❌ Built-in Tools (17) - Continue.dev natif
**NE PAS CONFONDRE !**
Ce sont les outils intégrés à Continue :
- `file_search`, `grep_search`, `run_in_terminal`, etc.
- **Pas de configuration JSON nécessaire**
- **Aucun rapport avec TwisterLab**

### ✅ TwisterLab MCP Tools (7) - VOS agents !
**Ce sont VOS agents autonomes exposés via MCP** :
1. `monitor_system_health` - RealMonitoringAgent
2. `create_backup` - RealBackupAgent
3. `sync_cache` - RealSyncAgent
4. `classify_ticket` - RealClassifierAgent
5. `resolve_ticket` - RealResolverAgent
6. `execute_desktop_command` - RealDesktopCommanderAgent
7. `list_autonomous_agents` - Registry

**Configuration** : `.continue/mcp-tools-config.json` (ce fichier)

---

## 🔍 Comment Voir les Outils dans Continue

### Méthode 1: Menu Tools dans VS Code
1. `Ctrl+Shift+P` → "Continue: Open Tools"
2. Section **"Built-in Tools (17)"** → Outils Continue natifs
3. Section **"MCP Servers"** → **"TwisterLab MCP (7)"** → Vos agents

### Méthode 2: Fichier de Configuration
Ouvrir `.continue/mcp-tools-config.json` :
```json
{
  "tools": [
    {
      "name": "monitor_system_health",
      "policy": "automatic",  // ✅ Exécution immédiate
      "enabled": true
    },
    {
      "name": "create_backup",
      "policy": "ask",  // ⚠️ Demande confirmation
      "enabled": true
    }
  ]
}
```

---

## ⚙️ Activer/Désactiver/Modifier les Policies

### Fichier: `.continue/mcp-tools-config.json`

#### ✅ Désactiver un outil (sécurité)
```json
{
  "name": "execute_desktop_command",
  "policy": "disabled",
  "enabled": false
}
```

#### ⚠️ Passer en mode "ask" (demande confirmation)
```json
{
  "name": "monitor_system_health",
  "policy": "ask",
  "enabled": true
}
```

#### 🚀 Passer en mode "automatic" (PRUDENCE !)
```json
{
  "name": "create_backup",
  "policy": "automatic",  // ⚠️ Exécution automatique !
  "enabled": true
}
```

### Recharger la Configuration
Après modification du JSON :
```
Ctrl+Shift+P → "Continue: Reload Config"
```

---

## 🎮 Utilisation des Outils TwisterLab

### Dans Continue Chat
Syntaxe : `@mcp <tool_name> <json_arguments>`

#### Exemples
```
@mcp monitor_system_health {"include_docker": true, "threshold_cpu_percent": 80}

@mcp classify_ticket {"title": "Wi-Fi ne fonctionne pas", "description": "Impossible de se connecter"}

@mcp list_autonomous_agents

@mcp create_backup {"backup_type": "incremental", "targets": ["database"], "encryption": true}
```

### Via PowerShell (API REST)
```powershell
# Lister les agents
Invoke-WebRequest -Uri "http://192.168.0.30:8000/v1/mcp/tools/list_autonomous_agents" -UseBasicParsing

# Surveiller le système
Invoke-WebRequest -Uri "http://192.168.0.30:8000/v1/mcp/tools/monitor_system_health" `
  -Method POST -ContentType "application/json" `
  -Body '{"include_docker": true}'
```

---

## 🔒 Policies de Sécurité

| Policy | Icône | Comportement | Outils Actuels |
|--------|-------|--------------|----------------|
| **automatic** | ✅ | Exécution immédiate sans confirmation | monitor_system_health, sync_cache, classify_ticket, list_autonomous_agents |
| **ask** | ⚠️ | Demande confirmation avant exécution | create_backup, resolve_ticket, execute_desktop_command |
| **disabled** | ❌ | Outil désactivé, ne peut pas être utilisé | Aucun (modifiable dans le JSON) |

---

## 📊 Architecture MCP

```
┌─────────────────────────────────┐
│  VS Code + Continue Extension   │
│  - Built-in Tools (17)          │
│  - Chat Interface               │
└─────────────┬───────────────────┘
              │ MCP Protocol
              ▼
┌─────────────────────────────────┐
│  MCP Server (Python)            │
│  agents/mcp/                    │
│  mcp_server_continue_sync.py    │
└─────────────┬───────────────────┘
              │ HTTP REST
              ▼
┌─────────────────────────────────┐
│  TwisterLab API                 │
│  http://192.168.0.30:8000       │
│  - 7 Real Agents                │
│  - PostgreSQL + Redis           │
│  - Ollama LLM (CoreRTX)         │
└─────────────────────────────────┘
```

---

## 🧪 Tests Rapides

### Test 1: Lister les Agents
```powershell
Invoke-WebRequest -Uri "http://192.168.0.30:8000/v1/mcp/tools/list_autonomous_agents" -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json | Select-Object -ExpandProperty data | Select-Object -ExpandProperty agents | Format-Table name, mcp_tool, status
```

**Résultat attendu**:
```
name                         mcp_tool                  status
----                         --------                  ------
RealMonitoringAgent          monitor_system_health     operational
RealBackupAgent              create_backup             operational
RealSyncAgent                sync_cache                operational
RealClassifierAgent          classify_ticket           operational
RealResolverAgent            resolve_ticket            operational
RealDesktopCommanderAgent    execute_desktop_command   operational
RealMaestroAgent                                       operational
```

### Test 2: Monitor System Health
```
@mcp monitor_system_health {"include_docker": true}
```

### Test 3: Classify Ticket
```
@mcp classify_ticket {"title": "Imprimante bloquée", "description": "Erreur lors de l impression"}
```

---

## 📚 Documentation

| Document | Chemin | Taille | Description |
|----------|--------|--------|-------------|
| **Config JSON** | `.continue/mcp-tools-config.json` | 12.5 Ko | Configuration des 7 outils avec policies |
| **Tools Guide** | `.continue/MCP_TOOLS_GUIDE.md` | 8.1 Ko | Guide complet d'utilisation |
| **README** | `.continue/README.md` | 5.8 Ko | Quick reference visuel |
| **Config YAML** | `.continue/config.yaml` | 3.7 Ko | Configuration principale Continue |
| **API Docs** | http://192.168.0.30:8000/docs | - | Swagger UI interactive |
| **TwisterLab Guide** | `copilot-instructions.md` | - | Guide complet du projet |

---

## 🚨 Troubleshooting

### Outil ne répond pas dans Continue
1. Vérifier l'API : `curl http://192.168.0.30:8000/health`
2. Vérifier les logs : `ssh twister@192.168.0.30 "docker service logs twisterlab_api --tail 50"`
3. Recharger Continue : `Ctrl+Shift+P` → "Continue: Reload Config"

### Les outils TwisterLab n'apparaissent pas dans Continue
1. Vérifier que le MCP Server est démarré
2. Ouvrir les Developer Tools : `Ctrl+Shift+P` → "Developer: Toggle Developer Tools"
3. Chercher des erreurs dans la console
4. Vérifier le PYTHONPATH dans `.continue/config.yaml`

### Policy "ask" ne demande pas confirmation
1. Vérifier la version de Continue : doit être >= v0.8.0
2. Recharger la config : `Ctrl+Shift+P` → "Continue: Reload Config"
3. Vérifier que `"policy": "ask"` dans `.continue/mcp-tools-config.json`

### Commande whitelistée rejetée
1. Vérifier la whitelist dans `agents/real/real_desktop_commander_agent.py`
2. Ajouter la commande si nécessaire
3. Redéployer : `infrastructure/scripts/deploy.ps1 -Environment production`

---

## ✅ Résumé de la Configuration

### Status Actuel
- **API TwisterLab** : http://192.168.0.30:8000 ✅ Operational
- **Ollama LLM** : http://192.168.0.20:11434 ✅ Operational (CoreRTX)
- **Continue Extension** : ✅ Configured
- **MCP Server** : ✅ Running
- **Total Agents** : 7/7 ✅ Running

### Fichiers Créés
- ✅ `.continue/mcp-tools-config.json` (12.5 Ko)
- ✅ `.continue/MCP_TOOLS_GUIDE.md` (8.1 Ko)
- ✅ `.continue/README.md` (5.8 Ko)
- ✅ `.continue/config.yaml` (mis à jour)

### Prochaines Étapes
1. Ouvrir Continue dans VS Code (`Ctrl+Shift+P` → "Continue: Open")
2. Tester les outils avec `@mcp list_autonomous_agents`
3. Modifier les policies dans `.continue/mcp-tools-config.json` selon vos besoins
4. Recharger la config après modification

---

**Status** : ✅ Operational
**API** : http://192.168.0.30:8000
**Agents** : 7/7 running
**Version** : 1.0.1
**Date** : 2025-11-12
