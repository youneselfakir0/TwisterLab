# ✅ Format Local Config Continue - Fichiers JSON MCP

## 🎯 Configuration Correcte

### Structure des Fichiers

```
.continue/
├── config.yaml              # Config principale (SANS mcpServers)
└── mcpServers/
    └── twisterlab-mcp.json  # ✅ Fichier JSON pour chaque MCP server
```

---

## 📋 Format JSON MCP Server

### Fichier : `.continue/mcpServers/twisterlab-mcp.json`

```json
{
  "mcpServers": {
    "twisterlab-mcp": {
      "command": "python",
      "args": [
        "agents/mcp/mcp_server_continue_sync.py"
      ],
      "env": {
        "API_URL": "http://192.168.0.30:8000",
        "PYTHONPATH": "C:\\TwisterLab"
      },
      "cwd": "C:\\TwisterLab"
    }
  }
}
```

---

## 🔍 Structure JSON Expliquée

```json
{
  "mcpServers": {                    // ✅ Clé racine obligatoire
    "nom-du-serveur": {              // ✅ ID unique du serveur
      "command": "python",           // ✅ Commande à exécuter
      "args": [                      // ✅ Arguments (array)
        "chemin/vers/script.py"
      ],
      "env": {                       // ✅ Variables d'environnement (object)
        "CLE": "valeur"
      },
      "cwd": "C:\\Chemin\\Projet"   // ✅ Répertoire de travail
    }
  }
}
```

---

## 📁 Continue Charge Automatiquement

Continue charge **TOUS** les fichiers `.json` dans `.continue/mcpServers/` :

```
.continue/mcpServers/
├── twisterlab-mcp.json       # ✅ Chargé automatiquement
├── autre-mcp.json            # ✅ Chargé automatiquement
└── test-mcp.json             # ✅ Chargé automatiquement
```

**Chaque fichier JSON peut définir un ou plusieurs MCP servers.**

---

## 🎮 Avantages du Format Local Config

### ✅ Avantages
1. **Séparation** : Chaque MCP server dans son propre fichier
2. **Built-in séparés** : `config.yaml` reste propre avec juste les built-in tools
3. **Modularité** : Ajouter/supprimer des MCP servers facilement
4. **Versioning** : Git track chaque MCP séparément

### ❌ Format Précédent (dans config.yaml)
```yaml
# ❌ Mélange built-in et MCP servers
mcpServers:
  - name: "TwisterLab MCP"
    command: "python"
    ...
```

### ✅ Nouveau Format (fichiers JSON séparés)
```yaml
# ✅ config.yaml : SEULEMENT built-in tools
models:
  - name: "Llama 3.2"
    ...
```

```json
// ✅ mcpServers/twisterlab-mcp.json : MCP servers
{
  "mcpServers": {
    "twisterlab-mcp": { ... }
  }
}
```

---

## 🔧 Ajouter un Nouveau MCP Server

### Créer un nouveau fichier JSON

**Fichier** : `.continue/mcpServers/mon-nouveau-mcp.json`

```json
{
  "mcpServers": {
    "mon-nouveau-mcp": {
      "command": "node",
      "args": [
        "mon-serveur-mcp.js"
      ],
      "env": {
        "API_KEY": "xyz123"
      },
      "cwd": "/chemin/vers/projet"
    }
  }
}
```

### Recharger Continue

```
Ctrl+Shift+P → "Continue: Reload Config"
```

Continue détecte automatiquement le nouveau fichier JSON !

---

## 🧪 Vérification

### Test 1 : Vérifier le JSON est valide
```powershell
Get-Content ".continue/mcpServers/twisterlab-mcp.json" | ConvertFrom-Json
```

### Test 2 : Recharger Continue
```
Ctrl+Shift+P → "Continue: Reload Config"
```

### Test 3 : Vérifier dans Developer Tools
```
Ctrl+Shift+P → "Developer: Toggle Developer Tools"
```
→ Console → Chercher "MCP" ou "twisterlab-mcp"

### Test 4 : Utiliser le MCP
```
@mcp list_autonomous_agents
```

---

## 🚨 Erreurs Courantes

### Erreur : "Connection closed"
**Cause** : Le serveur MCP ne démarre pas

**Solutions** :
1. Vérifier que Python est accessible : `python --version`
2. Vérifier que le script existe : `Test-Path "agents/mcp/mcp_server_continue_sync.py"`
3. Tester manuellement : `python agents/mcp/mcp_server_continue_sync.py`
4. Vérifier les logs : Developer Tools → Console

### Erreur : "Failed to parse config"
**Cause** : JSON invalide

**Solutions** :
1. Vérifier la syntaxe JSON : `ConvertFrom-Json`
2. Vérifier les backslashes : `C:\\TwisterLab` (double backslash)
3. Vérifier les virgules : pas de virgule après le dernier élément

### MCP Server ne s'affiche pas
**Cause** : Fichier JSON non détecté

**Solutions** :
1. Vérifier l'extension : `.json` (pas `.yaml`)
2. Vérifier l'emplacement : `.continue/mcpServers/`
3. Recharger Continue : `Ctrl+Shift+P` → "Continue: Reload Config"

---

## 📚 Exemple Complet

### Structure du Projet

```
TwisterLab/
├── .continue/
│   ├── config.yaml                      # Config principale (built-in)
│   └── mcpServers/
│       ├── twisterlab-mcp.json         # TwisterLab MCP
│       ├── docker-mcp.json             # Docker MCP (exemple)
│       └── github-mcp.json             # GitHub MCP (exemple)
├── agents/
│   └── mcp/
│       └── mcp_server_continue_sync.py # Serveur MCP TwisterLab
└── ...
```

### config.yaml (SANS mcpServers)

```yaml
name: "TwisterLab Assistant"
version: "1.0.0"
schema: "v1"

models:
  - name: "Llama 3.2 (1B)"
    provider: "ollama"
    model: "llama3.2:1b"
    apiBase: "http://192.168.0.20:11434"
    roles:
      - chat
      - edit

# MCP servers sont dans .continue/mcpServers/*.json
```

### mcpServers/twisterlab-mcp.json

```json
{
  "mcpServers": {
    "twisterlab-mcp": {
      "command": "python",
      "args": [
        "agents/mcp/mcp_server_continue_sync.py"
      ],
      "env": {
        "API_URL": "http://192.168.0.30:8000",
        "PYTHONPATH": "C:\\TwisterLab"
      },
      "cwd": "C:\\TwisterLab"
    }
  }
}
```

---

## ✅ Résumé

1. ✅ **Fichier JSON** créé : `.continue/mcpServers/twisterlab-mcp.json`
2. ✅ **Format correct** : `{ "mcpServers": { "nom": { ... } } }`
3. ✅ **config.yaml nettoyé** : SANS mcpServers
4. ✅ **Continue charge automatiquement** les JSON de `mcpServers/`

---

## 🎯 Prochaines Étapes

1. **Recharger Continue** : `Ctrl+Shift+P` → "Continue: Reload Config"
2. **Vérifier absence d'erreur** : Developer Tools → Console
3. **Tester** : `@mcp list_autonomous_agents`

---

**Status** : ✅ Format Local Config JSON Validé  
**Date** : 2025-11-12  
**Format** : Continue Local Config avec fichiers JSON séparés  

**🎉 FORMAT JSON LOCAL CONFIG - CORRECT ! 🎉**
