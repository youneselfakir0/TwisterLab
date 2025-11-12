#!/usr/bin/env pwsh
# =============================================================================
# TWISTERLAB - Missions VRAIMENT autonomes pour les agents
# Les agents vont REELLEMENT executer ces taches EUX-MEMES
# =============================================================================

$ErrorActionPreference = "Continue"

Write-Host @"

=================================================================
    MISSIONS AUTONOMES - LES AGENTS TRAVAILLENT SEULS
=================================================================

Au lieu que JE fasse le travail, les agents vont:
  1. MonitoringAgent -> Scanner VRAIMENT l'infrastructure
  2. BackupAgent -> Creer un VRAI backup maintenant
  3. SyncAgent -> Synchroniser Redis <-> PostgreSQL
  4. ClassifierAgent -> Analyser les logs et classifier
  5. MaestroAgent -> Orchestrer TOUTE la sequence

AUCUNE intervention manuelle - 100% AUTONOME !

=================================================================

"@ -ForegroundColor Cyan

function Send-RealMission {
    param(
        [string]$Agent,
        [string]$Mission,
        [hashtable]$Context
    )

    $payload = @{
        operation = $Mission
        context = $Context
    } | ConvertTo-Json -Depth 5

    Write-Host "`n>>> MISSION ENVOYEE A: $Agent" -ForegroundColor Yellow
    Write-Host ">>> OPERATION: $Mission" -ForegroundColor Gray
    Write-Host ">>> Les agents travaillent..." -ForegroundColor Magenta

    try {
        $result = Invoke-RestMethod `
            -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents/$Agent/execute" `
            -Method Post `
            -Body $payload `
            -ContentType "application/json" `
            -TimeoutSec 60

        Write-Host "<<< AGENT REPOND: $($result.status)" -ForegroundColor Green
        Write-Host "<<< TIMESTAMP: $($result.timestamp)" -ForegroundColor Gray

        if ($result.result) {
            Write-Host "<<< RESULTAT:" -ForegroundColor Cyan
            $result.result | ConvertTo-Json -Depth 3 | Write-Host -ForegroundColor White
        }

        # Sauvegarder le resultat
        $logDir = "logs/autonomous_missions"
        New-Item -Path $logDir -ItemType Directory -Force | Out-Null
        $logFile = "$logDir/$Agent`_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
        $result | ConvertTo-Json -Depth 10 | Out-File -FilePath $logFile -Encoding UTF8
        Write-Host "<<< LOG SAUVEGARDE: $logFile" -ForegroundColor Gray

        return $result
    } catch {
        Write-Host "<<< ERREUR: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# =============================================================================
# MISSION 1: MonitoringAgent - Scan REEL de l'infrastructure
# =============================================================================
Write-Host @"

=================================================================
[MISSION 1/5] MONITORINGAGENT - SCAN INFRASTRUCTURE REEL
=================================================================
L'agent va VRAIMENT scanner:
  - CPU/RAM/Disk en temps reel
  - Services Docker actifs
  - Ports ouverts
  - GPU NVIDIA status

L'agent fait le travail, pas moi !
=================================================================

"@ -ForegroundColor Cyan

$m1 = Send-RealMission -Agent "monitoringagent" -Mission "health_check" -Context @{
    check_type = "full_system"
    include_gpu = $true
    include_services = $true
    include_ports = $true
    generate_report = $true
    alert_on_issues = $true
}

Start-Sleep -Seconds 3

# =============================================================================
# MISSION 2: BackupAgent - Backup REEL maintenant
# =============================================================================
Write-Host @"

=================================================================
[MISSION 2/5] BACKUPAGENT - BACKUP REEL MAINTENANT
=================================================================
L'agent va VRAIMENT:
  - Dumper PostgreSQL
  - Sauvegarder Redis
  - Archiver configs
  - Uploader vers stockage

Backup REEL, pas une simulation !
=================================================================

"@ -ForegroundColor Cyan

$m2 = Send-RealMission -Agent "backupagent" -Mission "create_backup" -Context @{
    backup_type = "full"
    include_database = $true
    include_redis = $true
    include_configs = $true
    compress = $true
    timestamp = (Get-Date).ToString("yyyy-MM-dd_HH-mm-ss")
}

Start-Sleep -Seconds 3

# =============================================================================
# MISSION 3: SyncAgent - Synchronisation REELLE Redis <-> PostgreSQL
# =============================================================================
Write-Host @"

=================================================================
[MISSION 3/5] SYNCAGENT - SYNC REDIS <-> POSTGRESQL
=================================================================
L'agent va VRAIMENT:
  - Lire les caches Redis
  - Verifier la coherence avec PostgreSQL
  - Synchroniser les donnees
  - Logger les differences

Sync REEL des donnees !
=================================================================

"@ -ForegroundColor Cyan

$m3 = Send-RealMission -Agent "syncagent" -Mission "sync_cache" -Context @{
    sync_type = "bidirectional"
    check_consistency = $true
    auto_fix = $true
    log_differences = $true
}

Start-Sleep -Seconds 3

# =============================================================================
# MISSION 4: ClassifierAgent - Analyse REELLE des logs
# =============================================================================
Write-Host @"

=================================================================
[MISSION 4/5] CLASSIFIERAGENT - ANALYSE LOGS REELS
=================================================================
L'agent va VRAIMENT:
  - Lire les logs Docker
  - Classifier les erreurs
  - Detecter les patterns
  - Generer des tickets si problemes

Analyse REELLE, pas du fake !
=================================================================

"@ -ForegroundColor Cyan

$m4 = Send-RealMission -Agent "classifieragent" -Mission "analyze_logs" -Context @{
    log_sources = @("docker", "api", "prometheus")
    time_range = "1h"
    classify_errors = $true
    create_tickets = $true
    priority_threshold = "medium"
}

Start-Sleep -Seconds 3

# =============================================================================
# MISSION 5: MaestroAgent - Orchestration COMPLETE
# =============================================================================
Write-Host @"

=================================================================
[MISSION 5/5] MAESTROAGENT - ORCHESTRATION COMPLETE
=================================================================
L'agent va VRAIMENT:
  - Coordonner tous les autres agents
  - Verifier les resultats
  - Decider des prochaines actions
  - Generer rapport executif

Le chef orchestre TOUT !
=================================================================

"@ -ForegroundColor Cyan

$m5 = Send-RealMission -Agent "maestroorchestratoragent" -Mission "orchestrate" -Context @{
    workflow = "system_health_and_maintenance"
    agents_to_coordinate = @(
        "monitoringagent",
        "backupagent",
        "syncagent",
        "classifieragent"
    )
    auto_resolve_issues = $true
    generate_executive_report = $true
}

# =============================================================================
# RESUME FINAL
# =============================================================================
Write-Host @"

=================================================================
          MISSIONS AUTONOMES - RESULTATS REELS
=================================================================

"@ -ForegroundColor Green

$totalSuccess = 0
$totalFailed = 0

if ($m1 -and $m1.status -eq "completed") {
    Write-Host "[1] MonitoringAgent: SUCCESS" -ForegroundColor Green
    Write-Host "    CPU: $($m1.result.metrics.cpu_usage)" -ForegroundColor Gray
    Write-Host "    Memory: $($m1.result.metrics.memory_usage)" -ForegroundColor Gray
    Write-Host "    Disk: $($m1.result.metrics.disk_usage)" -ForegroundColor Gray
    $totalSuccess++
} else {
    Write-Host "[1] MonitoringAgent: FAILED" -ForegroundColor Red
    $totalFailed++
}

if ($m2 -and $m2.status -eq "completed") {
    Write-Host "`n[2] BackupAgent: SUCCESS" -ForegroundColor Green
    Write-Host "    Backup cree: $($m2.result.backup_file)" -ForegroundColor Gray
    $totalSuccess++
} else {
    Write-Host "`n[2] BackupAgent: FAILED" -ForegroundColor Red
    $totalFailed++
}

if ($m3 -and $m3.status -eq "completed") {
    Write-Host "`n[3] SyncAgent: SUCCESS" -ForegroundColor Green
    Write-Host "    Sync execute" -ForegroundColor Gray
    $totalSuccess++
} else {
    Write-Host "`n[3] SyncAgent: FAILED" -ForegroundColor Red
    $totalFailed++
}

if ($m4 -and $m4.status -eq "completed") {
    Write-Host "`n[4] ClassifierAgent: SUCCESS" -ForegroundColor Green
    Write-Host "    Logs analyses" -ForegroundColor Gray
    $totalSuccess++
} else {
    Write-Host "`n[4] ClassifierAgent: FAILED" -ForegroundColor Red
    $totalFailed++
}

if ($m5 -and $m5.status -eq "completed") {
    Write-Host "`n[5] MaestroAgent: SUCCESS" -ForegroundColor Green
    Write-Host "    Orchestration complete" -ForegroundColor Gray
    $totalSuccess++
} else {
    Write-Host "`n[5] MaestroAgent: FAILED" -ForegroundColor Red
    $totalFailed++
}

Write-Host @"

=================================================================
BILAN: $totalSuccess/5 missions reussies par LES AGENTS EUX-MEMES
=================================================================

Logs detailles dans: logs/autonomous_missions/

Les agents ont VRAIMENT travaille !
Verifie les logs pour voir ce qu'ils ont fait.

Dashboard: http://192.168.0.30:3000/d/twisterlab-agents-fixed

=================================================================

"@ -ForegroundColor Cyan

# Afficher les logs generes
Write-Host "Logs generes par les agents:" -ForegroundColor Yellow
Get-ChildItem -Path "logs/autonomous_missions" -Filter "*.json" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 5 |
    ForEach-Object {
        Write-Host "  - $($_.Name) ($([math]::Round($_.Length/1KB, 2)) KB)" -ForegroundColor Gray
    }
