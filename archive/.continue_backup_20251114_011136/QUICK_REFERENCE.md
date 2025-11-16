# 🚀 Continue IDE - Guide Rapide TwisterLab

**Version**: 1.0.0 | **Date**: 2025-11-12 | **GPU**: RTX 3060 (CoreRTX)

---

## 📋 Custom Commands (Sélection Automatique LLM)

| Commande | LLM Utilisé | Usage | Exemple |
|----------|-------------|-------|---------|
| `/quick` | Llama 3.2 (1B) | Question rapide | `/quick Quelle commande Docker Swarm?` |
| `/explain` | Llama 3 (8B) | Explication détaillée | `/explain Comment fonctionne asyncio?` |
| `/reason` | DeepSeek R1 | Analyse complexe | `/reason Dois-je utiliser Redis ou PostgreSQL?` |
| `/code` | CodeLlama | Génération code | `/code Crée un agent de backup` |
| `/refactor` | Qwen 3 (8B) | Refactoring | `/refactor Optimise cette fonction` |
| `/research` | GPT-OSS (120B) | Recherche avancée | `/research Patterns multi-agent AI` |

---

## 🤖 Slash Commands MCP (Agents TwisterLab)

| Commande | Description | Exemple |
|----------|-------------|---------|
| `/agents` | Liste 7 agents autonomes | `/agents` |
| `/classify` | Classifier ticket IT | `/classify Erreur PostgreSQL connection refused` |
| `/resolve` | Générer SOP résolution | `/resolve Redis cache timeout` |
| `/monitor` | État santé système | `/monitor` |

---

## 🎯 Sélection Manuelle des LLM

**Dans le chat Continue** (Ctrl+L) :

1. 🚀 **Llama 3.2 (1B)** - Ultra Rapide (~2s)
   - Questions simples
   - Réponses concises
   - Chat basique

2. 💬 **Llama 3 (8B)** - Chat Expert (~5s)
   - Explications détaillées
   - Documentation
   - Tutoriels

3. 🧠 **DeepSeek R1** - Raisonnement Complexe (~8s)
   - Architecture système
   - Analyse approfondie
   - Planification

4. 💻 **CodeLlama** - Génération Code (~4s)
   - Code production-ready
   - Type hints + docstrings
   - Tests pytest

5. 🔧 **Qwen 3 (8B)** - Refactoring Expert (~5s)
   - Optimisation code
   - Code review
   - Best practices

6. ☁️ **GPT-OSS (120B)** - Cloud Power (~15s)
   - Recherche avancée
   - Raisonnement multi-étapes
   - Problèmes complexes

---

## 📊 Matrice de Performance

| LLM | Tokens/s | Temps Réponse | VRAM | Usage Optimal |
|-----|----------|---------------|------|---------------|
| Llama 3.2 (1B) | 50-60 | ~2s | 1.5 GB | Questions rapides |
| Llama 3 (8B) | 30-40 | ~5s | 6 GB | Explications |
| DeepSeek R1 | 20-30 | ~8s | 8 GB | Analyse |
| CodeLlama | 35-45 | ~4s | 5 GB | Code |
| Qwen 3 (8B) | 30-40 | ~5s | 6 GB | Refactoring |
| GPT-OSS (120B) | 10-15 | ~15s | 12 GB | Recherche |

---

## 🛠️ Configuration Système

```yaml
Infrastructure:
  CoreRTX: 192.168.0.20
    - GPU: RTX 3060 (12GB VRAM)
    - Ollama: http://192.168.0.20:11434
    - Models: 6 actifs
  
  Edgeserver: 192.168.0.30
    - API: http://192.168.0.30:8000
    - PostgreSQL: 16
    - Redis: 7
    - Docker Swarm: 6 services

Continue IDE:
  Config: C:\Users\Administrator\.continue\config.json
  MCP Server: agents/mcp/mcp_server_continue_sync.py
  Tools: 7 auto-approved
  Rules: 13 guidelines TwisterLab
```

---

## ✅ Vérification Rapide

```powershell
# Test Ollama GPU
curl http://192.168.0.20:11434/api/tags | ConvertFrom-Json | Select -ExpandProperty models | Select name

# Test API TwisterLab
curl http://192.168.0.30:8000/health

# Test MCP Server (local)
python agents/mcp/mcp_server_continue_sync.py

# Vérifier config Continue
cat C:\Users\Administrator\.continue\config.json | jq '.models[].title'
```

---

## 🎯 Workflows Recommandés

### 1️⃣ Développement Rapide
```
1. /code Crée un nouvel agent
2. CodeLlama génère le code
3. /refactor Optimise le code
4. Qwen 3 améliore
5. pytest tests/ -v
```

### 2️⃣ Analyse Système
```
1. /reason Analyse architecture
2. DeepSeek R1 évalue
3. /explain Explique décisions
4. Llama 3 documente
```

### 3️⃣ Debugging
```
1. /monitor État système
2. MCP récupère métriques
3. /classify Identifie problème
4. /resolve Génère solution
```

---

## 🚨 Troubleshooting

**MCP Connection Failed** :
```powershell
# Vérifier PYTHONPATH
python -c "import sys; print(sys.path)"

# Test manuel MCP server
python agents/mcp/mcp_server_continue_sync.py

# Check logs
tail -f mcp_server.log
```

**Ollama Inaccessible** :
```powershell
# Vérifier service
curl http://192.168.0.20:11434/api/tags

# Firewall Windows CoreRTX
netsh advfirewall firewall show rule name="Ollama API"

# Restart Ollama
ssh coreserver@192.168.0.20 "systemctl restart ollama"
```

**Model Not Found** :
```powershell
# Lister modèles disponibles
curl http://192.168.0.20:11434/api/tags

# Télécharger nouveau modèle
ssh coreserver@192.168.0.20 "ollama pull mistral:7b"

# Ajouter dans config.json
```

---

## 📚 Références

- **API TwisterLab** : http://192.168.0.30:8000/docs
- **Ollama API** : http://192.168.0.20:11434
- **MCP Server** : `agents/mcp/mcp_server_continue_sync.py`
- **Guidelines** : `copilot-instructions.md`
- **Architecture** : `README.md`

---

**Quick Start** : `Ctrl+L` → Tapez votre question → Continue sélectionne automatiquement le bon LLM ! 🚀
