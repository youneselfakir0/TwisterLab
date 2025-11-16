# 🎯 TwisterLab Continue Integration - Système de Prompts Autonomes

**Date de création** : 2025-11-12
**Version** : 1.0.0
**Statut** : ✅ Opérationnel (5 prompts système + MCP 7 tools)

---

## 📋 Vue d'Ensemble

Intégration complète de **Continue IDE** avec **TwisterLab** via **Model Context Protocol (MCP)**, permettant l'exécution de workflows autonomes sur 6+ heures pour troubleshooting, optimisation et simulation de tickets.

### Composants Créés

```
.continue/
├── config.yaml                          # Config Continue (6 modèles Ollama)
├── mcpServers/
│   └── twisterlab-mcp.json             # Config MCP (stdio transport)
└── prompts/
    ├── README.md                        # Documentation complète
    ├── quick-help.prompt.md             # Aide rapide (5 min)
    ├── troubleshoot-system.prompt.md    # Diagnostic infra (90 min)
    ├── debug-mcp.prompt.md              # Fix MCP (10 min)
    ├── optimize-pc.prompt.md            # Nettoyage PC (2h)
    └── simulate-tickets-6h.prompt.md    # Simulation 6h (overnight)
```

---

## 🚀 Prompts Système

### 1. **quick-help** (5 minutes)
**Usage** : `@prompt quick-help`

Guide ultra-rapide avec commandes courantes :
- Status check infra (API, Ollama, Docker)
- Logs rapides (API, PostgreSQL, Redis)
- Troubleshooting express (Connection refused, Services down, GPU lent)
- Monitoring CLI (métriques via MCP)
- Workflows courants (Morning check, Avant déploiement, Debug session)

**Quand l'utiliser** :
- ❓ Besoin d'aide rapide
- 📝 Mémo commandes courantes
- 🔍 Lookup quick pour syntax

---

### 2. **troubleshoot-system** (90 minutes)
**Usage** : `@prompt troubleshoot-system`

Diagnostic complet infrastructure TwisterLab :
1. **Phase 1 : Diagnostic** (30 min)
   - Infrastructure Docker (7 services sur edgeserver)
   - État des agents (7 agents autonomes)
   - Logs et erreurs (API, PostgreSQL, Redis, Ollama)
   - Réseau et connectivité (CoreRTX, edgeserver, Open WebUI)

2. **Phase 2 : Analyse** (15 min)
   - Problèmes critiques (services down, erreurs répétitives)
   - Problèmes moyens (performance dégradée, warnings)
   - Optimisations (configuration, monitoring, sécurité)

3. **Phase 3 : Actions Correctives** (45 min)
   - Demande confirmation avant exécution
   - Exécute corrections
   - Vérifie résolution
   - Documente changements

**Résultat** : Rapport structuré (résumé exécutif, métriques, problèmes, actions, recommandations)

**MCP Tools** : `monitor_system_health`, `list_autonomous_agents`, `create_backup`, `sync_cache`

**Quand l'utiliser** :
- ⚠️  Services down ou dégradés
- 📉 Performance lente
- 🔍 Audit régulier
- 📊 Avant/après déploiements

---

### 3. **debug-mcp** (10 minutes)
**Usage** : `@prompt debug-mcp`

Diagnostic et réparation connexion MCP Continue ↔ TwisterLab :

**Checklist automatique** (7 tests) :
- ✅ Continue Extension installée
- ✅ MCP config JSON valide
- ✅ MCP server syntaxe Python OK
- ✅ MCP server répond (initialize, tools/list)
- ✅ API TwisterLab online/offline
- ✅ Ollama GPU accessible
- ✅ 7 tools détectés

**Erreurs diagnostiquées** :
1. Connection refused (errno 111)
2. Failed to parse config
3. Python SyntaxError
4. No tools detected
5. Ollama localhost vs CoreRTX confusion

**Fixes automatiques** :
- Recréer MCP config JSON
- Corriger Ollama apiBase (localhost → 192.168.0.20)
- Valider syntaxe Python
- Reload Continue config

**Quand l'utiliser** :
- ❌ Erreurs MCP connexion
- 🔄 Après changements infrastructure
- 🆕 Première installation

---

### 4. **optimize-pc** (2 heures)
**Usage** : `@prompt optimize-pc`

Nettoyage et optimisation PC Windows TwisterLab :

**Phase 1 : Diagnostic** (30 min)
- CPU/RAM/Disk usage
- Services Windows
- Réseau (CoreRTX, edgeserver)
- Python/Docker/Git versions
- Fichiers volumineux (>1GB)
- Cache npm/pip/temp

**Phase 2 : Nettoyage** (45 min)
- Temp Windows + utilisateur
- Docker cleanup (containers, images, volumes, cache)
- Python cleanup (pip cache, __pycache__, .pyc)
- Logs TwisterLab anciens (>7 jours)

**Phase 3 : Optimisation** (30 min)
- Désactiver services inutiles
- TCP/IP tuning réseau
- Défrag (HDD) ou TRIM (SSD)
- Mise à jour packages

**Phase 4 : Sécurité** (15 min)
- Vérifier Firewall + règles Docker
- Windows Update
- Windows Defender

**Phase 5 : Monitoring** (20 min)
- Script monitoring quotidien
- Tâche planifiée (2h chaque jour)
- Performance Monitor collecteur

**Résultat attendu** :
- 🧹 Espace libéré : 5-20 GB
- ⚡ Performance : +10-30%
- 📊 Monitoring automatique

**Quand l'utiliser** :
- 🐌 PC lent
- 💾 Espace disque faible
- 🗓️ Maintenance mensuelle
- 🆕 Après gros projets

---

### 5. **simulate-tickets-6h** (6 heures)
**Usage** : `@prompt simulate-tickets-6h`

Génération et traitement automatique ~100-120 tickets pour tester orchestration :

**Phase 1 : Initialisation** (5 min)
- Vérifier 7 agents actifs
- État système baseline
- Backup de sécurité

**Phase 2 : Génération Continue** (6 heures)
Distribution réaliste :
- **P1 (10%)** : Critiques (serveur down, DB corrompue, API 500)
- **P2 (20%)** : Élevées (CPU 95%, queries lentes, backup fail)
- **P3 (50%)** : Normales (cleanup, optimisation, sync)
- **P4 (20%)** : Questions (versions, stats, docs)

**Workflow par ticket** :
1. Générer ticket aléatoire
2. `@mcp classify_ticket` → agent + SOP
3. `@mcp resolve_ticket` → exécution SOP
4. Logger résultat
5. Attendre interval (P1: 0s, P2: 30s, P3: 2-3min, P4: 4-5min)

**Phase 3 : Monitoring Parallèle** (toutes les 15 min)
- `@mcp monitor_system_health`
- Si CPU >80% → ticket P2 auto
- Si agent down → ticket P1 auto
- `@mcp sync_cache` toutes les heures

**Phase 4 : Rapport Final**
- Métriques globales (total, résolus, échoués, temps moyen)
- Distribution P1/P2/P3/P4
- Performance 7 agents
- Problèmes détectés
- Recommandations

**Résultat attendu** :
- 📊 ~100-120 tickets traités
- ⚡ Taux succès >80%
- 🤖 Validation orchestration Maestro
- 📈 Benchmarking agents

**MCP Tools** : `classify_ticket`, `resolve_ticket`, `monitor_system_health`, `create_backup`, `sync_cache`

**Précautions** :
- ✅ Backup obligatoire avant
- ✅ Surveillance CPU/RAM
- ✅ Arrêt auto si >95%
- ❌ Jamais tickets destructifs (DROP, DELETE)

**Quand l'utiliser** :
- 🧪 Tests de charge
- 🤖 Validation agents autonomes
- 📊 Benchmarking
- 🔬 Tests régression
- 🌙 Overnight (lancer soir, rapport matin)

---

## 🔧 MCP Tools Disponibles (7)

Tous les prompts peuvent utiliser ces tools via `@mcp <tool>` :

| Tool | Description | Usage Prompts |
|------|-------------|---------------|
| `list_autonomous_agents` | Liste 7 agents actifs | troubleshoot, simulate |
| `monitor_system_health` | Métriques CPU/RAM/Disk/Docker | troubleshoot, simulate |
| `create_backup` | Backup PostgreSQL + configs | troubleshoot, simulate |
| `sync_cache` | Sync Redis ↔ PostgreSQL | troubleshoot, simulate |
| `classify_ticket` | Classification LLM tickets | simulate |
| `resolve_ticket` | Exécution SOPs | simulate |
| `execute_desktop_command` | Commandes système Windows/Linux | troubleshoot, optimize |

---

## 🌐 Architecture Réseau

```
┌─────────────────────────────────────────────────────────────┐
│ TwisterLab PC (Windows Dev)                                 │
│ - VS Code + Continue Extension                              │
│ - MCP Client (stdio transport)                              │
│ - 5 Prompts Système                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴──────────────┐
         │                               │
         ▼                               ▼
┌─────────────────────┐      ┌────────────────────────┐
│ CoreRTX             │      │ edgeserver             │
│ 192.168.0.20        │      │ 192.168.0.30           │
│                     │      │                        │
│ Ollama :11434       │      │ TwisterLab API :8000   │
│ RTX 3060 GPU        │      │ PostgreSQL :5432       │
│                     │      │ Redis :6379            │
│ Models:             │      │ Prometheus :9090       │
│ - llama3.2:1b       │      │ Grafana :3000          │
│ - llama3:8b         │      │ Open WebUI :8083       │
│ - deepseek-r1       │      │                        │
│ - codellama         │      │ 7 Real Agents:         │
│ - qwen3:8b          │      │ - Monitoring           │
│ - gpt-oss:120b      │      │ - Backup               │
│                     │      │ - Sync                 │
│                     │      │ - Classifier           │
│                     │      │ - Resolver             │
│                     │      │ - DesktopCommander     │
│                     │      │ - Maestro              │
└─────────────────────┘      └────────────────────────┘
```

---

## 📊 Métriques & Performances

### Prompts - Durée Estimée

| Prompt | Durée | Complexité | Autonomie |
|--------|-------|------------|-----------|
| quick-help | 5 min | Faible | Aide seulement |
| debug-mcp | 10 min | Moyenne | Semi-automatique |
| troubleshoot-system | 90 min | Élevée | Confirmation requise |
| optimize-pc | 2h | Élevée | Confirmation requise |
| simulate-tickets-6h | 6h | Très élevée | Entièrement autonome |

### MCP Tools - Usage par Prompt

| Tool | troubleshoot | debug-mcp | optimize | simulate |
|------|--------------|-----------|----------|----------|
| list_autonomous_agents | ✅ | ❌ | ❌ | ✅ |
| monitor_system_health | ✅ | ❌ | ❌ | ✅ |
| create_backup | ✅ | ❌ | ❌ | ✅ |
| sync_cache | ✅ | ❌ | ❌ | ✅ |
| classify_ticket | ❌ | ❌ | ❌ | ✅ |
| resolve_ticket | ❌ | ❌ | ❌ | ✅ |
| execute_desktop_command | ⚠️  | ❌ | ✅ | ❌ |

---

## 🎯 Workflows Recommandés

### Morning Routine (10 min)
```bash
1. @prompt quick-help          # Refresh commandes
2. @mcp list_autonomous_agents # Vérifier agents
3. @mcp monitor_system_health  # Métriques système
4. Grafana dashboard           # Overview visuel
```

### Weekly Maintenance (3h)
```bash
1. @prompt optimize-pc         # Nettoyage PC (2h)
2. @prompt troubleshoot-system # Diagnostic infra (90 min)
3. Backup & Sync               # via Grafana/scripts
```

### Monthly Load Test (6h)
```bash
1. @prompt simulate-tickets-6h # Overnight test
2. Analyser rapport final
3. Ajuster configuration selon résultats
4. Redéployer si nécessaire
```

### Emergency Debug (20 min)
```bash
1. @prompt quick-help          # Commands référence
2. @prompt debug-mcp           # Si MCP fail
3. @prompt troubleshoot-system # Si infra fail
4. Escalate si non résolu
```

---

## 🔒 Sécurité & Best Practices

### Prompts
- ✅ **Backup obligatoire** avant actions critiques
- ✅ **Confirmation utilisateur** pour opérations destructives
- ✅ **Logs détaillés** de toutes actions
- ❌ **Jamais exposer** credentials dans outputs
- ❌ **Jamais exécuter** commandes non validées

### MCP Tools
- ✅ **Mode MOCK** automatique si API offline
- ✅ **Validation input** pour tous arguments
- ✅ **Timeout** sur appels API (30s max)
- ✅ **Rate limiting** (max 1 ticket/minute pour simulate)
- ❌ **Pas de SQL direct** (toujours via ORM)

### Infrastructure
- ✅ **Credentials** dans `.env` (jamais Git)
- ✅ **HTTPS** pour APIs externes
- ✅ **Firewall** configuré (ports nécessaires seulement)
- ✅ **Monitoring** actif (Prometheus + Grafana)
- ✅ **Backups automatiques** (quotidiens)

---

## 📖 Documentation

### Fichiers Clés
- `.continue/prompts/README.md` - Documentation complète prompts
- `.continue/config.yaml` - Config Continue (6 modèles Ollama)
- `.continue/mcpServers/twisterlab-mcp.json` - Config MCP
- `agents/mcp/mcp_server_continue_sync.py` - Serveur MCP
- `copilot-instructions.md` - Guide développement TwisterLab

### Ressources Externes
- [Continue Documentation](https://docs.continue.dev)
- [MCP Protocol](https://spec.modelcontextprotocol.io)
- [Ollama Documentation](https://ollama.ai/docs)
- [TwisterLab GitHub](https://github.com/youneselfakir0/TwisterLab)

---

## 🚦 Statut Actuel

**Date vérification** : 2025-11-12

| Composant | Statut | Notes |
|-----------|--------|-------|
| Continue Extension | ✅ Installé | Version latest |
| MCP Server | ✅ Fonctionnel | 7 tools détectés |
| Ollama GPU | ✅ Online | CoreRTX (192.168.0.20:11434) |
| TwisterLab API | ⚠️  Variable | Mode MOCK si offline |
| Prompts Système | ✅ Créés | 5 prompts opérationnels |
| Config Continue | ✅ Configuré | 6 modèles Ollama |
| Monitoring | ✅ Actif | Prometheus + Grafana |

---

## 🎓 Prochaines Étapes

### Court Terme (1 semaine)
- [ ] Tester `@prompt simulate-tickets-6h` overnight
- [ ] Collecter métriques performance prompts
- [ ] Ajuster timeouts/intervals selon résultats
- [ ] Créer dashboard Grafana pour prompts

### Moyen Terme (1 mois)
- [ ] Ajouter prompts spécialisés (backup, deployment, testing)
- [ ] Intégrer alerting Prometheus pour prompts critiques
- [ ] Créer CI/CD pour validation prompts
- [ ] Documentation vidéo workflows

### Long Terme (3 mois)
- [ ] Prompts multi-agents (orchestration complexe)
- [ ] ML sur résultats simulations (prédiction pannes)
- [ ] API REST pour trigger prompts externes
- [ ] Marketplace prompts TwisterLab communauté

---

## 📞 Support

**Problème MCP** → `@prompt debug-mcp`
**Problème Infrastructure** → `@prompt troubleshoot-system`
**Aide Rapide** → `@prompt quick-help`
**Documentation** → `.continue/prompts/README.md`

**GitHub Issues** : https://github.com/youneselfakir0/TwisterLab/issues
**Email** : [votre-email]

---

**Version** : 1.0.0
**Date** : 2025-11-12
**Auteur** : TwisterLab Team
**Licence** : MIT
