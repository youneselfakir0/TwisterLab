# Getting Started (Draft) - Consolidated from archive

This is a mechanical draft combining several archived quick-start files. Please review and edit to produce the final `docs/GETTING_STARTED.md`.

---

## Source: CONTINUE_IDE_GUIDE.md

# 🎯 Guide Continue IDE - TwisterLab

## ✅ Configuration Validée

La configuration Continue IDE pour TwisterLab est maintenant **complètement opérationnelle** !

### 📊 État de la Configuration

- ✅ **6 modèles Ollama** configurés (Llama 3.2 1B → GPT-OSS 120B)
- ✅ **1 serveur MCP** actif (TwisterLab MCP v2.1.0)
- ✅ **7 outils MCP** auto-approuvés
- ✅ **15 règles** unifiées pour développement TwisterLab
- ✅ **6 prompts spécialisés** pour tâches courantes
- ✅ **API TwisterLab** connectée et fonctionnelle

### 🚀 Utilisation Immédiate

#### 1. Redémarrage VS Code
```bash
# Fermer et rouvrir VS Code pour charger la nouvelle configuration
```

#### 2. Test des Outils MCP
Ouvrir un fichier Python dans TwisterLab et tester :

```bash
# Lister les 7 agents autonomes
@mcp list_autonomous_agents

# Vérifier l'état système (CPU, RAM, Disk, Docker)
@mcp monitor_system_health

# Classifier un ticket IT
@mcp classify_ticket "Mon ordinateur ne démarre plus"

# Résoudre un problème réseau
@mcp resolve_ticket "Connexion internet lente" "network" "WiFi se déconnecte régulièrement"
```

#### 3. Utilisation des Prompts Spécialisés
```bash
# Développement d'agents
@prompt agent-development

# Diagnostic système
@prompt troubleshoot-system

# Debug MCP
@prompt debug-mcp

# Optimisation PC
@prompt optimize-pc
```

#### 4. Commandes Personnalisées
```bash
# Question rapide (Llama 3.2 1B)
/quick Comment créer un nouvel agent TwisterLab ?

# Explication détaillée (Llama 3 8B)
/explain Architecture des 7 agents autonomes

# Analyse complexe (DeepSeek R1)
/reason Comment optimiser les performances du système ?

# Génération code (CodeLlama)
/code Créer une classe RealNewAgent héritant de TwisterAgent

# Refactoring (Qwen 3 8B)
/refactor Améliorer cette fonction async
```

### 🎯 Raccourcis Recommandés

#### Développement Agent
1. `@prompt agent-development` - Guide complet création agent
2. `/code` - Générer code avec type hints et docstrings
3. `@mcp list_autonomous_agents` - Voir agents existants

#### Debugging
1. `@prompt debug-mcp` - Diagnostiquer problèmes MCP
2. `@mcp monitor_system_health` - État système temps réel
3. `@prompt troubleshoot-system` - Diagnostic complet

#### Production
1. `@prompt optimize-pc` - Nettoyage et optimisation
2. `@mcp create_backup` - Sauvegarde système
3. `@mcp sync_cache` - Synchronisation Redis/PostgreSQL

### 🔧 Architecture TwisterLab dans Continue

#### 7 Agents Réels
- **RealMonitoringAgent** - Surveillance système (CPU/RAM/Disk/Docker)
- **RealBackupAgent** - Sauvegardes PostgreSQL/Redis/config
- **RealSyncAgent** - Synchronisation cache/base
- **RealClassifierAgent** - Classification tickets IT (LLM)
- **RealResolverAgent** - Résolution SOP automatique
- **RealDesktopCommanderAgent** - Commandes système distantes
- **RealMaestroAgent** - Orchestration et load balancing

#### Infrastructure
- **API FastAPI** : http://192.168.0.30:8000
- **Ollama GPU** : http://192.168.0.20:11434 (RTX 3060)
- **PostgreSQL** : Port 5432
- **Redis** : Port 6379
- **Prometheus** : Port 9090 (métriques)
- **Grafana** : Port 3000 (dashboards)

### 📋 Checklist Utilisation

- [x] Configuration Continue validée
- [x] Serveur MCP opérationnel
- [x] API TwisterLab accessible
- [ ] VS Code redémarré
- [ ] Premier test @mcp list_autonomous_agents
- [ ] Premier test @mcp monitor_system_health
- [ ] Prompt agent-development testé

### 🎉 Prêt pour la Production !

Continue IDE est maintenant parfaitement configuré pour le développement TwisterLab avec :
- **IA spécialisée** pour chaque type de tâche
- **Outils MCP intégrés** pour interagir avec les agents réels
- **Règles unifiées** garantissant la qualité du code
- **Prompts spécialisés** pour accélérer le développement

**Commencez par tester `@mcp list_autonomous_agents` ! 🚀**


---

## Source: CONTINUE_MCP_GUIDE.md

# 🚀 Continue + TwisterLab MCP - Guide d'Utilisation

## ✅ Installation Complète

Le serveur MCP TwisterLab est maintenant configuré pour Continue IDE !

**Fichiers créés** :
- `agents/mcp/mcp_server_continue_sync.py` - Serveur MCP pour Continue
- `test_mcp_sync.py` - Tests de validation
- `c:\Users\Administrator\.continue\config.json` - Configuration Continue

---

## 🎯 Utilisation dans Continue

### **1. Redémarrer VS Code**
```
Ctrl+Shift+P → Developer: Reload Window
```

### **2. Ouvrir Continue Chat**
```
Ctrl+L
```

### **3. Utiliser les MCP Tools**

#### **Option A : Via mentions @**
```
@twisterlab classify this ticket: Cannot connect to WiFi eduroam
```

#### **Option B : Via commands**
```
Use the classify_ticket MCP tool to classify: "Printer not working"
```

#### **Option C : Via custom commands**
```
Ctrl+L → Dans le menu → Sélectionner "Classify Ticket"
```

---

## 🔧 MCP Tools Disponibles

### **1. classify_ticket**
Classifie un ticket IT helpdesk

**Exemple** :
```
@twisterlab classify: "Cannot access shared drive Z:"
```

**Résultat** :
```json
{
  "status": "success",
  "category": "network",
  "confidence": 0.85,
  "agent": "RealClassifierAgent"
}
```

---

### **2. resolve_ticket**
Obtient les étapes de résolution depuis la base SOP

**Exemple** :
```
@twisterlab resolve ticket category=network description="WiFi keeps disconnecting"
```

**Résultat** :
```json
{
  "status": "success",
  "resolution_steps": [
    "Step 1: Verify network issue symptoms",
    "Step 2: Check network configuration",
    "Step 3: Apply standard network troubleshooting",
    "Step 4: Escalate if unresolved"
  ],
  "estimated_time": "15-30 minutes"
}
```

---

### **3. monitor_system_health**
Vérifie la santé du système TwisterLab

**Exemple** :
```
@twisterlab check system health
```

**Résultat** :
```json
{
  "status": "warning",
  "services": {
    "postgres": "running",
    "redis": "running",
    "api": "down (0/1 replicas)",
    "ollama": "running"
  }
}
```

---

### **4. create_backup**
Crée une sauvegarde de la base de données/config

**Exemple** :
```
@twisterlab create full backup
```

**Résultat** :
```json
{
  "status": "success",
  "backup_location": "/backups/backup_20251111.tar.gz",
  "agent": "RealBackupAgent"
}
```

---

## 📚 MCP Resources Disponibles

### **1. twisterlab://system/health**
Status système en temps réel

**Utilisation** :
```
Read resource: twisterlab://system/health
```

### **2. twisterlab://agents/status**
Status de tous les agents

**Utilisation** :
```
Read resource: twisterlab://agents/status
```

---

## 🧪 Tests Locaux

### **Test rapide du serveur MCP** :
```powershell
cd C:\TwisterLab
python test_mcp_sync.py
```

**Output attendu** :
```
✅ ALL TESTS PASSED

TEST: classify_ticket
→ category: network, confidence: 0.85

TEST: monitor_system_health
→ status: warning, api: down
```

### **Test manuel du serveur** :
```powershell
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python agents/mcp/mcp_server_continue_sync.py
```

---

## ⚠️ Mode Actuel : MOCK

**Important** : Le serveur MCP retourne actuellement des **réponses simulées** car l'API TwisterLab est offline (0/1 replicas).

**Toutes les réponses incluent** :
```json
{
  "note": "⚠️ Mock response - API service offline"
}
```

**Quand l'API sera online** :
1. Le serveur MCP appellera les **vrais agents** (RealClassifierAgent, etc.)
2. Les réponses viendront de **Ollama LLM** (classification réelle)
3. Les données viendront de **PostgreSQL** (SOPs, historique)

---

## 🔄 Différence avec GitHub Copilot

| Feature | GitHub Copilot (toi) | Continue + MCP |
|---------|---------------------|----------------|
| **Agents** | ❌ Pas d'accès | ✅ Appelle agents TwisterLab |
| **LLM** | GPT-4 (cloud) | Llama 3.2 1B (local) |
| **Classification** | Simulée | **Vraie** (via RealClassifierAgent) |
| **Résolution** | Générique | **SOPs réels** (base de données) |
| **Monitoring** | N/A | **Système réel** (Docker, PostgreSQL) |
| **Backup** | N/A | **Vraies sauvegardes** (RealBackupAgent) |

---

## 🚀 Prochaines Étapes

### **1. Fixer l'API Service** (priorité haute)
```powershell
# Rebuild image avec dépendances
docker build -f infrastructure/dockerfiles/Dockerfile.api -t twisterlab/api:v1.0.1 .

# Copier vers edgeserver
docker save twisterlab/api:v1.0.1 | ssh twister@192.168.0.30 docker load

# Redéployer
ssh twister@192.168.0.30 "docker stack deploy -c docker-compose.yml twisterlab"
```

### **2. Remplacer MOCK par Agents Réels**
Modifier `mcp_server_continue_sync.py` pour appeler les agents via l'API REST :
```python
# Remplacer mock responses par :
import requests
response = requests.post(
    "http://192.168.0.30:8000/v1/mcp/tools/call",
    json={"tool": "classify_ticket", "arguments": arguments}
)
```

### **3. Tester l'Intégration Complète**
```
Continue → MCP Server → API REST → Real Agents → Ollama LLM
```

---

## � Dépannage - Erreurs Courantes

### **Erreur "Connection refused"**
Si vous obtenez `[Errno 111] Connection refused` :

1. **Vérifiez que le serveur MCP fonctionne** :
   ```bash
   python agents/mcp/mcp_server_continue_sync.py
   ```

2. **Testez la connectivité** :
   ```bash
   curl -X POST http://127.0.0.1:8000 \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
   ```

3. **Redémarrez VS Code** :
   ```
   Ctrl+Shift+P → Developer: Reload Window
   ```

### **Erreur "Duplicate tools/rules"**
Si Continue signale des doublons :

1. **Videz le cache Continue** :
   ```bash
   rm -rf ~/.continue/cache/
   rm -rf ~/.continue/sessions/
   rm -rf ~/.continue/index/
   ```

2. **Redémarrez VS Code**

### **MCP Tools non visibles**
Si les outils MCP n'apparaissent pas :

1. **Vérifiez la configuration** :
   ```bash
   cat ~/.continue/config.yaml
   ```

2. **Testez le serveur MCP** :
   ```bash
   python test_mcp_sync.py
   ```

3. **Redémarrez VS Code**

---

## �📖 Documentation Complète

- **MCP Protocol** : `MCP_INTEGRATION_GUIDE.md`
- **Projet TwisterLab** : `copilot-instructions.md`
- **API REST** : `API_DOCUMENTATION.md`
- **Changelog** : `CHANGELOG.md`

---

**Version** : 1.0.0
**Date** : 2025-11-11
**Status** : ✅ MCP Server opérationnel (mode MOCK)
**Next** : Fixer API service → Passer en mode REAL


---

## Source: GITHUB_SETUP.md

# TwisterLab GitHub Setup Instructions

## 🚀 Phase 1: Create GitHub Repository

### Step 1: Create Repository on GitHub
1. Go to https://github.com/new
2. Repository name: `twisterlab`
3. Owner: `youneselfakir0`
4. Make it **PUBLIC**
5. **DO NOT** initialize with README, .gitignore, or license
6. Click "Create repository"

### Step 2: Copy Repository URL
- Copy the HTTPS URL: `https://github.com/youneselfakir0/twisterlab.git`

### Step 3: Push Local Repository to GitHub

#### Option A: Automated Script (Recommended)
```bash
cd twisterlab-repo
python setup_github.py
```

#### Option B: Manual Commands
```bash
cd twisterlab-repo

# Add remote origin
git remote add origin https://github.com/youneselfakir0/twisterlab.git

# Push to GitHub
git push -u origin master

# Verify
git remote -v
```

### Step 4: Verify Setup
1. Visit: https://github.com/youneselfakir0/twisterlab
2. Check that all files are uploaded
3. Verify GitHub Actions are running (should auto-start)
4. Check the README renders correctly

## 🔧 Troubleshooting

### If Push Fails
```bash
# Check git status
git status

# If you need to authenticate
git config --global user.name "Younes El Fakir"
git config --global user.email "youneselfakir@outlook.com"

# Try push again
git push -u origin master
```

### If GitHub Actions Don't Run
1. Go to repository Settings → Actions → General
2. Under "Actions permissions", select "Allow all actions and reusable workflows"
3. Click Save

### If Tests Fail
- Check the Actions tab for error details
- Fix any issues in the code
- Commit and push fixes

## ✅ Phase 1 Checkpoint Validation

After successful push, verify:

- [ ] Repository is public and accessible
- [ ] All files uploaded (13 files total)
- [ ] README renders correctly
- [ ] GitHub Actions running (green checks)
- [ ] No security alerts
- [ ] Branch protection can be configured

## 🎯 Next Steps

Once Phase 1 is complete:
1. **Generate Phase 2 Prompt** (Grafana Optimization)
2. **Configure branch protection** (main/develop)
3. **Setup project boards** for tracking
4. **Begin Phase 2** (Grafana dashboards)

## 📞 Support

If you encounter issues:
- Check GitHub documentation
- Review error messages carefully
- Contact: youneselfakir@outlook.com

---

**Status**: Ready for GitHub deployment 🚀

---

## Source: LLM_GUIDE_CONTINUE_IDE.md

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


---

## Source: QUICK_START.md

# 🚀 GUIDE RAPIDE - QUELLE COMMANDE UTILISER ?

## Situation 1: Le service est cassé et je veux juste réparer

**Commande**:
```powershell
.\fix_database_config.ps1
```

**Durée**: 15-20 minutes
**Risque**: Faible (backup automatique créé)
**Résultat**: Service avec agents réels fonctionnels

---

## Situation 2: Le fix a échoué, je veux revenir en arrière

**Commande**:
```powershell
.\rollback_service.ps1
```

**Options**:
- Option 1: Rollback automatique Swarm
- Option 2: Version `real-agents-final`
- Option 3: Version `production-real-agents-20251111-024958`

---

## Situation 3: Je veux juste vérifier l'état actuel

**Commandes**:
```powershell
# Status du service
ssh twister@192.168.0.30 "docker service ps twisterlab_api"

# Logs récents
ssh twister@192.168.0.30 "docker service logs twisterlab_api --tail 50"

# Test API
Invoke-RestMethod -Uri "http://192.168.0.30:8000/health"
```

---

## Situation 4: Je veux tester les agents réels

**Commandes**:
```powershell
# Test MonitoringAgent
$body = @{ operation = "health_check" } | ConvertTo-Json
Invoke-RestMethod `
  -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents/MonitoringAgent/execute" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"

# Test BackupAgent
$body = @{ operation = "status" } | ConvertTo-Json
Invoke-RestMethod `
  -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents/BackupAgent/execute" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"
```

---

## Situation 5: Je veux exécuter les tests d'intégration

**Commande**:
```powershell
python C:\TwisterLab\tests\test_integration_real_agents.py
```

---

## Arbre de décision visuel

```
┌─────────────────────────────────┐
│ Le service fonctionne-t-il ?    │
└────────────┬────────────────────┘
             │
      ┌──────┴──────┐
      │             │
     OUI           NON
      │             │
      │        ┌────┴────────────────────┐
      │        │ API répond /health ?     │
      │        └─────┬──────────────────┘
      │              │
      │        ┌─────┴─────┐
      │       OUI         NON
      │        │           │
      │        │      fix_database_config.ps1
      │        │           │
      │   Données       ┌──┴──┐
      │   réelles?    SUCCESS  FAIL
      │        │           │     │
      │    ┌───┴───┐      OK    rollback_service.ps1
      │   OUI     NON
      │    │       │
      │   OK   Vérifier
      │        orchestrator
      │
  Tests
  d'intégration
```

---

## Le problème exact et sa solution

**Problème identifié**:
```python
# File: /app/agents/database/config.py (ligne 22)
engine = create_async_engine(DATABASE_URL)  # ❌ psycopg2 (sync) with async engine
```

**Solution**:
```python
# Change DATABASE_URL from:
postgresql+psycopg2://user:pass@host/db

# To:
postgresql+asyncpg://user:pass@host/db
```

**Pourquoi ça plante**:
- `create_async_engine()` nécessite un driver asynchrone
- `psycopg2` est synchrone
- `asyncpg` est asynchrone ✅

**Ce que fait le script fix_database_config.ps1**:
1. Backup de config.py → config.py.backup
2. `sed -i 's/postgresql+psycopg2/postgresql+asyncpg/g' config.py`
3. Rebuild l'image Docker avec le fix
4. Déploie la nouvelle image
5. Teste que tout fonctionne

---

## Fichiers créés cette session

| Fichier | Description | Usage |
|---------|-------------|-------|
| `fix_database_config.ps1` | Fix le problème async driver | **EXÉCUTER EN PREMIER** |
| `rollback_service.ps1` | Revenir en arrière si échec | Si fix échoue |
| `RAPPORT_FINAL_SESSION_2025-11-11.md` | Rapport détaillé | Documentation |
| `QUICK_START.md` | Ce fichier | Référence rapide |

---

## Images Docker disponibles

| Image | Status | Notes |
|-------|--------|-------|
| `production-real-agents-20251111-024958` | ✅ READY | Toutes dépendances, mais config DB à fixer |
| `production-asyncpg-XXXXXXXX-XXXXXX` | 🔄 SERA CRÉÉ | Après exécution fix_database_config.ps1 |
| `real-agents-final` | ⚠️ ANCIEN | Version précédente (avant ce fix) |
| `with-real-agents` | ⚠️ ANCIEN | Version test |

---

## Commandes utiles

```powershell
# Rebuild manuel si besoin
ssh twister@192.168.0.30 "cd /home/twister/TwisterLab && docker build -f Dockerfile.production -t twisterlab-api:manual-fix ."

# Déployer une image spécifique
ssh twister@192.168.0.30 "docker service update --image twisterlab-api:TAG twisterlab_api"

# Voir toutes les images
ssh twister@192.168.0.30 "docker images | grep twisterlab-api"

# Supprimer images anciennes
ssh twister@192.168.0.30 "docker image prune -f"

# Logs en temps réel
ssh twister@192.168.0.30 "docker service logs -f twisterlab_api"

# Redémarrer le service (dernier recours)
ssh twister@192.168.0.30 "docker service update --force twisterlab_api"
```

---

## FAQ

**Q: Combien de temps prend le fix ?**
A: 15-20 minutes (5 min build + 2 min deploy + 3 min tests)

**Q: Y a-t-il un risque de casser le système ?**
A: Non. Un backup automatique est créé et rollback disponible.

**Q: Que faire si le fix échoue ?**
A: Exécuter `.\rollback_service.ps1` pour revenir en arrière.

**Q: Comment vérifier que les agents sont bien réels ?**
A: Tester MonitoringAgent - le CPU ne doit PAS être "23%" (c'était la valeur mock).

**Q: Est-ce que je peux continuer à utiliser l'ancien service ?**
A: Oui, avec rollback_service.ps1 option 2 ou 3. Mais il retournera des données mock.

---

## 🎯 Action recommandée MAINTENANT

```powershell
# 1. Exécuter le fix (15-20 minutes)
.\fix_database_config.ps1

# 2. Si succès, tester
Invoke-RestMethod -Uri "http://192.168.0.30:8000/health"

# 3. Vérifier données réelles
$body = @{ operation = "health_check" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents/MonitoringAgent/execute" -Method POST -Body $body -ContentType "application/json"

# 4. Exécuter tests d'intégration
python C:\TwisterLab\tests\test_integration_real_agents.py
```

**Résultat attendu**: 100% completion avec agents réels fonctionnels 🚀

---

**Status actuel**: 97% complete
**Blocage**: 1 ligne dans database/config.py
**Solution**: Exécuter fix_database_config.ps1
**Temps estimé**: 15-20 minutes
**Difficulté**: ⭐☆☆☆☆ (très simple)


---

## Source: QUICKSTART.md

# TwisterLab v1.0 - Guide de Démarrage Rapide

**Démarrez TwisterLab en 5 minutes** ⏱️

---

## 📋 Prérequis

- ✅ Docker Desktop installé et en cours d'exécution
- ✅ Python 3.12+ installé
- ✅ Git installé

---

## 🚀 Démarrage Rapide (5 étapes)

### 1. Cloner le projet (si pas déjà fait)

```bash
cd C:\TwisterLab
```

### 2. Créer et activer l'environnement virtuel

```bash
# Créer l'environnement
python -m venv .venv_new

# Activer (Windows PowerShell)
.\.venv_new\Scripts\Activate.ps1

# Ou (Windows CMD)
.\.venv_new\Scripts\activate.bat

# Ou (Git Bash/Linux)
source .venv_new/bin/activate
```

### 3. Installer les dépendances

```bash
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary pydantic python-dotenv requests typer rich
```

### 4. Démarrer PostgreSQL

```bash
docker-compose up -d postgres

# Vérifier que ça tourne
docker ps
# Vous devriez voir: twisterlab-postgres (healthy)
```

### 5. Démarrer l'API

```bash
uvicorn agents.api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## ✅ Vérifier que tout fonctionne

### Option 1: Test avec le script Python (Recommandé)

**Ouvrir un nouveau terminal** et lancer:

```bash
cd C:\TwisterLab
.\.venv_new\Scripts\Activate.ps1
python test_sops_api.py
```

**Résultat attendu**: 7 tests passent avec succès ✅

### Option 2: Test manuel avec curl

```bash
# Health check
curl http://localhost:8000/api/v1/sops/hello

# Créer une SOP
curl -X POST http://localhost:8000/api/v1/sops/ ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Test SOP\",\"description\":\"Test\",\"category\":\"password\",\"steps\":[\"Step 1\"],\"applicable_issues\":[\"test\"]}"

# Lister les SOPs
curl http://localhost:8000/api/v1/sops/
```

### Option 3: Test dans le navigateur

Ouvrez votre navigateur et allez sur:

- **Documentation API interactive**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/api/v1/sops/hello

---

## 📚 Accès aux services

| Service | URL | Credentials |
|---------|-----|-------------|
| **API FastAPI** | http://localhost:8000 | - |
| **API Docs (Swagger)** | http://localhost:8000/docs | - |
| **PostgreSQL** | localhost:5432 | User: twisterlab, DB: twisterlab_db |

---

## 🔍 Vérifier PostgreSQL directement (Optionnel)

```bash
# Se connecter à PostgreSQL
docker exec -it twisterlab-postgres psql -U twisterlab -d twisterlab_db

# Dans psql:
# Lister les tables
\dt

# Voir les SOPs créées
SELECT * FROM sops;

# Quitter
\q
```

---

## 🛠️ Commandes utiles

### Arrêter/Redémarrer

```bash
# Arrêter l'API
# Ctrl+C dans le terminal de uvicorn

# Arrêter PostgreSQL
docker-compose stop postgres

# Redémarrer PostgreSQL
docker-compose start postgres

# Tout arrêter
docker-compose down
```

### Voir les logs

```bash
# Logs PostgreSQL
docker logs twisterlab-postgres

# Logs API
# Les logs s'affichent directement dans le terminal uvicorn
```

### Réinitialiser la base de données

```bash
# Supprimer les données (⚠️ ATTENTION: supprime toutes les données)
docker-compose down -v

# Recréer
docker-compose up -d postgres

# Réappliquer les migrations
alembic upgrade head
```

---

## 🧪 Tester avec Postman/Insomnia

Importez cette collection:

**Endpoint**: `http://localhost:8000/api/v1/sops/`

**Exemple POST (Créer SOP)**:
```json
{
  "title": "Software Installation",
  "description": "Standard procedure for installing software",
  "category": "software",
  "steps": [
    "1. Download installer",
    "2. Run as administrator",
    "3. Follow installation wizard",
    "4. Restart computer"
  ],
  "applicable_issues": ["software_install", "new_software"],
  "estimated_time": 10,
  "success_rate": 0.95,
  "tags": ["software", "installation"]
}
```

---

## 📖 Documentation Complète

- **Documentation master**: `.github/copilot-instructions.md`
- **État du projet**: `STATUS.md`
- **Schémas agents**: `docs/AGENT_SCHEMA.md`
- **Scripts automation**: `deployment/scripts/`

---

## 🆘 Dépannage

### Problème: "Cannot connect to API"

**Solution**:
1. Vérifiez que uvicorn est lancé: `uvicorn agents.api.main:app --reload`
2. Vérifiez le port 8000: `netstat -ano | findstr :8000`
3. Essayez un autre port: `uvicorn agents.api.main:app --port 8001 --reload`

### Problème: "Connection refused to PostgreSQL"

**Solution**:
1. Vérifiez que Docker tourne: `docker ps`
2. Vérifiez le conteneur: `docker ps | findstr postgres`
3. Redémarrez: `docker-compose restart postgres`
4. Vérifiez les logs: `docker logs twisterlab-postgres`

### Problème: "Module not found"

**Solution**:
1. Vérifiez l'environnement virtuel est activé: `where python` (doit pointer vers .venv_new)
2. Réinstallez les dépendances: `pip install -r requirements.txt`
3. Vérifiez Python 3.12+: `python --version`

### Problème: "Alembic migration error"

**Solution**:
1. Vérifiez la connexion DB: `alembic current`
2. Réappliquez: `alembic downgrade base` puis `alembic upgrade head`
3. Vérifiez alembic.ini pointe vers la bonne DB

---

## 🎯 Prochaines étapes

Une fois que tout fonctionne, vous pouvez:

1. **Option A**: Implémenter l'authentification JWT/OAuth2
2. **Option B**: Intégrer les agents MCP + orchestration
3. **Option C**: Créer un frontend React/Vue
4. **Option D**: Ajouter tests automatisés (pytest)
5. **Option E**: Préparer le déploiement production

**Voir**: `STATUS.md` pour détails sur chaque option

---

## ✨ Commandes CLI TwisterLab

```bash
# Lister les agents disponibles
python cli/twisterlab.py list-agents

# Exporter un agent au format Microsoft
python cli/twisterlab.py export-agent helpdesk-resolver

# Exporter vers un fichier
python cli/twisterlab.py export-agent classifier --output agent.json

# Voir détails d'un agent
python cli/twisterlab.py show-agent desktop-commander

# Valider un schéma
python cli/twisterlab.py validate-schema config/agent_schemas/helpdesk_resolver.json

# Voir les formats supportés
python cli/twisterlab.py formats
```

---

## 🎉 Félicitations !

Vous avez maintenant TwisterLab v1.0 opérationnel avec:

- ✅ PostgreSQL + SQLAlchemy
- ✅ API FastAPI avec CRUD complet
- ✅ Migrations Alembic
- ✅ Scripts de test
- ✅ CLI riche
- ✅ Documentation complète

**Prêt pour la production !** 🚀

---

**Besoin d'aide ?** Consultez:
- `STATUS.md` - État du projet et prochaines étapes
- `.github/copilot-instructions.md` - Documentation complète
- `docs/AGENT_SCHEMA.md` - Guide des schémas agents


---

## Source: QUICKSTART_AGENT_IMPLEMENTATION.md

# 🚀 QUICK START: Implementing 6 Remaining Agents

## ⚡ FAST TRACK (5 Hours Total)

### **Step 1: Open Claude (5 minutes)**

1. In VS Code: `Ctrl+Shift+P`
2. Type: "Claude: Open"
3. Open file: `CLAUDE_STRATEGIC_PROMPT.md`
4. Copy entire content
5. Paste into Claude chat
6. Wait for detailed plan (~3-5 minutes)
7. **Save Claude's response** to a file: `CLAUDE_AGENT_PLANS.md`

### **Step 2: Implement with Copilot (4 hours)**

For EACH of the 6 agents:

#### A. Open Copilot Chat
```
Ctrl+I (or click Copilot icon)
```

#### B. Provide Context
```
I need to implement [AgentName] based on this plan:

[PASTE SECTION FROM CLAUDE'S PLAN FOR THIS AGENT]

Also reference:
- COPILOT_TACTICAL_PROMPT.md (instructions)
- agents/helpdesk/classifier.py (working example)
- agents/base.py (base class)
```

#### C. Request Implementation
```
Please implement [AgentName]Agent following the pattern from ClassifierAgent.
Include:
1. Agent class in agents/{category}/{agent_name}.py
2. Tests in tests/test_{agent_name}.py
3. Integration guide in agents/{category}/{agent_name}_integration.md

Follow TwisterLab conventions from .github/copilot-instructions.md
```

#### D. Test
```powershell
pytest tests/test_{agent_name}.py -v
```

#### E. Commit
```powershell
git add .
git commit -m "Implement {AgentName}Agent"
git push origin main
```

#### F. Repeat for Next Agent
Go to B with next agent from list

---

## 📋 AGENT IMPLEMENTATION ORDER

1. ✅ **ClassifierAgent** - DONE (already implemented)
2. ⏳ **ResolverAgent** - NEXT (30 min)
3. ⏳ **Desktop-CommanderAgent** (25 min)
4. ⏳ **MaestroOrchestratorAgent** (40 min)
5. ⏳ **Sync-AgentAgent** (20 min)
6. ⏳ **Backup-AgentAgent** (20 min)
7. ⏳ **Monitoring-AgentAgent** (25 min)

**Total: ~2.5 hours implementation + 1.5 hours testing = 4 hours**

---

## 🎯 CHECKLIST FOR EACH AGENT

Before moving to next agent:

- [ ] Agent file created
- [ ] Tests created
- [ ] Integration guide written
- [ ] Tests passing (`pytest tests/test_{agent_name}.py -v`)
- [ ] Coverage > 80% (`pytest --cov=agents.{category}.{agent_name}`)
- [ ] Health check working
- [ ] Committed to Git
- [ ] Pushed to GitHub

---

## 💻 TERMINAL COMMANDS REFERENCE

```powershell
# Activate environment
.venv\Scripts\Activate.ps1

# Run specific agent tests
pytest tests/test_resolver.py -v

# Run all tests
pytest tests/ -v

# Check coverage
pytest --cov=agents --cov-report=html

# Start API server
python start_api_server.py

# Commit changes
git add .
git commit -m "Implement ResolverAgent"
git push origin main
```

---

## 🔥 RAPID IMPLEMENTATION TIPS

### For Claude:
- ✅ Ask for complete code blocks (not snippets)
- ✅ Request error handling patterns
- ✅ Ask for test examples
- ✅ Get integration specifications

### For Copilot:
- ✅ Reference ClassifierAgent explicitly
- ✅ Request tests immediately after code
- ✅ Ask to follow .github/copilot-instructions.md
- ✅ Provide Claude's plan as context

### For You:
- ✅ Test immediately after implementation
- ✅ Don't fix everything - commit working code
- ✅ Move to next agent quickly
- ✅ Refine later if needed

---

## ⏱️ TIMELINE

```
09:00 - 09:05   Open Claude, paste prompt
09:05 - 09:10   Claude generates plans
09:10 - 09:40   Implement ResolverAgent
09:40 - 09:45   Test & commit
09:45 - 10:10   Implement Desktop-CommanderAgent
10:10 - 10:15   Test & commit
10:15 - 10:55   Implement MaestroOrchestratorAgent
10:55 - 11:00   Test & commit
11:00 - 11:20   Implement Sync-AgentAgent
11:20 - 11:25   Test & commit
11:25 - 11:45   Implement Backup-AgentAgent
11:45 - 11:50   Test & commit
11:50 - 12:15   Implement Monitoring-AgentAgent
12:15 - 12:20   Test & commit
12:20 - 12:30   Final integration test
12:30 - 13:00   Celebration! 🎉
```

**6 Agents done in 4 hours!** ⚡

---

## 🎊 AFTER COMPLETION

When all 6 agents are done:

```powershell
# Run full test suite
pytest tests/ -v --cov=agents --cov-report=html

# Deploy to Docker
docker-compose up -d

# Verify all endpoints
curl http://localhost:8000/health

# Check agent status
curl http://localhost:8000/api/v1/agents

# Celebrate! 🎉
```

---

## 📞 HELP & REFERENCES

- **Stuck?** Check `agents/helpdesk/classifier.py` for working example
- **Error?** Copy error to Copilot and ask for fix
- **Pattern?** Reference `.github/copilot-instructions.md`
- **Integration?** See `agents/api/main.py` for API patterns

---

**LET'S BUILD! START WITH STEP 1!** 🚀


---

## Source: START_HERE.md

# 🚀 TwisterLab - Guide de Démarrage Rapide

## Bienvenue dans TwisterLab !

**TwisterLab** est un système d'automatisation IT Helpdesk multi-agent utilisant FastAPI, PostgreSQL et le protocole MCP.

---

## ⚡ Démarrage en 5 Minutes

### 1. Vérifier l'Environnement
```bash
# Vérifier Python 3.12+
python --version

# Vérifier que vous êtes dans le bon répertoire
pwd  # Doit afficher le chemin vers TwisterLab
```

### 2. Installer les Dépendances
```bash
pip install -r requirements.txt
```

### 3. Lancer les Tests Automatisés
```bash
# Utiliser le script d'automatisation (recommandé)
.\run_all_tests.ps1

# Ou manuellement
pytest tests/unit/ -v
pytest test_maestro_integration.py -v
```

### 4. Démarrer l'API
```bash
# 🚀 SOLUTION RECOMMANDÉE : Utiliser Docker
docker-compose up api -d

# Vérifier que l'API fonctionne
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

**⚠️ Note**: Si Docker n'est pas disponible, l'API peut avoir des problèmes de démarrage dans certains environnements Windows/PowerShell. Docker garantit un environnement isolé et stable.

### 5. Créer un Ticket de Test
```bash
# Avec curl
curl -X POST "http://localhost:8000/api/v1/tickets/" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test ticket",
    "description": "Test de l'\''orchestrateur Maestro",
    "requestor_email": "test@example.com"
  }'

# Avec PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/tickets/" `
  -Method POST -ContentType "application/json" `
  -Body '{"subject": "Test ticket", "description": "Test de l''orchestrateur Maestro", "requestor_email": "test@example.com"}'
```

---

## 🏗️ Architecture du Système

### Composants Principaux
```
TwisterLab/
├── agents/                          # Agents AI spécialisés
│   ├── base.py                     # Classe de base TwisterAgent
│   ├── orchestrator/maestro.py     # Orchestrateur principal
│   └── helpdesk/                   # Agents métier
│       ├── classifier.py           # Classification des tickets
│       ├── auto_resolver.py        # Résolution automatique
│       └── desktop_commander.py    # Commandes à distance
├── agents/api/                     # API REST FastAPI
│   ├── main.py                     # Application principale
│   └── routes_*.py                 # Endpoints API
├── agents/database/                # Persistance des données
│   ├── models.py                   # Modèles SQLAlchemy
│   ├── config.py                   # Configuration PostgreSQL
│   └── services.py                 # Services CRUD
├── tests/                          # Tests automatisés
│   ├── unit/                       # Tests unitaires (19 tests)
│   └── integration/                # Tests d'intégration (6 tests)
└── deployment/                     # Déploiement production
    ├── docker/                     # Conteneurs Docker
    └── scripts/                    # Scripts PowerShell Azure
```

### Flux de Traitement des Tickets
1. **Réception** → Ticket soumis via API
2. **Classification** → Agent Classifier évalue priorité/complexité
3. **Routage** → Maestro Orchestrator décide du chemin
4. **Traitement** → Agent spécialisé traite le ticket
5. **Résolution** → Réponse finale au demandeur

---

## 📋 Endpoints API Disponibles

### Tickets
```http
POST   /api/v1/tickets/          # Créer un ticket
GET    /api/v1/tickets/          # Lister les tickets
GET    /api/v1/tickets/{id}      # Détails d'un ticket
PUT    /api/v1/tickets/{id}      # Mettre à jour un ticket
DELETE /api/v1/tickets/{id}      # Supprimer un ticket
```

### Agents
```http
GET    /api/v1/agents/           # Liste des agents
GET    /api/v1/agents/{name}     # Détails d'un agent
POST   /api/v1/agents/{name}/execute  # Exécuter un agent
```

### Orchestrateur
```http
POST   /api/v1/orchestrator/route # Router un ticket
GET    /api/v1/orchestrator/status # Status des agents
POST   /api/v1/orchestrator/rebalance # Rééquilibrer la charge
```

### Système
```http
GET    /health                   # Health check
GET    /metrics                  # Métriques système
GET    /docs                     # Documentation Swagger UI
```

---

## 🧪 Tests Disponibles

### Tests Unitaires (19 tests)
- `test_maestro.py` - Orchestrateur Maestro
  - Routage des tickets
  - Gestion des agents
  - Métriques de performance
  - Rebalancing de charge

### Tests d'Intégration (6 tests)
- `test_maestro_integration.py` - Flux complet
  - Création → Classification → Routage → Résolution
  - Gestion d'erreurs
  - Performance sous charge

### Exécution des Tests
```bash
# Tous les tests
pytest

# Tests unitaires seulement
pytest tests/unit/

# Tests d'intégration seulement
pytest test_maestro_integration.py

# Avec coverage
pytest --cov=agents --cov-report=html
```

---

## 🔧 Dépannage

### Erreur: ModuleNotFoundError
```bash
# Installer les dépendances manquantes
pip install -r requirements.txt

# Vérifier l'installation
python -c "import fastapi, uvicorn, sqlalchemy, asyncpg"
```

### Erreur: Port 8000 déjà utilisé
```bash
# Tuer les processus sur le port
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Ou utiliser un autre port
uvicorn agents.api.main:app --port 8001
```

### Erreur: Base de données PostgreSQL
```bash
# Vérifier Docker
docker ps

# Redémarrer les services
docker-compose down
docker-compose up -d

# Attendre 10 secondes puis vérifier
alembic current
```

### Erreur: Tests échouent
```bash
# Vérifier la structure des répertoires
ls -la tests/

# Recréer l'environnement virtuel si nécessaire
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## 📊 Métriques et Monitoring

### Métriques Clés
- **Coverage Tests**: > 80%
- **Temps de Réponse API**: < 500ms
- **Taux de Résolution Auto**: > 70%
- **Disponibilité**: 99.9%

### Commandes de Monitoring
```bash
# Métriques API
curl http://localhost:8000/metrics

# Status des agents
curl http://localhost:8000/api/v1/agents/status

# Health check
curl http://localhost:8000/health

# Logs en temps réel
tail -f logs/twisterlab.log
```

---

## 🚀 Prochaines Étapes

Après ce guide de démarrage rapide :

1. **Phase 2** (En cours)
   - ✅ Installation dépendances
   - 🔄 Exécution des tests
   - ⏳ Test API REST
   - ⏳ Documentation technique
   - ⏳ Implémentation Desktop Commander

2. **Phase 3**: Interfaces utilisateur
3. **Phase 4**: Déploiement production
4. **Phase 5**: Optimisation et scaling

### Utiliser GitHub Copilot
Pour continuer le développement :
```bash
# Ouvrir le prompt détaillé
code .github/copilot-prompt-next-steps.md

# Copier le contenu dans Copilot Chat
# Suivre les instructions étape par étape
```

---

## 📞 Support

- **Documentation**: `.github/copilot-prompt-next-steps.md`
- **Tests**: `run_all_tests.ps1`
- **API**: `http://localhost:8000/docs`
- **Logs**: `logs/twisterlab.log`

**Version**: 1.0.0-alpha.1
**Date**: 28 octobre 2025
```

**Tests d'intégration**:
```bash
python test_maestro_integration.py
```

#### 4. Démarrer l'API

```bash
uvicorn agents.api.main:app --reload --port 8000
```

Ouvrir dans le navigateur: http://localhost:8000/docs

---

## 📚 Documentation

### Fichiers Importants

| Fichier | Description |
|---------|-------------|
| [.github/copilot-prompt-next-steps.md](.github/copilot-prompt-next-steps.md) | **PROMPT COMPLET pour GitHub Copilot** avec les 5 prochaines étapes à implémenter |
| [.github/copilot-instructions.md](.github/copilot-instructions.md) | Instructions complètes du projet (1200+ lignes) |
| [test_maestro_integration.py](test_maestro_integration.py) | Tests d'intégration (6 tests) |
| [tests/unit/test_maestro.py](tests/unit/test_maestro.py) | Tests unitaires pytest (19 tests) |
| [requirements.txt](requirements.txt) | Dépendances Python |

### Architecture du Projet

```
TwisterLab/
├── agents/
│   ├── base.py                          # Classe de base TwisterAgent
│   ├── orchestrator/
│   │   └── maestro.py                   # ⭐ Orchestrateur principal (CORRIGÉ)
│   ├── helpdesk/
│   │   ├── classifier.py                # Classification des tickets
│   │   ├── auto_resolver.py             # Résolution automatique
│   │   └── desktop_commander.py         # Gestion postes à distance
│   ├── api/
│   │   ├── main.py                      # Application FastAPI
│   │   └── routes_orchestrator.py       # Routes API orchestrateur
│   └── database/
│       ├── config.py                    # Config PostgreSQL
│       ├── models.py                    # Modèles SQLAlchemy
│       └── services.py                  # Services CRUD
├── tests/
│   └── unit/
│       └── test_maestro.py              # ⭐ 19 tests unitaires
├── test_maestro_integration.py          # ⭐ 6 tests d'intégration
├── run_all_tests.ps1                    # ⭐ Script PowerShell auto
├── requirements.txt                     # Dépendances Python
└── .github/
    ├── copilot-instructions.md          # Instructions complètes
    └── copilot-prompt-next-steps.md     # ⭐ PROMPT pour Copilot
```

---

## 🎯 État Actuel du Projet

### ✅ Complété

- [x] Base de données PostgreSQL + SQLAlchemy + Alembic
- [x] API FastAPI avec endpoints REST
- [x] Agent Maestro Orchestrator (corrections des 9 erreurs)
- [x] Agent Classifier (classification des tickets)
- [x] Agent Helpdesk Resolver (résolution automatique)
- [x] Agent Desktop Commander (gestion postes à distance)
- [x] Tests d'intégration (6 tests)
- [x] Tests unitaires pytest (19 tests)
- [x] Routes API orchestrateur (4 endpoints)

### 📋 Prochaines Étapes

Voir le fichier **[.github/copilot-prompt-next-steps.md](.github/copilot-prompt-next-steps.md)** pour le prompt complet GitHub Copilot.

**Résumé des 5 étapes**:
1. ✅ Installer dépendances (`pip install asyncpg pytest pytest-asyncio`)
2. ✅ Exécuter tests pytest (`pytest tests/unit/test_maestro.py -v`)
3. 🔄 Tester API REST (démarrer avec `uvicorn`)
4. 📝 Créer documentation technique (3 fichiers MD)
5. 🔌 Implémenter intégration MCP pour Desktop Commander

---

## 🧪 Tests Disponibles

### Tests Unitaires (pytest)

**Fichier**: `tests/unit/test_maestro.py`

**19 tests couvrant**:
- Initialisation de Maestro
- Routing de tickets (urgent, password, software)
- Statut des agents
- Rééquilibrage de charge
- Métriques de performance
- Gestion d'erreurs
- Enums TicketPriority et TicketComplexity

**Exécuter**:
```bash
pytest tests/unit/test_maestro.py -v
```

**Avec couverture de code**:
```bash
pytest tests/unit/test_maestro.py --cov=agents.orchestrator.maestro --cov-report=html
```

### Tests d'Intégration

**Fichier**: `test_maestro_integration.py`

**6 tests end-to-end**:
1. Password Reset (classification + routing)
2. Urgent Ticket (escalade immédiate)
3. Software Installation
4. Access Request
5. Agent Status (avec health metrics)
6. Load Balancing

**Exécuter**:
```bash
python test_maestro_integration.py
```

---

## 🌐 API Endpoints

### Orchestrateur (/api/v1/orchestrator)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/process-ticket` | Traiter un ticket complet (classify → route → resolve) |
| GET | `/results/{ticket_id}` | Obtenir les résultats pour un ticket |
| GET | `/results` | Lister tous les résultats |
| GET | `/agents/status` | Statut de tous les agents |
| GET | `/metrics` | Métriques de performance |
| POST | `/rebalance` | Rééquilibrer la charge |

**Exemple d'utilisation**:

```bash
# Démarrer l'API
uvicorn agents.api.main:app --reload --port 8000

# Tester un endpoint
curl http://localhost:8000/api/v1/orchestrator/metrics
```

**Documentation interactive**: http://localhost:8000/docs

---

## 🐛 Dépannage

### Erreur: "No module named 'asyncpg'"

**Solution**:
```bash
pip install asyncpg
```

### PostgreSQL n'est pas démarré

**Solution**:
```bash
docker-compose up -d postgres
```

### Tests pytest échouent

**Solutions**:
1. Vérifier que toutes les dépendances sont installées:
   ```bash
   pip install -r requirements.txt
   ```

2. Vérifier que PostgreSQL fonctionne:
   ```bash
   docker ps | grep postgres
   ```

3. Vérifier les imports:
   ```bash
   python -c "from agents.orchestrator.maestro import MaestroOrchestratorAgent"
   ```

### API ne démarre pas (port 8000 occupé)

**Solution**:
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

Utiliser un autre port:
```bash
uvicorn agents.api.main:app --reload --port 8001
```

---

## 📞 Aide et Support

- **Documentation complète**: `.github/copilot-instructions.md`
- **Prochaines étapes**: `.github/copilot-prompt-next-steps.md`
- **Tests unitaires**: `tests/unit/test_maestro.py`
- **Tests d'intégration**: `test_maestro_integration.py`

---

## ✅ Checklist de Vérification

Avant de passer aux étapes suivantes, vérifier que:

- [ ] Python 3.12+ est installé
- [ ] Toutes les dépendances sont installées (`pip install -r requirements.txt`)
- [ ] PostgreSQL fonctionne (docker ps)
- [ ] Les 19 tests unitaires passent (pytest)
- [ ] Les 6 tests d'intégration passent
- [ ] L'API démarre sans erreur (uvicorn)
- [ ] La page Swagger est accessible (http://localhost:8000/docs)

**Si tout est ✅, vous êtes prêt pour les prochaines étapes!**

Voir: [.github/copilot-prompt-next-steps.md](.github/copilot-prompt-next-steps.md)

---

**Bon développement! 🚀**


