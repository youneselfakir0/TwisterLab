---
description: "Index des prompts système TwisterLab pour Continue"
---

# 📚 Prompts TwisterLab - Guide d'Utilisation

Voici tous les prompts système disponibles pour Continue, organisés par catégorie.

## 🔧 Troubleshooting & Diagnostic

### `@prompt troubleshoot-system`
**Durée** : ~90 minutes
**Objectif** : Diagnostic complet de l'infrastructure TwisterLab (Docker Swarm, agents, API, monitoring)

**Ce qu'il fait** :
1. Vérifie les 7 services Docker sur edgeserver (192.168.0.30)
2. Analyse l'état des 7 agents autonomes via MCP
3. Inspecte logs (API, PostgreSQL, Redis, Ollama)
4. Teste connectivité réseau (CoreRTX, edgeserver, Open WebUI)
5. Identifie problèmes critiques/moyens/faibles
6. Propose solutions concrètes avec commandes
7. Génère rapport détaillé

**Quand l'utiliser** :
- ⚠️  Services TwisterLab down ou dégradés
- 📉 Performance lente (CPU/RAM/Disk élevé)
- 🔍 Audit régulier de santé système
- 📊 Avant/après déploiements majeurs

**MCP Tools utilisés** :
- `@mcp monitor_system_health` - Métriques temps réel
- `@mcp list_autonomous_agents` - État agents
- `@mcp create_backup` - Backup avant corrections
- `@mcp sync_cache` - Sync Redis/PostgreSQL

---

### `@prompt debug-mcp`
**Durée** : ~10 minutes
**Objectif** : Diagnostiquer et réparer les erreurs de connexion MCP Continue ↔ TwisterLab

**Ce qu'il fait** :
1. Checklist automatique (7 tests)
   - Continue Extension installée
   - MCP config JSON valide
   - MCP server syntaxe Python OK
   - MCP server répond (initialize, tools/list)
   - API TwisterLab online/offline
   - Ollama GPU accessible
   - 7 tools détectés
2. Identifie erreurs courantes (errno 111, syntax, config)
3. Applique corrections automatiques
4. Vérifie fonctionnement après fix

**Quand l'utiliser** :
- ❌ "Connection refused (errno 111)"
- ❌ "Failed to parse config"
- ❌ "No tools detected" dans Continue
- ❌ Python SyntaxError dans MCP server
- 🔄 Après changements infrastructure
- 🆕 Première installation Continue + MCP

**Fixes automatiques** :
- Recréer MCP config JSON
- Corriger Ollama apiBase (localhost → 192.168.0.20)
- Valider syntaxe Python
- Reload Continue config

---

## ⚡ Optimisation & Performance

### `@prompt optimize-pc`
**Durée** : ~2 heures
**Objectif** : Nettoyer et optimiser le PC Windows de développement TwisterLab

**Ce qu'il fait** :
1. **Diagnostic** (30 min)
   - CPU/RAM/Disk usage
   - Services Windows running
   - Réseau (CoreRTX, edgeserver)
   - Python/Docker/Git versions
   - Fichiers volumineux (>1GB)
   - Cache npm/pip/temp

2. **Nettoyage** (45 min)
   - Temp Windows + utilisateur
   - Docker cleanup (containers, images, volumes, cache)
   - Python cleanup (pip cache, __pycache__, .pyc)
   - Logs TwisterLab anciens (>7 jours)
   - Debug reports obsolètes

3. **Optimisation** (30 min)
   - Désactiver services inutiles (telemetry, superfetch)
   - TCP/IP tuning réseau
   - Défrag (HDD) ou TRIM (SSD)
   - Mise à jour Python packages

4. **Sécurité** (15 min)
   - Vérifier Firewall + règles Docker
   - Windows Update status
   - Windows Defender actif

5. **Monitoring** (20 min)
   - Créer script monitoring quotidien
   - Tâche planifiée (tous les jours 2h)
   - Performance Monitor collecteur

**Résultat attendu** :
- 🧹 Espace libéré : 5-20 GB
- ⚡ Performance : +10-30%
- 📊 Monitoring automatique configuré

**Quand l'utiliser** :
- 🐌 PC lent (CPU/RAM/Disk élevé)
- 💾 Espace disque faible (<20GB libre)
- 🗓️ Maintenance mensuelle préventive
- 🆕 Après installation de gros projets

---

## 🎭 Simulation & Tests

### `@prompt simulate-tickets-6h`
**Durée** : 6 heures (non-stop)
**Objectif** : Générer et traiter automatiquement ~100-120 tickets pour tester l'orchestration autonome

**Ce qu'il fait** :
1. **Initialisation** (5 min)
   - Vérifier 7 agents actifs
   - État système baseline
   - Backup de sécurité

2. **Génération continue** (6 heures)
   - **P1 (10%)** : Incidents critiques (serveur down, DB corrompue, API 500)
   - **P2 (20%)** : Problèmes élevés (CPU 95%, queries lentes, backup fail)
   - **P3 (50%)** : Maintenance normale (cleanup logs, optimisation, sync)
   - **P4 (20%)** : Questions (versions, stats, documentation)

   **Workflow par ticket** :
   - Générer ticket aléatoire (selon distribution)
   - `@mcp classify_ticket` → agent assigné + SOP
   - `@mcp resolve_ticket` → exécution SOP
   - Logger résultat (success/failed/pending)
   - Attendre interval (P1: 0s, P2: 30s, P3: 2-3min, P4: 4-5min)

3. **Monitoring parallèle** (toutes les 15 min)
   - `@mcp monitor_system_health`
   - Si CPU >80% → ticket P2 auto
   - Si agent down → ticket P1 auto
   - `@mcp sync_cache` toutes les heures

4. **Rapport final** (après 6h)
   - Métriques globales (total, résolus, échoués, temps moyen)
   - Distribution P1/P2/P3/P4
   - Performance des 7 agents
   - Problèmes détectés
   - Recommandations

**Résultat attendu** :
- 📊 ~100-120 tickets traités
- ⚡ Taux succès >80%
- 🤖 Validation orchestration Maestro
- 📈 Métriques performance agents

**Quand l'utiliser** :
- 🧪 Tests de charge infrastructure
- 🤖 Validation agents autonomes
- 📊 Benchmarking performance
- 🔬 Tests régression après changements
- 🌙 Overnight (lancer le soir, rapport le matin)

**MCP Tools utilisés** :
- `@mcp classify_ticket` - Classification LLM
- `@mcp resolve_ticket` - Exécution SOPs
- `@mcp monitor_system_health` - Surveillance
- `@mcp create_backup` - Sécurité
- `@mcp sync_cache` - Sync horaire

⚠️ **Précautions** :
- Backup obligatoire avant lancement
- Surveillance CPU/RAM pendant exécution
- Arrêt auto si ressources >95%
- Ne jamais générer tickets destructifs réels (DROP, DELETE)

---

## 📖 Utilisation des Prompts

### Dans Continue Chat
```
@prompt troubleshoot-system
```

### Via Command Palette (Ctrl+Shift+P)
```
Continue: Use Prompt → Sélectionner prompt
```

### Dans le code (commentaires)
```python
# @prompt debug-mcp
# Diagnostiquer connexion MCP
```

---

## 🔗 Architecture TwisterLab

```
┌─────────────────────────────────────────────────────────────┐
│ TwisterLab PC (Windows Dev)                                 │
│ - VS Code + Continue Extension                              │
│ - MCP Client (stdio transport)                              │
│ - Prompts : troubleshoot, debug-mcp, optimize-pc, simulate  │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴──────────────┐
         │                               │
         ▼                               ▼
┌─────────────────────┐      ┌────────────────────────┐
│ CoreRTX             │      │ edgeserver             │
│ 192.168.0.20        │      │ 192.168.0.30           │
│                     │      │                        │
│ - Ollama :11434     │      │ - TwisterLab API :8000 │
│ - RTX 3060 GPU      │      │ - PostgreSQL :5432     │
│ - llama3.2:1b       │      │ - Redis :6379          │
│ - deepseek-r1       │      │ - Prometheus :9090     │
│ - codellama         │      │ - Grafana :3000        │
│ - qwen3:8b          │      │ - Open WebUI :8083     │
│                     │      │                        │
│                     │      │ 7 Real Agents:         │
│                     │      │  - Monitoring          │
│                     │      │  - Backup              │
│                     │      │  - Sync                │
│                     │      │  - Classifier          │
│                     │      │  - Resolver            │
│                     │      │  - DesktopCommander    │
│                     │      │  - Maestro             │
└─────────────────────┘      └────────────────────────┘
```

---

## 🛠️ MCP Tools Disponibles

Tous les prompts peuvent utiliser ces 7 tools MCP :

| Tool | Description | Utilisation |
|------|-------------|-------------|
| `@mcp list_autonomous_agents` | Liste agents actifs | État système |
| `@mcp monitor_system_health` | Métriques CPU/RAM/Disk/Docker | Monitoring temps réel |
| `@mcp create_backup` | Backup PostgreSQL + config | Avant changements |
| `@mcp sync_cache` | Synchronisation Redis ↔ PostgreSQL | Maintenance cache |
| `@mcp classify_ticket` | Classification LLM de tickets | Workflow helpdesk |
| `@mcp resolve_ticket` | Exécution SOPs automatiques | Résolution tickets |
| `@mcp execute_desktop_command` | Commandes système Windows/Linux | Administration |

---

## 📝 Créer un Nouveau Prompt

1. Créer fichier dans `.continue/prompts/` :
```bash
touch .continue/prompts/mon-prompt.prompt.md
```

2. Structure YAML frontmatter :
```yaml
---
description: "Description courte du prompt"
---

# Titre du Prompt

Instructions détaillées...
```

3. Utiliser dans Continue :
```
@prompt mon-prompt
```

---

## 🆘 Support

**Logs MCP** :
```powershell
python agents/mcp/mcp_server_continue_sync.py 2>&1 | Tee-Object mcp.log
```

**Test manuel MCP** :
```powershell
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test"}}}' | python agents/mcp/mcp_server_continue_sync.py
```

**Reload Continue** :
```
Ctrl+Shift+P → Continue: Reload Config
```

**Config files** :
- `.continue/mcpServers/twisterlab-mcp.json` - MCP config
- `~/.continue/config.yaml` - Continue global config
- `.continue/config.yaml` - Continue project config

---

**Version** : 1.0.0
**Dernière mise à jour** : 2025-11-12
**Prompts disponibles** : 4 (troubleshoot, debug-mcp, optimize-pc, simulate-tickets-6h)
