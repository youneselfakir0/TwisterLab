# Configuration Continue IDE - Format YAML

## 📋 Vue d'ensemble

Ce fichier `config.yaml` contient la configuration built-in de Continue IDE pour TwisterLab avec intégration MCP complète.

## 🎯 Fonctionnalités configurées

### 🤖 Modèles avec rôles spécialisés
- **Qwen 3 (8B)** - Rôle: `chat` - Optimisé pour les conversations et tâches d'agent
- **DeepSeek R1** - Rôle: `edit` - Spécialisé dans le raisonnement et l'édition de code
- **Llama 3.2 (1B)** - Modèle général léger
- **Llama 3 (8B)** - Modèle général performant
- **Qwen 3 VL** - Modèle multimodal
- **CodeLlama** - Autocomplétion de code

### 🔧 Serveur MCP TwisterLab
- **Nom**: TwisterLab MCP
- **Auto-approve**: `list_autonomous_agents`, `monitor_system_health`
- **API**: http://192.168.0.30:8000
- **Script**: `agents/mcp/mcp_server_continue_sync.py`

### 📊 Composants
- **Context Providers**: code, diff, terminal
- **Embeddings**: Llama 3.2 1B
- **Autocomplétion**: CodeLlama

## 🚀 Utilisation

1. **Redémarrer VS Code** pour charger la configuration YAML
2. **Ouvrir un fichier Python** dans TwisterLab
3. **Tester les fonctionnalités**:
   - Chat avec Qwen 3: conversations générales
   - Édition avec DeepSeek R1: modifications de code
   - MCP: `@mcp list_autonomous_agents`

## ✅ Validation

Utilisez le script de validation:
```bash
python validate_continue_yaml.py
```

## 🔄 Migration depuis JSON

Cette configuration YAML remplace avantageusement la configuration JSON complexe qui causait des erreurs de parsing. Elle utilise la syntaxe native YAML de Continue IDE.

## 📁 Structure des fichiers

```
.continue/
├── config.yaml          # Configuration principale (YAML)
├── config.json          # Configuration de secours (JSON)
├── config.backup.json   # Sauvegarde de l'ancienne config
├── mcp.json            # Configuration MCP séparée
└── prompts/            # Prompts personnalisés
```

## 🛠️ Dépannage

Si des problèmes surviennent:
1. Vérifier la syntaxe YAML avec `python validate_continue_yaml.py`
2. Consulter les logs VS Code (Console développeur)
3. Revenir à la configuration JSON si nécessaire

---
**Configuration validée et fonctionnelle** ✅
**Date**: 14 novembre 2025
**Version**: YAML Built-in + MCP v2.1.0
