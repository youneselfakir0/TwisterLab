---
name: "Simulate Tickets 6H"
description: "Génère et traite des tickets automatiquement pendant 6 heures pour tester les agents TwisterLab"
---

# Mission : Simulation de Tickets Helpdesk (6 Heures)

Tu es un **générateur de tickets automatique** qui va créer et soumettre des tickets réalistes à TwisterLab pendant **6 heures non-stop**.

## 🎯 Objectif

Tester l'orchestration autonome des agents en générant :
- **Tickets variés** (P1 à P4)
- **Distribution réaliste** (70% P3-P4, 20% P2, 10% P1)
- **Flux continu** (1 ticket toutes les 2-5 minutes)
- **Complexité croissante** (simple → complexe au fil du temps)

## 📋 Types de Tickets à Générer

### P1 - Critique (10%)
```yaml
type: incident
priority: P1
category: infrastructure
exemples:
  - "Serveur edgeserver DOWN - services inaccessibles"
  - "Base PostgreSQL corrompue - perte de données"
  - "Redis crash en boucle - cache indisponible"
  - "API TwisterLab 500 Internal Error sur tous les endpoints"
  - "Ollama GPU freeze - LLM ne répond plus"
  - "Docker Swarm en état dégradé - 4/7 services down"
```

### P2 - Élevée (20%)
```yaml
type: problem
priority: P2
category: performance
exemples:
  - "CPU edgeserver à 95% depuis 30 minutes"
  - "PostgreSQL queries lentes (>5s)"
  - "Redis OOM - mémoire saturée"
  - "API latency élevée (>2s par requête)"
  - "Backup agent échoue depuis 48h"
  - "Monitoring agent ne remonte plus de métriques"
  - "Disk utilization 85% sur edgeserver"
```

### P3 - Normale (50%)
```yaml
type: request
priority: P3
category: maintenance
exemples:
  - "Nettoyer les logs Docker (>10GB)"
  - "Optimiser les index PostgreSQL"
  - "Mettre à jour Ollama vers dernière version"
  - "Ajouter monitoring sur température GPU"
  - "Configurer rotation logs automatique"
  - "Créer backup manuel avant déploiement"
  - "Synchroniser cache Redis/PostgreSQL"
  - "Vérifier certificats SSL expiration"
```

### P4 - Basse (20%)
```yaml
type: question
priority: P4
category: information
exemples:
  - "Quelle version de llama3.2 est déployée ?"
  - "Combien de tickets traités aujourd'hui ?"
  - "Quel agent a le plus d'uptime ?"
  - "Statistiques d'utilisation RAM dernières 24h"
  - "Liste des backups disponibles"
  - "Historique des déploiements ce mois"
  - "Documentation du ClassifierAgent"
```

## ⚙️ Workflow de Simulation

### Étape 1 : Initialisation (5 min)
```python
# Vérifier que les agents sont prêts
@mcp list_autonomous_agents
# Expected: 7 agents actifs (Monitoring, Backup, Sync, Classifier, Resolver, DesktopCommander, Maestro)

# Vérifier l'état système de base
@mcp monitor_system_health
# Expected: CPU <50%, RAM <70%, tous services UP

# Créer backup de sécurité
@mcp create_backup
# Expected: Backup créé avec succès
```

### Étape 2 : Génération Continue (6 heures)
Pour chaque itération (toutes les 2-5 minutes) :

1. **Générer ticket aléatoire** selon distribution :
```python
import random
priority_distribution = {
    "P1": 0.10,  # 10% critiques
    "P2": 0.20,  # 20% élevées
    "P3": 0.50,  # 50% normales
    "P4": 0.20   # 20% basses
}

ticket = {
    "id": f"TICKET-{timestamp}-{random.randint(1000,9999)}",
    "priority": random.choices(["P1","P2","P3","P4"], weights=[0.10,0.20,0.50,0.20])[0],
    "title": "[généré automatiquement]",
    "description": "[détails réalistes]",
    "category": random.choice(["infrastructure","performance","maintenance","information"]),
    "created_at": datetime.now().isoformat()
}
```

2. **Classifier le ticket** :
```python
@mcp classify_ticket {
    "ticket_id": ticket["id"],
    "description": ticket["description"],
    "priority": ticket["priority"]
}
# Expected: Classifier retourne agent assigné + catégorie
```

3. **Résoudre le ticket** :
```python
@mcp resolve_ticket {
    "ticket_id": ticket["id"],
    "assigned_agent": result_classification["agent"],
    "sop_id": result_classification["sop"]
}
# Expected: Resolver exécute SOP et retourne résultat
```

4. **Logger les résultats** :
```markdown
### Ticket #{N} - {timestamp}
**ID** : {ticket_id}
**Priorité** : {priority}
**Titre** : {title}
**Assigné à** : {agent}
**Statut** : {resolved/failed/pending}
**Durée** : {duration_seconds}s
**Résultat** : {success_message}
```

5. **Attendre interval** :
```python
# P1 → traiter immédiatement (0s)
# P2 → attendre 30s
# P3 → attendre 2-3 min
# P4 → attendre 4-5 min
```

### Étape 3 : Monitoring Continu (en parallèle)
Toutes les 15 minutes :
```python
# Vérifier santé du système
health = @mcp monitor_system_health

# Si CPU >80% ou RAM >85% → générer ticket P2 automatiquement
if health["cpu"] > 80:
    generate_ticket("P2", "CPU surchargé pendant simulation")

# Si agent down → générer ticket P1
if any(agent["status"] == "down" for agent in agents):
    generate_ticket("P1", f"Agent {agent['name']} DOWN")

# Synchroniser cache toutes les heures
if minute % 60 == 0:
    @mcp sync_cache
```

### Étape 4 : Rapport Final (après 6h)
```markdown
# 📊 Rapport de Simulation 6 Heures

## Métriques Globales
- **Durée totale** : 6h 00m 00s
- **Tickets générés** : {total_tickets}
- **Tickets résolus** : {resolved_count} ({success_rate}%)
- **Tickets échoués** : {failed_count}
- **Temps moyen résolution** : {avg_duration}s

## Distribution des Tickets
- P1 (Critique) : {p1_count} tickets ({p1_percent}%)
- P2 (Élevée) : {p2_count} tickets ({p2_percent}%)
- P3 (Normale) : {p3_count} tickets ({p3_percent}%)
- P4 (Basse) : {p4_count} tickets ({p4_percent}%)

## Performance des Agents
| Agent | Tickets Traités | Taux Succès | Temps Moyen |
|-------|----------------|-------------|-------------|
| ClassifierAgent | {count} | {rate}% | {avg}s |
| ResolverAgent | {count} | {rate}% | {avg}s |
| MonitoringAgent | {count} | {rate}% | {avg}s |
| BackupAgent | {count} | {rate}% | {avg}s |
| SyncAgent | {count} | {rate}% | {avg}s |
| DesktopCommanderAgent | {count} | {rate}% | {avg}s |
| MaestroAgent | {count} | {rate}% | {avg}s |

## Problèmes Détectés
- {problem_1} (apparu après {duration})
- {problem_2} (résolu automatiquement)
- {problem_3} (nécessite intervention manuelle)

## Recommandations
1. **Performance** : {recommendation}
2. **Scalabilité** : {recommendation}
3. **Monitoring** : {recommendation}

## Logs Détaillés
[Lien vers fichier log complet : simulation_{timestamp}.log]
```

## 🔧 Outils MCP Utilisés

- `@mcp classify_ticket` - Classification automatique des tickets
- `@mcp resolve_ticket` - Résolution via SOPs
- `@mcp monitor_system_health` - Surveillance en temps réel
- `@mcp list_autonomous_agents` - État des agents
- `@mcp create_backup` - Backup avant simulation
- `@mcp sync_cache` - Synchronisation données
- `@mcp execute_desktop_command` - Commandes système si besoin

## ⚠️ Consignes de Sécurité

- ✅ **Backup obligatoire** avant de démarrer
- ✅ **Surveiller ressources** (CPU/RAM/Disk) pendant simulation
- ✅ **Arrêt automatique** si système critique (CPU >95%, RAM >95%)
- ✅ **Logger tout** pour analyse post-mortem
- ❌ **Ne jamais** générer tickets destructifs réels (DELETE, DROP, etc.)
- ❌ **Ne jamais** dépasser 1 ticket/minute pour éviter surcharge

## 🚀 Commande de Lancement

Pour démarrer la simulation 6h :
```
@prompt simulate-tickets-6h
```

Continue va :
1. Demander confirmation finale
2. Créer backup de sécurité
3. Démarrer génération de tickets
4. Monitorer le système en parallèle
5. Générer rapport final après 6h

**Temps estimé** : 6h 00m (360 minutes)
**Tickets estimés** : ~100-120 tickets
**Charge système** : Modérée (CPU 40-60%, RAM 50-70%)
