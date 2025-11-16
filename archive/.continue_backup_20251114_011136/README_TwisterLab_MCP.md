# TwisterLab MCP Integration pour Continue IDE

## Statut de Configuration

✅ **Configuration Continue IDE**: YAML valide avec name/version requis
✅ **Serveur MCP**: Configuré pour transport stdio
✅ **Endpoints API**: Vérifiés fonctionnels (200 OK)
✅ **Modèles**: Ollama GPU + Claude 3.5 configurés

## Utilisation

### Méthodes d'Accès MCP

1. **Via Continue IDE Interface**:
   - Ouvrir Continue Chat (Cmd/Ctrl + Shift + L)
   - Les outils MCP seront automatiquement disponibles

2. **Via Commandes Slash**:
   ```
   /tools - Lister tous les outils MCP disponibles
   /mcp - Accéder directement aux serveurs MCP
   ```

3. **Via Éditeur**:
   - Sélectionner du code
   - Utiliser "Edit with MCP" ou "Chat with MCP"

### Outils MCP Disponibles

- **MonitoringAgent**: Surveillance système (CPU/RAM/disk/Docker)
- **BackupAgent**: Sauvegardes automatisées
- **SyncAgent**: Synchronisation cache/base de données
- **ClassifierAgent**: Classification tickets
- **ResolverAgent**: Exécution SOP résolution
- **DesktopCommanderAgent**: Commandes système distantes

## Configuration Technique

### Serveur MCP
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

### Modèles Configurés
- **Ollama Llama3.2 (GPU RTX)**: http://192.168.0.20:11434
- **Claude 3.5 Sonnet**: Via Anthropic API

## Tests de Connectivité

### Vérifier Endpoints MCP
```bash
curl -X GET "http://192.168.0.30:8000/v1/mcp/tools"
curl -X POST "http://192.168.0.30:8000/v1/mcp/execute" \
  -H "Content-Type: application/json" \
  -d '{"tool": "monitoring", "parameters": {}}'
```

### Tester Configuration Continue
1. Ouvrir VS Code
2. Cmd/Ctrl + Shift + P → "Continue: Open Settings"
3. Vérifier que config.yaml se charge sans erreurs

## Dépannage

### Erreur "name: Required"
- ✅ **RÉSOLU**: Ajouté `name` et `version` dans config.yaml

### Erreur "models.0: Invalid input"
- ✅ **RÉSOLU**: Structure `models` corrigée selon docs Continue

### Serveur MCP non disponible
- Vérifier que `agents/mcp/mcp_server_continue_sync.py` existe
- Tester endpoint API: `curl http://192.168.0.30:8000/health`
- Vérifier PYTHONPATH dans configuration

### Modèles Ollama non accessibles
- Vérifier Ollama: `ollama list`
- Tester API: `curl http://192.168.0.20:11434/api/tags`

## Architecture

```
Continue IDE → MCP Client → TwisterLab API (192.168.0.30:8000)
                                      ↓
                               Real Agents (Docker Swarm)
                                      ↓
                            PostgreSQL + Redis + Ollama
```

## Sécurité

- **Isolation**: Agents s'exécutent dans containers séparés
- **Authentification**: Via API keys (non commitées)
- **Audit**: Toutes les actions loggées avec timestamps
- **Rate Limiting**: Implémenté au niveau API

## Support

Pour problèmes avec l'intégration MCP:
1. Vérifier logs Continue IDE
2. Tester endpoints API manuellement
3. Consulter `agents/mcp/mcp_server_continue_sync.py`
4. Vérifier configuration réseau Docker Swarm
