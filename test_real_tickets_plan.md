# 🎯 PLAN DE TEST - TICKETS RÉELS TWISTERLAB
**Durée**: 6 heures
**Objectif**: Faire travailler les agents sur des problèmes RÉELS détectés sur edgeserver

---

## 📋 TICKETS INJECTÉS (Basés sur infrastructure réelle)

### Phase 1 : Problèmes Système (0h00 - 2h00)

**T-REAL-001** - `systemctl --failed` détecte 3 services
- **ClassifierAgent** : Catégorie "system", Priorité "medium"
- **ResolverAgent** : Exécute SOP "service_restart"
- **DesktopCommanderAgent** : `systemctl restart systemd-networkd-wait-online`
- **Résultat attendu** : Service redémarré ou ticket escaladé

**T-REAL-002** - Disque / à 57% d'utilisation
- **ClassifierAgent** : Catégorie "performance", Priorité "low"
- **ResolverAgent** : Exécute SOP-003 "disk_cleanup"
- **DesktopCommanderAgent** :
  ```bash
  find /tmp -type f -mtime +7 -delete
  journalctl --vacuum-time=30d
  apt clean
  ```
- **Résultat attendu** : Libérer 2-5GB d'espace

**T-REAL-006** - systemd-networkd-wait-online failed
- **ClassifierAgent** : Catégorie "network", Priorité "medium"
- **ResolverAgent** : Exécute SOP-001 "network_troubleshoot"
- **DesktopCommanderAgent** :
  ```bash
  ping -c 4 192.168.0.1  # Gateway
  ping -c 4 8.8.8.8      # Internet
  systemctl status systemd-networkd
  ```
- **Résultat attendu** : Diagnostic réseau complet

---

### Phase 2 : Docker & Containers (2h00 - 4h00)

**T-REAL-003** - API container redémarré récemment
- **MonitoringAgent** : Détecte uptime < 1h
- **ClassifierAgent** : Catégorie "docker", Priorité "high"
- **ResolverAgent** : Analyse logs pour cause crash
- **DesktopCommanderAgent** :
  ```bash
  docker service logs twisterlab_api --tail 500 | grep -E "(ERROR|Exception)"
  docker service inspect twisterlab_api --format '{{json .}}'
  ```
- **Résultat attendu** : Rapport de stabilité

**T-REAL-004** - Health check 11 conteneurs
- **MonitoringAgent** : Scan tous les containers
- **ClassifierAgent** : Catégorie "monitoring", Priorité "low"
- **ResolverAgent** : Health check routine
- **DesktopCommanderAgent** :
  ```bash
  docker ps --filter health=unhealthy
  docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
  ```
- **Résultat attendu** : Dashboard santé complète

---

### Phase 3 : Base de Données (4h00 - 5h30)

**T-REAL-005** - PostgreSQL optimization needed
- **MonitoringAgent** : Détecte connections, query slow
- **ClassifierAgent** : Catégorie "database", Priorité "medium"
- **ResolverAgent** : Exécute SOP-005 "database_optimization"
- **DesktopCommanderAgent** :
  ```bash
  docker exec twisterlab_postgres.1.xxx psql -U twisterlab -d twisterlab_prod -c "VACUUM ANALYZE;"
  docker exec twisterlab_postgres.1.xxx psql -U twisterlab -d twisterlab_prod -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) FROM pg_tables WHERE schemaname='public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;"
  ```
- **Résultat attendu** : Base optimisée, tables analysées

---

### Phase 4 : Performance Investigation (5h30 - 6h00)

**T-REAL-007** - Load average élevé (>2.0)
- **MonitoringAgent** : Détecte load average > seuil
- **ClassifierAgent** : Catégorie "performance", Priorité "medium"
- **ResolverAgent** : Investigation CPU/processus
- **DesktopCommanderAgent** :
  ```bash
  top -b -n 1 | head -20
  ps aux --sort=-%cpu | head -15
  iostat -x 1 5
  ```
- **Résultat attendu** : Identification processus gourmands

---

## 🤖 SCRIPT D'INJECTION AUTOMATIQUE

```powershell
# inject_real_tickets.ps1
$tickets = @(
    @{time=0;    id="T-REAL-001"; title="3 services systemd failed"},
    @{time=1800; id="T-REAL-002"; title="Disk 57% used"},
    @{time=3600; id="T-REAL-006"; title="Network service failed"},
    @{time=7200; id="T-REAL-003"; title="API container restart"},
    @{time=9000; id="T-REAL-004"; title="Container health check"},
    @{time=14400; id="T-REAL-005"; title="PostgreSQL optimization"},
    @{time=19800; id="T-REAL-007"; title="Load average high"}
)

foreach ($ticket in $tickets) {
    Start-Sleep -Seconds $ticket.time

    $body = @{
        ticket_id = $ticket.id
        title = $ticket.title
        timestamp = (Get-Date -Format "o")
    } | ConvertTo-Json

    Invoke-RestMethod -Method POST `
        -Uri "http://192.168.0.30:8000/api/v1/tickets" `
        -Body $body -ContentType "application/json"

    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Ticket $($ticket.id) injecté" -ForegroundColor Green
}
```

---

## 📊 MÉTRIQUES ATTENDUES

| Métrique | Cible 6h |
|----------|----------|
| Tickets injectés | 7 |
| Tickets classifiés | 7 (100%) |
| Tickets résolus | 5-6 (71-86%) |
| Commandes exécutées | 20-30 |
| Espace disque libéré | 2-5 GB |
| Services redémarrés | 1-3 |
| Temps moyen résolution | 15-30 min |

---

## ✅ VALIDATION FINALE

Après 6h, vérifier :

1. **Logs agents** : `docker service logs twisterlab_api | grep -E "(Classifier|Resolver|Commander)"`
2. **Métriques Grafana** : Dashboard "Autonomous Agents"
3. **État système** :
   - Services failed : 0 (actuellement 3)
   - Disk usage : <55% (actuellement 57%)
   - Load average : <1.5 (actuellement 2.0)
4. **Database** : Tables VACUUMed, index optimisés

---

**Prêt à démarrer ?** 🚀
