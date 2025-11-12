#!/usr/bin/env pwsh
# TwisterLab - Missions d'apprentissage agents (version simplifiee)

$ErrorActionPreference = "Continue"

Write-Host "`n==================================================================" -ForegroundColor Cyan
Write-Host "  TWISTERLAB - MISSIONS D'APPRENTISSAGE AGENTS" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "GPU: NVIDIA GeForce GTX 1050 (2GB VRAM, CUDA 13.0)" -ForegroundColor Yellow
Write-Host ""

# Fonction pour envoyer une mission
function Send-Mission {
    param(
        [string]$Agent,
        [string]$Operation,
        [hashtable]$Context
    )

    $payload = @{
        operation = $Operation
        context = $Context
    } | ConvertTo-Json -Depth 5

    Write-Host "[MISSION] $Agent -> $Operation" -ForegroundColor Yellow

    try {
        $result = Invoke-RestMethod `
            -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents/$Agent/execute" `
            -Method Post `
            -Body $payload `
            -ContentType "application/json"

        Write-Host "  [OK] $($result.status) - $($result.timestamp)" -ForegroundColor Green
        return $result
    } catch {
        Write-Host "  [ERROR] $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# MISSION 1: MonitoringAgent - Health check complet
Write-Host "`n[1/4] MonitoringAgent - Analyse infrastructure" -ForegroundColor Cyan
$m1 = Send-Mission -Agent "monitoringagent" -Operation "health_check" -Context @{
    check_type = "full_system"
    include_gpu = $true
    generate_report = $true
}

if ($m1) {
    Write-Host "  CPU: $($m1.result.metrics.cpu_usage)" -ForegroundColor Gray
    Write-Host "  Memory: $($m1.result.metrics.memory_usage)" -ForegroundColor Gray
    Write-Host "  Disk: $($m1.result.metrics.disk_usage)" -ForegroundColor Gray
}

Start-Sleep -Seconds 2

# MISSION 2: Test Ollama avec GPU
Write-Host "`n[2/4] Test Ollama + GPU NVIDIA GTX 1050" -ForegroundColor Cyan
try {
    $tags = Invoke-RestMethod -Uri "http://192.168.0.30:11434/api/tags" -Method Get -TimeoutSec 5
    Write-Host "  Modeles disponibles: $($tags.models.Count)" -ForegroundColor Green

    foreach ($model in $tags.models) {
        $sizeGB = [math]::Round($model.size / 1GB, 2)
        Write-Host "    - $($model.name) ($sizeGB GB)" -ForegroundColor Gray
    }

    if ($tags.models.Count -gt 0) {
        $modelName = $tags.models[0].name
        Write-Host "`n  Test de generation avec $modelName..." -ForegroundColor Yellow

        $promptData = @{
            model = $modelName
            prompt = "Analyse TwisterLab infrastructure et suggere 3 optimisations. Francais, 100 mots max."
            stream = $false
        } | ConvertTo-Json

        $start = Get-Date
        $response = Invoke-RestMethod `
            -Uri "http://192.168.0.30:11434/api/generate" `
            -Method Post `
            -Body $promptData `
            -ContentType "application/json" `
            -TimeoutSec 120
        $duration = ((Get-Date) - $start).TotalSeconds

        Write-Host "  [OK] Reponse generee en $([math]::Round($duration, 2))s" -ForegroundColor Green
        Write-Host "`n--- REPONSE OLLAMA ---" -ForegroundColor Cyan
        Write-Host $response.response -ForegroundColor White
        Write-Host "--- FIN ---`n" -ForegroundColor Cyan

        # Sauvegarder le test
        $testLog = @{
            timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            model = $modelName
            gpu = "NVIDIA GTX 1050"
            cuda = "13.0"
            duration_sec = $duration
            response_length = $response.response.Length
            response = $response.response
        }

        New-Item -Path "logs" -ItemType Directory -Force | Out-Null
        $logFile = "logs/ollama_gpu_test_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
        $testLog | ConvertTo-Json -Depth 5 | Out-File -FilePath $logFile -Encoding UTF8
        Write-Host "  Log sauvegarde: $logFile" -ForegroundColor Gray
    }
} catch {
    Write-Host "  [WARNING] Ollama non accessible: $($_.Exception.Message)" -ForegroundColor Yellow
}

# MISSION 3: Structure report
Write-Host "`n[3/4] Analyse structure systeme" -ForegroundColor Cyan
$structureReport = @{
    timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    gpu = @{
        model = "NVIDIA GeForce GTX 1050"
        vram = "2GB"
        driver = "580.95.05"
        cuda = "13.0"
    }
    services = @()
    agents = @()
}

Write-Host "  Scanning Docker services..." -ForegroundColor Yellow
try {
    $svcList = ssh twister@192.168.0.30 "docker service ls --format '{{.Name}}:{{.Replicas}}'" 2>$null
    if ($svcList) {
        $structureReport.services = $svcList -split "`n" | Where-Object { $_ -ne "" }
        Write-Host "  [OK] $($structureReport.services.Count) services detectes" -ForegroundColor Green
    }
} catch {
    Write-Host "  [WARNING] Impossible de scanner services" -ForegroundColor Yellow
}

Write-Host "  Scanning agents..." -ForegroundColor Yellow
try {
    $agentList = Invoke-RestMethod -Uri "http://192.168.0.30:8000/api/v1/autonomous/agents" -Method Get
    if ($agentList.agents) {
        $structureReport.agents = $agentList.agents | Select-Object name, status, priority
        Write-Host "  [OK] $($structureReport.agents.Count) agents actifs" -ForegroundColor Green
    }
} catch {
    Write-Host "  [WARNING] Impossible de scanner agents" -ForegroundColor Yellow
}

$reportFile = "logs/structure_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$structureReport | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportFile -Encoding UTF8
Write-Host "  Rapport sauvegarde: $reportFile" -ForegroundColor Gray

# MISSION 4: Schedule de tests
Write-Host "`n[4/4] Configuration tests automatiques" -ForegroundColor Cyan

$schedule = @"
# TWISTERLAB - Schedule de tests automatiques
# Genere: $(Get-Date)

TESTS PERIODIQUES:

1. Health Check (toutes les 5 min):
   Invoke-RestMethod -Uri http://192.168.0.30:8000/api/v1/autonomous/agents/monitoringagent/execute -Method Post -Body '{\"operation\":\"health_check\",\"context\":{\"check_type\":\"full_system\"}}'

2. Test Ollama GPU (toutes les heures):
   pwsh -File C:\TwisterLab\scripts\agent_learning_simple.ps1

3. Backup (toutes les 6h):
   Invoke-RestMethod -Uri http://192.168.0.30:8000/api/v1/autonomous/agents/backupagent/execute -Method Post -Body '{\"operation\":\"create_backup\"}'

MONITORING:
- Dashboard: http://192.168.0.30:3000/d/twisterlab-agents-fixed
- Logs: C:\TwisterLab\logs\
- API: http://192.168.0.30:8000/api/v1/autonomous/status
"@

$scheduleFile = "logs/test_schedule.txt"
$schedule | Out-File -FilePath $scheduleFile -Encoding UTF8
Write-Host "  Schedule cree: $scheduleFile" -ForegroundColor Gray

# RESUME FINAL
Write-Host "`n==================================================================" -ForegroundColor Green
Write-Host "  MISSIONS COMPLETEES" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "[1] Infrastructure analysee" -ForegroundColor White
Write-Host "    Services: $($structureReport.services.Count)" -ForegroundColor Gray
Write-Host "    Agents: $($structureReport.agents.Count)/7 actifs" -ForegroundColor Gray
Write-Host ""
Write-Host "[2] Ollama GPU teste" -ForegroundColor White
Write-Host "    GPU: NVIDIA GTX 1050 (2GB)" -ForegroundColor Gray
Write-Host "    CUDA: 13.0" -ForegroundColor Gray
Write-Host "    Logs: logs/ollama_gpu_test_*.json" -ForegroundColor Gray
Write-Host ""
Write-Host "[3] Structure documentee" -ForegroundColor White
Write-Host "    Rapport: $reportFile" -ForegroundColor Gray
Write-Host ""
Write-Host "[4] Tests automatiques configures" -ForegroundColor White
Write-Host "    Schedule: $scheduleFile" -ForegroundColor Gray
Write-Host ""
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "NEXT: Configurer cron job pour automatisation complete" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Green
