# Configuration Continue IDE - TwisterLab

## État Actuel
 Configuration YAML valide et fonctionnelle
 6 modèles Ollama configurés avec rôles spécialisés
 1 serveur MCP TwisterLab opérationnel
 7 outils MCP auto-approuvés
 3 règles de développement intégrées
 API TwisterLab accessible (healthy)
 Tous les modèles Ollama disponibles

## Utilisation

### Chat
- **Qwen 3 (8B)** - Conversations générales et tâches d'agent
- Sélectionner dans la liste des modèles Continue

### Édition
- **DeepSeek R1** - Édition de code et raisonnement complexe
- Utiliser pour refactoring et modifications avancées

### Autocomplétion
- **CodeLlama** - Suggestions de code en temps réel
- Active automatiquement lors de la frappe

### MCP Tools
Utiliser la syntaxe @mcp dans le chat :
- @mcp list_autonomous_agents - Lister les agents
- @mcp monitor_system_health - Surveillance système
- @mcp create_backup - Sauvegarde
- @mcp sync_cache - Synchronisation cache
- @mcp classify_ticket - Classification tickets
- @mcp resolve_ticket - Résolution SOP
- @mcp execute_desktop_command - Commandes distantes

## Règles de Développement

Les règles TwisterLab sont automatiquement appliquées :

### Architecture
- Production-First : Solutions production-ready
- Real Infrastructure : Technologies déployées uniquement
- Security-Conscious : Pas d'exposition credentials
- Documentation-Driven : Type hints et docstrings requis

### Python Standards
- Imports absolus depuis la racine du projet
- Type hints obligatoires sur toutes les fonctions
- Async/await pour tous les agents
- Logging structuré avec contexte

### Agent Development
- Héritage de TwisterAgent obligatoire
- Méthode execute() async requise
- Outils au format OpenAI function calling
- Support multi-framework export

## Validation

Script de validation disponible :
`ash
python validate_final.py
`

Résultat attendu :
`
Configuration valide - 6 modeles, 1 MCP servers
Resultat: SUCCES
`

## Dépannage

### Modèles non visibles
1. Redémarrer VS Code complètement
2. Vérifier que Ollama fonctionne : curl http://192.168.0.20:11434/api/tags

### MCP tools non fonctionnels
1. Vérifier API : curl http://192.168.0.30:8000/health
2. Tester serveur MCP : python agents/mcp/mcp_server_continue_sync.py

### Erreur de parsing
1. Valider YAML : python -c "import yaml; yaml.safe_load(open('.continue/config.yaml'))"
2. Restaurer depuis backup si nécessaire

## Sauvegardes
- config.corrupted-*.yaml - Fichiers corrompus sauvegardés
- config.backup.json - Sauvegarde complète JSON
- config.simple.json - Version simplifiée

## Infrastructure

### Modèles IA
- **Ollama** : http://192.168.0.20:11434
- **API TwisterLab** : http://192.168.0.30:8000
- **GPU Support** : RTX 3060 pour accélération

### Agents Disponibles
1. RealMonitoringAgent - Surveillance système
2. RealBackupAgent - Sauvegarde PostgreSQL/Redis
3. RealSyncAgent - Synchronisation cache
4. RealClassifierAgent - Classification tickets
5. RealResolverAgent - Résolution SOP
6. RealDesktopCommanderAgent - Commandes système
7. RealMaestroAgent - Orchestration workflow

---
**Configuration validée et opérationnelle** 
**Date** : 14 novembre 2025
**Version** : YAML v1.0.2 + MCP v2.1.0
**Status** : Production Ready
