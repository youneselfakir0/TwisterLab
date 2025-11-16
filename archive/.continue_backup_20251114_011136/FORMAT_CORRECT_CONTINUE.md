# Format MCP Continue - Correct et Validé

## ⚠️ Erreur Précédente

J'ai créé un fichier `mcp-tools-config.json` avec un format complexe qui n'est **PAS compatible** avec Continue. Continue est **très strict** sur le format.

### ❌ Format INCORRECT (supprimé)
```json
{
  "$schema": "https://docs.continue.dev/schemas/mcp-tools-config.json",
  "version": "1.0.0",
  "metadata": {
    "total_tools": 7,  // ❌ Continue n'accepte pas de metadata
    "enabled_tools": 7
  },
  "tools": [...] // ❌ Continue gère les tools automatiquement
}
```

**Erreur Continue** :
```
Failed to parse config: name: Required,
metadata.total_tools: Expected string, received number,
metadata.enabled_tools: Expected string, received number
```

---

## ✅ Format CORRECT Continue

Continue attend un format YAML **ultra-simple** pour les MCP servers :

### Dans `config.yaml`
```yaml
mcpServers:
  - name: "TwisterLab MCP"
    command: "python"
    args:
      - "agents/mcp/mcp_server_continue_sync.py"
    env:
      API_URL: "http://192.168.0.30:8000"
      PYTHONPATH: "C:\\TwisterLab"
    cwd: "C:\\TwisterLab"
    connectionTimeout: 10000
```

### OU dans `.continue/mcpServers/twisterlab-mcp.yaml`
```yaml
name: TwisterLab MCP
version: 1.0.1
schema: v1
mcpServers:
  - name: TwisterLab MCP
    command: python
    args:
      - agents/mcp/mcp_server_continue_sync.py
    env:
      API_URL: http://192.168.0.30:8000
      PYTHONPATH: C:\TwisterLab
    cwd: C:\TwisterLab
    connectionTimeout: 10000
```

---

## 📋 Champs Autorisés par Continue

### Champs REQUIS
- `name` : Nom du serveur MCP (string)
- `command` : Commande à exécuter (string)

### Champs OPTIONNELS
- `args` : Arguments de la commande (array of strings)
- `env` : Variables d'environnement (object with string values)
- `cwd` : Répertoire de travail (string)
- `connectionTimeout` : Timeout en ms (number)

### Champs INTERDITS
- ❌ `metadata` : Continue ne supporte PAS de metadata
- ❌ `tools` : Les tools sont détectés automatiquement par le serveur MCP
- ❌ `policies` : Les policies sont gérées par le serveur MCP, pas par Continue
- ❌ `$schema` : Pas de schema JSON dans YAML Continue
- ❌ `version` au niveau racine (sauf dans mcpServers/*.yaml)

---

## 🔧 Comment Continue Découvre les Outils

Continue ne lit **PAS** une config JSON des outils. Au lieu de cela :

1. **Continue démarre le serveur MCP** (via `command` et `args`)
2. **Le serveur MCP expose ses outils** via le protocole MCP
3. **Continue interroge le serveur** pour découvrir les outils disponibles
4. **Les outils apparaissent automatiquement** dans le menu Tools

```
┌─────────────────────────────────┐
│  Continue Extension (VS Code)   │
│  - Lit config.yaml              │
│  - Démarre serveur MCP          │
└─────────────┬───────────────────┘
              │ Lance: python agents/mcp/...
              ▼
┌─────────────────────────────────┐
│  MCP Server (Python)            │
│  - Expose outils via MCP        │
│  - Continue les découvre auto   │
└─────────────┬───────────────────┘
              │ HTTP REST
              ▼
┌─────────────────────────────────┐
│  TwisterLab API                 │
│  - 7 agents opérationnels       │
└─────────────────────────────────┘
```

---

## 🎯 Policies et Configuration des Outils

Les **policies** (automatic/ask/disabled) doivent être gérées dans :

1. **Le serveur MCP** (`agents/mcp/mcp_server_continue_sync.py`)
2. **L'API TwisterLab** (`api/routes_mcp_real.py`)

**PAS dans la config Continue !**

### Exemple dans le serveur MCP
```python
# Dans agents/mcp/mcp_server_continue_sync.py
TOOL_POLICIES = {
    "monitor_system_health": "automatic",
    "create_backup": "ask",
    "classify_ticket": "automatic",
    "resolve_ticket": "ask",
    "execute_desktop_command": "ask",
}

async def handle_tool_call(tool_name: str, args: dict):
    policy = TOOL_POLICIES.get(tool_name, "ask")

    if policy == "ask":
        # Demander confirmation à l'utilisateur
        confirmed = await ask_user_confirmation(tool_name, args)
        if not confirmed:
            return {"error": "User cancelled operation"}

    # Exécuter l'outil
    return await call_api(tool_name, args)
```

---

## 📁 Structure Corrigée

```
.continue/
├── config.yaml                      # ✅ Config principale (format simple)
├── mcpServers/
│   └── twisterlab-mcp.yaml         # ✅ MCP server config (optionnel)
├── MCP_TOOLS_GUIDE.md              # 📄 Documentation (pas lu par Continue)
├── README.md                        # 📄 Documentation (pas lu par Continue)
└── CONFIGURATION_COMPLETE.md       # 📄 Documentation (pas lu par Continue)
```

**Fichiers supprimés** :
- ❌ `mcp-tools-config.json` (format incompatible)

---

## ✅ Validation

### Test 1 : Vérifier le Format YAML
```powershell
Get-Content "c:\TwisterLab\.continue\config.yaml" | Select-String -Pattern "mcpServers" -Context 15
```

### Test 2 : Recharger Continue
```
Ctrl+Shift+P → "Continue: Reload Config"
```

### Test 3 : Vérifier les Erreurs
```
Ctrl+Shift+P → "Developer: Toggle Developer Tools"
```
→ Onglet "Console" → Chercher "MCP" ou "error"

### Test 4 : Lister les Outils
Continue devrait **automatiquement** découvrir les 7 outils TwisterLab au démarrage du serveur MCP.

---

## 🔍 Debugging

### Erreur "Failed to parse config"
- ✅ Vérifier que `config.yaml` est bien du YAML valide
- ✅ Pas de `metadata` avec des numbers
- ✅ Pas de champs interdits

### Outils ne s'affichent pas
- ✅ Vérifier que le serveur MCP démarre : logs dans Developer Tools
- ✅ Vérifier que l'API répond : `curl http://192.168.0.30:8000/health`
- ✅ Vérifier le PYTHONPATH dans `env`

### Serveur MCP crash
- ✅ Vérifier Python >= 3.10 : `python --version`
- ✅ Vérifier que `agents/mcp/mcp_server_continue_sync.py` existe
- ✅ Vérifier les logs : Developer Tools → Console

---

## 📚 Références Officielles Continue

- **MCP Documentation** : https://docs.continue.dev/reference/mcp
- **Config Schema** : https://docs.continue.dev/reference/config
- **YAML Format** : Format strict, pas de metadata complexe
- **Tools Discovery** : Automatique via protocole MCP

---

## ✅ Résumé

1. ❌ **Supprimé** : `mcp-tools-config.json` (format incompatible)
2. ✅ **Gardé** : `config.yaml` avec format simple
3. ✅ **Créé** : `mcpServers/twisterlab-mcp.yaml` (optionnel)
4. 📄 **Documentation** : Guides Markdown (pas lus par Continue)

**Continue découvrira automatiquement les outils du serveur MCP !**

---

**Status** : ✅ Format Corrigé
**Date** : 2025-11-12
**Leçon Apprise** : Continue est TRÈS strict sur le format YAML, pas de fantaisie !
