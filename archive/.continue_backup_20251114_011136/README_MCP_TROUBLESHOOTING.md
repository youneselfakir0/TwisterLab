# MCP Server Troubleshooting - Continue IDE

## Problème Rencontré

```
Failed to connect to "New MCP server"
Error: MCP error -32000: Connection closed
```

## Cause

Continue IDE essaie de charger `mcp.json` mais le serveur MCP n'est pas correctement configuré ou ne démarre pas.

## Solutions

### Solution 1 : DÉSACTIVER MCP (Recommandé pour l'instant)

**Avantages** :
- ✅ Continue fonctionne immédiatement avec Ollama local
- ✅ Pas de configuration complexe
- ✅ Ollama suffit pour la plupart des tâches

**Action** :
```powershell
# Renommer mcp.json pour le désactiver
Rename-Item .continue\mcp.json .continue\mcp.json.disabled
```

**Résultat** :
- Continue utilise uniquement les 4 modèles Ollama configurés
- Pas d'erreur MCP au démarrage
- Réactiver plus tard si besoin

---

### Solution 2 : ACTIVER MCP (Configuration avancée)

**Prérequis** :
- ✅ Serveur MCP fonctionne : `python agents/mcp/mcp_server_continue_sync.py`
- ✅ API TwisterLab accessible : http://192.168.0.30:8000
- ✅ Package `httpx` installé : `pip install httpx`

**Configuration** :

1. **Vérifier que le serveur démarre** :
```powershell
# Test manuel
python agents/mcp/mcp_server_continue_sync.py
# Doit afficher:
# INFO - MCP Server Starting: twisterlab-mcp-continue
# INFO - Protocol: MCP 2024-11-05
```

2. **Activer mcp.json** :
```powershell
# Si désactivé, réactiver
Rename-Item .continue\mcp.json.disabled .continue\mcp.json
```

3. **Redémarrer Continue IDE** :
   - `Ctrl+Shift+P` → "Reload Window"
   - Ou redémarrer VS Code

**Vérification** :
```powershell
# Tester les outils MCP via API
curl http://192.168.0.30:8000/v1/mcp/tools/list_autonomous_agents

# Doit retourner la liste des 7 agents
```

---

## Configuration Actuelle

### mcp.json (Désactivé)
```json
{
  "mcpServers": {
    "twisterlab-mcp": {
      "command": "python",
      "args": ["agents/mcp/mcp_server_continue_sync.py"],
      "env": {
        "API_URL": "http://192.168.0.30:8000",
        "PYTHONPATH": "C:\\TwisterLab"
      }
    }
  }
}
```

### config.yaml (Actif)
- 4 modèles Ollama locaux configurés
- Pas de référence MCP
- Fonctionne sans erreur

---

## Recommandation

**Pour l'instant : DÉSACTIVER MCP**

Raisons :
1. **Continue fonctionne parfaitement avec Ollama local**
   - Llama 3.2 : Chat rapide
   - DeepSeek R1 : Analyses complexes
   - CodeLlama : Génération code
   - Qwen 2.5 : Refactoring

2. **MCP est optionnel**
   - Permet d'appeler agents TwisterLab depuis Continue
   - Utile pour workflows avancés
   - Pas nécessaire pour développement quotidien

3. **GitHub Copilot suffit pour autocomplétion**
   - Claude 3.5 Sonnet intégré VS Code
   - Suggestions contextuelles

**Activer MCP plus tard si besoin** :
- Quand vous voulez intégrer agents TwisterLab dans Continue
- Pour workflows nécessitant classification/résolution automatique
- Pour accès direct aux agents autonomes depuis l'IDE

---

## Outils MCP Disponibles (si activé)

1. **list_autonomous_agents** - Liste les 7 agents autonomes
2. **monitor_system_health** - Santé système (CPU/RAM/Disk)
3. **classify_ticket** - Classification LLM (90% confidence)
4. **resolve_ticket** - Résolution avec SOP
5. **execute_desktop_command** - Commandes distantes
6. **backup_system** - Backup automatique
7. **sync_cache** - Synchronisation Redis/PostgreSQL

**Usage exemple** (si MCP activé) :
```
@twisterlab-mcp monitor_system_health
@twisterlab-mcp classify_ticket "Le serveur web ne répond plus"
```

---

## État Actuel

- ✅ **mcp.json.disabled** - MCP désactivé
- ✅ **config.yaml** - 4 modèles Ollama actifs
- ✅ **Continue IDE** - Fonctionne sans erreur
- ✅ **Serveur MCP** - Prêt si besoin (testé OK)

**Prochaine étape** : Utiliser Continue avec Ollama, activer MCP si besoin plus tard.
