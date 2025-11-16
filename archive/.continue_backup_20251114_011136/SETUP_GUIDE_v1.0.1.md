# TwisterLab - Guide Configuration Continue IDE v1.0.1

**Date** : 2025-11-12
**Statut** : ✅ 6 modèles Ollama + Cloud gratuit + MCP activé

---

## 🎯 Résumé Configuration

**Continue IDE configuré avec** :
- ✅ **6 modèles Ollama locaux** (vs 4 avant)
- ✅ **1 modèle cloud gratuit** (GPT-OSS 120B)
- ✅ **MCP TwisterLab activé** (7 agents autonomes)
- ✅ **Context providers** (file, code, diff, terminal)
- ✅ **Roles configurés** (chat, edit, apply, autocomplete)

**Total** : 7 modèles gratuits + accès agents TwisterLab

---

## 🤖 Modèles Ollama Locaux (GRATUITS)

### 1. Llama 3.2 (1B) ⚡⚡⚡ ULTRA RAPIDE
```yaml
model: llama3.2:1b
taille: 1.3 GB
roles: chat, edit
température: 0.7
```
**Usage** :
- Chat rapide
- Questions simples
- Prototypage code
- Tests d'idées

**Commande** : `ollama pull llama3.2:1b`

---

### 2. Llama 3 (8B) ⚡⚡ RAPIDE
```yaml
model: llama3:latest
taille: 4.7 GB
roles: chat, edit, apply
température: 0.7
```
**Usage** :
- Conversations avancées
- Analyse générale
- Documentation
- Explications complexes

**Commande** : `ollama pull llama3`

---

### 3. DeepSeek R1 ⚡⚡ RAISONNEMENT
```yaml
model: deepseek-r1:latest
taille: 5.2 GB
roles: chat
température: 0.7
reasoning: true  ← MODE RAISONNEMENT
```
**Usage** :
- Analyses complexes
- Raisonnement multi-étapes
- Débogage difficile
- Architecture systèmes

**Commande** : `ollama pull deepseek-r1`

---

### 4. CodeLlama ⚡⚡ CODE GENERATION
```yaml
model: codellama:latest
taille: 3.8 GB
roles: chat, edit, autocomplete
température: 0.3
autocomplete: activé ← AUTOCOMPLÉTION
```
**Usage** :
- Génération code from scratch
- Autocomplétion (Tab)
- Snippets
- Boilerplate code

**Commande** : `ollama pull codellama`

---

### 5. Qwen 3 (8B) ⚡⚡ REFACTORING
```yaml
model: qwen3:8b
taille: 5.2 GB
roles: chat, edit, apply
température: 0.5
```
**Usage** :
- Refactoring code existant
- Optimisation performance
- Clean code
- Best practices

**Commande** : `ollama pull qwen3:8b`

---

### 6. GPT-OSS (120B Cloud) ☁️ GRATUIT
```yaml
model: gpt-oss:120b-cloud
taille: 384 bytes (cloud)
roles: chat, edit
température: 0.7
```
**Usage** :
- Tâches TRÈS complexes
- Modèle 120B gratuit via API Ollama
- Nécessite connexion internet
- Pas de limite gratuite connue

**Commande** : `ollama pull gpt-oss:120b-cloud`

**Note** : Ce modèle utilise l'API cloud Ollama GRATUITE (pas de coût)

---

## 🔧 MCP TwisterLab (Agents Autonomes)

**Configuration** :
```yaml
mcpServers:
  - name: "TwisterLab MCP"
    command: "python"
    args: ["agents/mcp/mcp_server_continue_sync.py"]
    env:
      API_URL: "http://192.168.0.30:8000"
```

**Agents disponibles** :
1. **MonitoringAgent** - Santé système (CPU/RAM/Disk)
2. **ClassifierAgent** - Classification tickets (90% confidence)
3. **ResolverAgent** - Résolution avec SOP
4. **DesktopCommanderAgent** - Exécution commandes distantes
5. **MaestroOrchestratorAgent** - Orchestration workflows
6. **SyncAgent** - Synchronisation cache/DB
7. **BackupAgent** - Backups automatiques

**Usage dans Continue** :
```
@mcp monitor_system_health
@mcp classify_ticket "Le serveur web ne répond plus"
@mcp resolve_ticket ticket_id=123
```

---

## 📊 Workflows Recommandés

### Génération Code Rapide
1. **Ctrl+L** → Ouvrir chat Continue
2. Sélectionner **CodeLlama**
3. Demander génération code
4. Tab pour autocomplétion

### Refactoring Code Existant
1. Sélectionner code dans éditeur
2. **Ctrl+I** → Continue Edit
3. Choisir **Qwen 3 (8B)**
4. Demander refactoring/optimisation

### Analyse Complexe
1. **Ctrl+L** → Chat
2. Sélectionner **DeepSeek R1**
3. Poser question complexe
4. Mode reasoning activé automatiquement

### Tâche Ultra Complexe (Cloud)
1. **Ctrl+L** → Chat
2. Sélectionner **GPT-OSS (120B Cloud)**
3. Nécessite connexion internet
4. Modèle 120B gratuit

### Chat Rapide
1. **Ctrl+L** → Chat
2. Sélectionner **Llama 3.2 (1B)**
3. Réponse instantanée
4. Parfait prototypage

### Monitoring TwisterLab
1. **Ctrl+L** → Chat
2. Taper `@mcp monitor_system_health`
3. Résultat : CPU/RAM/Disk en temps réel

---

## 🎮 Raccourcis Continue

| Raccourci | Action | Modèle recommandé |
|-----------|--------|-------------------|
| `Ctrl+L` | Chat Continue | Llama 3.2 (rapide) |
| `Ctrl+I` | Edit inline | Qwen 3 (refactor) |
| `Tab` | Autocomplétion | CodeLlama |
| `Ctrl+Shift+P` → "Continue" | Commandes | - |

---

## 💡 Comparaison Outils AI

### Continue IDE (Ollama Local)
- ✅ 100% gratuit
- ✅ Privacy totale
- ✅ Offline
- ✅ 6 modèles locaux
- ✅ 1 modèle cloud gratuit
- ✅ MCP TwisterLab
- ❌ Modèles moins puissants que Claude 3.5

### GitHub Copilot (Payant mais vous avez accès)
- ✅ Claude 3.5 Sonnet
- ✅ Suggestions inline excellentes
- ✅ Chat intégré VS Code
- ❌ Nécessite licence (vous l'avez)
- ❌ Pas privacy (code envoyé GitHub)

### Claude Desktop Free
- ✅ Gratuit
- ✅ Claude 3.5 Sonnet
- ✅ Excellent pour brainstorming
- ❌ Pas intégré Continue
- ❌ Standalone uniquement

**Recommandation** :
1. **Continue** → Développement quotidien (gratuit, privacy)
2. **Copilot** → Autocomplétion premium (Claude 3.5)
3. **Claude Desktop** → Brainstorming architecture

---

## 🚀 Installation Modèles Manquants

Si un modèle n'apparaît pas dans Continue :

```powershell
# Installer tous les modèles configurés
ollama pull llama3.2:1b
ollama pull llama3:latest
ollama pull deepseek-r1:latest
ollama pull codellama:latest
ollama pull qwen3:8b
ollama pull gpt-oss:120b-cloud

# Vérifier installation
ollama list

# Redémarrer VS Code
# Ctrl+Shift+P → "Reload Window"
```

---

## 🔍 Vérification Configuration

### Test modèles Ollama
```powershell
curl http://localhost:11434/api/tags | ConvertFrom-Json | Select -ExpandProperty models
```

### Test MCP TwisterLab
```powershell
# Démarrer serveur MCP manuellement
python agents/mcp/mcp_server_continue_sync.py

# Doit afficher:
# INFO - MCP Server Starting: twisterlab-mcp-continue
# INFO - Protocol: MCP 2024-11-05
```

### Test API TwisterLab
```powershell
curl http://192.168.0.30:8000/health
# → {"status":"healthy","version":"1.0.0"}

curl http://192.168.0.30:8000/api/v1/autonomous/agents
# → Liste 7 agents
```

---

## ❌ Troubleshooting

### Erreur "MCP error -32000: Connection closed"
✅ **RÉSOLU** - MCP maintenant dans `config.yaml` (pas `mcp.json` séparé)

### Modèles n'apparaissent pas dans Continue
```powershell
# 1. Vérifier modèles installés
ollama list

# 2. Vérifier syntaxe config.yaml
# model: "llama3:latest"  ← Correct
# model: "llama3"         ← Mauvais (manque :latest)

# 3. Redémarrer VS Code
# Ctrl+Shift+P → "Reload Window"
```

### GPT-OSS cloud ne fonctionne pas
```powershell
# Vérifier connexion internet
ping 8.8.8.8

# Vérifier modèle installé
ollama list | Select-String "gpt-oss"

# Tester manuellement
ollama run gpt-oss:120b-cloud "Hello"
```

### MCP TwisterLab timeout
```powershell
# Vérifier API accessible
curl http://192.168.0.30:8000/health

# Augmenter timeout dans config.yaml:
# connectionTimeout: 30000  # 30 secondes
```

---

## 📦 Fichiers Configuration

```
.continue/
├── config.yaml                      # ← Configuration principale
├── SETUP_GUIDE_v1.0.1.md           # ← Ce guide
├── README_MCP_TROUBLESHOOTING.md   # ← Debug MCP
└── config.edgeserver.yaml          # ← Config Linux (edgeserver)
```

**Fichier principal** : `.continue/config.yaml`
- 6 modèles Ollama locaux
- 1 modèle cloud gratuit
- MCP TwisterLab
- Context providers
- Rules personnalisées

---

## 🎯 Prochaines Étapes

1. **Redémarrer VS Code** : `Ctrl+Shift+P` → "Reload Window"
2. **Tester Continue** : `Ctrl+L` → Sélectionner modèle
3. **Installer modèles manquants** : `ollama pull <model>`
4. **Tester MCP** : `@mcp monitor_system_health`
5. **Profiter** : 7 modèles gratuits + MCP + privacy ! 🎉

---

## 📚 Ressources

- **Continue Docs** : https://docs.continue.dev/reference
- **Ollama Models** : https://ollama.com/library
- **TwisterLab API** : http://192.168.0.30:8000/docs
- **MCP Protocol** : https://modelcontextprotocol.io

---

**Version** : 1.0.1
**Dernière mise à jour** : 2025-11-12
**Statut** : ✅ Production ready
