# 📋 Guide d'utilisation des LLM dans Continue IDE

## Modèles configurés pour TwisterLab

### 1. **Llama3.2 Fast (Available)** - `llama3.2:1b`
- **Usage** : Chat rapide, questions simples
- **Points forts** : Très rapide, faible utilisation mémoire
- **⚠️ Limite** : PAS adapté aux agents (modèle trop léger - 1B paramètres)
- **Quand l'utiliser** : Questions basiques, tests rapides

### 2. **Qwen 3 (8B) - Agent Compatible** - `qwen3:8b`
- **Usage** : ✅ **RECOMMANDÉ pour les agents TwisterLab**
- **Points forts** : Tâches complexes, raisonnement, génération de code
- **Capacités** : Excellente pour les workflows d'agent, compréhension contextuelle
- **Quand l'utiliser** : Toutes les tâches avec les agents MCP TwisterLab

### 3. **DeepSeek R1 - Reasoning Agent** - `deepseek-r1:latest`
- **Usage** : Raisonnement avancé, analyse complexe
- **Points forts** : Réflexion approfondie, résolution de problèmes complexes
- **Capacités** : Excellente pour les tâches de diagnostic et d'analyse
- **Quand l'utiliser** : Troubleshooting, analyse système, planification complexe

### 4. **CodeLlama - Code Agent** - `codellama:latest`
- **Usage** : Génération et compréhension de code
- **Points forts** : Autocomplétion intelligente, refactoring
- **Capacités** : Compréhension fine du code, génération de qualité
- **Quand l'utiliser** : Développement, debugging, optimisation code

## 🚀 Comment utiliser les agents avec le bon modèle

### Dans Continue IDE :
1. **Sélectionner le modèle** : Cliquez sur l'icône du modèle en bas à gauche
2. **Choisir "Qwen 3 (8B) - Agent Compatible"** pour les agents
3. **Utiliser les outils MCP** :
   ```
   @mcp twisterlab_mcp_list_autonomous_agents
   @mcp monitor_system_health
   @mcp create_backup
   ```

### Exemple de prompt d'agent :
```
Utilise le modèle Qwen 3 (8B) pour analyser le système TwisterLab :

@mcp monitor_system_health

Analyse les métriques et propose des optimisations.
```

## 📥 Installation des modèles

Si les modèles ne sont pas disponibles, exécutez :

```powershell
# Sur CoreRTX (192.168.0.20) ou edgeserver (192.168.0.30)
.\download_ollama_models.ps1
```

Ou manuellement :
```bash
ollama pull qwen3:8b
ollama pull deepseek-r1:latest
ollama pull codellama:latest
```

## ⚡ Recommandations

- **Pour les agents TwisterLab** : Utilisez toujours **Qwen 3 (8B)**
- **Pour le développement** : **CodeLlama** pour l'autocomplétion
- **Pour l'analyse** : **DeepSeek R1** pour le raisonnement complexe
- **Pour les tests** : **Llama3.2** pour les questions rapides

## 🔧 Dépannage

Si un modèle n'est pas disponible :
1. Vérifiez qu'Ollama fonctionne : `ollama list`
2. Téléchargez le modèle : `ollama pull <nom-modele>`
3. Redémarrez Continue IDE
4. Sélectionnez le modèle dans l'interface

---
**Version** : 1.0.0
**Dernière mise à jour** : 2025-11-14
