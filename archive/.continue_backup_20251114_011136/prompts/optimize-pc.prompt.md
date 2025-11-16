---
description: "Optimisation et amélioration automatique du PC Windows TwisterLab"
---

# Mission : Optimisation PC TwisterLab (2 Heures)

Tu es un expert Windows qui va **diagnostiquer, nettoyer et optimiser** ce PC de développement TwisterLab.

## 🎯 Objectifs

- 🧹 **Nettoyer** : Libérer espace disque, supprimer fichiers temporaires
- ⚡ **Optimiser** : Performance CPU/RAM/Disk, services Windows
- 🔒 **Sécuriser** : Firewall, Windows Update, antivirus
- 📊 **Monitorer** : Installer outils de monitoring manquants

## Phase 1 : Diagnostic Complet (30 min)

### 1.1 Ressources Système
```powershell
# CPU & RAM
Get-WmiObject Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed
Get-WmiObject Win32_ComputerSystem | Select-Object TotalPhysicalMemory
Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 2 -MaxSamples 5

# Disk Space
Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{Name="Used(GB)";Expression={[math]::round($_.Used/1GB,2)}}, @{Name="Free(GB)";Expression={[math]::round($_.Free/1GB,2)}}, @{Name="Total(GB)";Expression={[math]::round(($_.Used+$_.Free)/1GB,2)}}

# Processus lourds
Get-Process | Sort-Object WS -Descending | Select-Object -First 20 Name, @{Name="RAM(MB)";Expression={[math]::round($_.WS/1MB,2)}}, CPU
```

### 1.2 Services Windows
```powershell
# Services en cours
Get-Service | Where-Object {$_.Status -eq 'Running'} | Measure-Object
Get-Service | Where-Object {$_.Status -eq 'Stopped' -and $_.StartType -eq 'Automatic'} | Select-Object DisplayName, Status, StartType

# Services Docker
Get-Service -Name "com.docker.*", "Docker*" | Select-Object Name, Status, StartType
```

### 1.3 Réseau & Connectivité
```powershell
# Interfaces réseau
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
Get-NetIPAddress | Where-Object {$_.AddressFamily -eq 'IPv4'} | Select-Object IPAddress, InterfaceAlias

# Test connectivité infrastructure
Test-Connection -ComputerName 192.168.0.20 -Count 2 -Quiet  # CoreRTX (Ollama)
Test-Connection -ComputerName 192.168.0.30 -Count 2 -Quiet  # edgeserver (API)
Test-NetConnection -ComputerName 192.168.0.20 -Port 11434   # Ollama
Test-NetConnection -ComputerName 192.168.0.30 -Port 8000    # TwisterLab API
```

### 1.4 Logiciels & Dépendances
```powershell
# Python
python --version
pip list | findstr "fastapi ollama httpx pytest"

# Docker
docker --version
docker ps
docker images | Measure-Object

# Git
git --version
git config --global user.name
git config --global user.email
```

### 1.5 Fichiers & Espace Disque
```powershell
# Fichiers volumineux
Get-ChildItem -Path C:\ -Recurse -ErrorAction SilentlyContinue | Where-Object {$_.Length -gt 1GB} | Select-Object FullName, @{Name="Size(GB)";Expression={[math]::round($_.Length/1GB,2)}} | Sort-Object Size -Descending

# Dossiers temp
Get-ChildItem -Path $env:TEMP | Measure-Object -Property Length -Sum | Select-Object @{Name="TempFiles(GB)";Expression={[math]::round($_.Sum/1GB,2)}}

# Logs Docker
Get-ChildItem -Path "C:\ProgramData\Docker\containers" -Recurse -Filter "*.log" -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum

# Cache npm/pip
if (Test-Path "$env:APPDATA\npm-cache") { Get-ChildItem "$env:APPDATA\npm-cache" | Measure-Object -Property Length -Sum }
if (Test-Path "$env:LOCALAPPDATA\pip\cache") { Get-ChildItem "$env:LOCALAPPDATA\pip\cache" | Measure-Object -Property Length -Sum }
```

## Phase 2 : Nettoyage (45 min)

### 2.1 Fichiers Temporaires
```powershell
# Supprimer temp Windows
Remove-Item -Path $env:TEMP\* -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "✅ Temp Windows nettoyé"

# Supprimer temp utilisateur
Remove-Item -Path "$env:USERPROFILE\AppData\Local\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "✅ Temp utilisateur nettoyé"

# Corbeille
Clear-RecycleBin -Force -ErrorAction SilentlyContinue
Write-Host "✅ Corbeille vidée"
```

### 2.2 Docker Cleanup
```powershell
# Supprimer containers arrêtés
docker container prune -f

# Supprimer images non utilisées
docker image prune -a -f

# Supprimer volumes non utilisés
docker volume prune -f

# Supprimer build cache
docker builder prune -a -f

# Statistiques après nettoyage
docker system df
```

### 2.3 Python Cleanup
```powershell
# Supprimer cache pip
pip cache purge

# Supprimer pycache
Get-ChildItem -Path C:\TwisterLab -Recurse -Filter "__pycache__" -Directory -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force

# Supprimer .pyc files
Get-ChildItem -Path C:\TwisterLab -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force
```

### 2.4 Logs & Debug Files
```powershell
# Logs TwisterLab
Get-ChildItem -Path C:\TwisterLab -Filter "*.log" -Recurse -ErrorAction SilentlyContinue | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | Remove-Item -Force

# Debug reports
Get-ChildItem -Path C:\TwisterLab -Filter "debug_report_*.json" -ErrorAction SilentlyContinue | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | Remove-Item -Force

# Pytest cache
if (Test-Path C:\TwisterLab\.pytest_cache) { Remove-Item -Path C:\TwisterLab\.pytest_cache -Recurse -Force }
```

## Phase 3 : Optimisation (30 min)

### 3.1 Services Windows
```powershell
# Désactiver services non utilisés (demander confirmation)
$ServicesToDisable = @(
    "DiagTrack",          # Telemetry
    "dmwappushservice",   # WAP Push
    "SysMain",            # Superfetch (si SSD)
    "WSearch"             # Windows Search (si non utilisé)
)

foreach ($svc in $ServicesToDisable) {
    $service = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($service -and $service.Status -eq 'Running') {
        Write-Host "⚠️  Service $svc détecté - Désactiver ? (peut améliorer performance)"
        # Attendre confirmation utilisateur via Continue
    }
}
```

### 3.2 Performance Réseau
```powershell
# Optimiser TCP/IP
netsh int tcp set global autotuninglevel=normal
netsh int tcp set global chimney=enabled
netsh int tcp set global dca=enabled
netsh int tcp set global netdma=enabled

# Flush DNS
ipconfig /flushdns
Write-Host "✅ Cache DNS vidé"
```

### 3.3 Disk Optimization
```powershell
# Défragmentation (si HDD, skip si SSD)
$diskType = Get-PhysicalDisk | Select-Object -First 1 MediaType
if ($diskType -eq 'HDD') {
    Write-Host "🔄 HDD détecté - Défragmentation recommandée"
    Optimize-Volume -DriveLetter C -Defrag -Verbose
} else {
    Write-Host "✅ SSD détecté - TRIM activé automatiquement"
}

# Analyser erreurs disque
chkdsk C: /scan
```

### 3.4 Mise à Jour Logiciels
```powershell
# Vérifier Python packages obsolètes
pip list --outdated

# Vérifier Docker version
$latestDockerVersion = (Invoke-WebRequest -Uri "https://api.github.com/repos/docker/docker-ce/releases/latest" -UseBasicParsing | ConvertFrom-Json).tag_name
$currentDockerVersion = (docker --version).Split(" ")[2]
Write-Host "Docker actuel: $currentDockerVersion | Dernier: $latestDockerVersion"

# Vérifier Git version
git update-git-for-windows
```

## Phase 4 : Sécurité (15 min)

### 4.1 Firewall
```powershell
# Vérifier état firewall
Get-NetFirewallProfile | Select-Object Name, Enabled

# Vérifier règles Docker
Get-NetFirewallRule -DisplayGroup "Docker" | Select-Object DisplayName, Enabled, Direction, Action

# Vérifier règles TwisterLab
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*TwisterLab*"}
```

### 4.2 Windows Update
```powershell
# Vérifier mises à jour en attente
Get-WindowsUpdate -MicrosoftUpdate

# Historique dernières updates
Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 10 HotFixID, Description, InstalledOn
```

### 4.3 Antivirus
```powershell
# Windows Defender status
Get-MpComputerStatus | Select-Object AMEngineVersion, AMProductVersion, AMServiceEnabled, AntispywareEnabled, AntivirusEnabled, RealTimeProtectionEnabled

# Dernière analyse
Get-MpComputerStatus | Select-Object QuickScanAge, FullScanAge
```

## Phase 5 : Monitoring (20 min)

### 5.1 Installer Outils Manquants
```powershell
# Vérifier si Performance Monitor est configuré
Get-Counter -ListSet * | Where-Object {$_.CounterSetName -like "*Processor*"} | Select-Object CounterSetName, Description

# Créer collecteur de données personnalisé pour TwisterLab
$collectorName = "TwisterLab-Monitor"
if (-not (Get-PerformanceCounterDataCollectorSet -Name $collectorName -ErrorAction SilentlyContinue)) {
    Write-Host "📊 Création du collecteur TwisterLab..."
    # Configuration collecteur personnalisé
}
```

### 5.2 Scripts de Monitoring Automatiques
```powershell
# Créer script de monitoring quotidien
$monitorScript = @"
# TwisterLab Daily Monitor
`$date = Get-Date -Format "yyyy-MM-dd_HH-mm"
`$report = "C:\TwisterLab\reports\daily_monitor_`$date.json"

`$metrics = @{
    timestamp = `$date
    cpu = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples[0].CookedValue
    ram = (Get-Counter '\Memory\% Committed Bytes In Use').CounterSamples[0].CookedValue
    disk_c = (Get-PSDrive C).Free/1GB
    docker_running = (docker ps -q | Measure-Object).Count
    network_errors = (Get-NetAdapterStatistics | Measure-Object -Property ReceivedPacketErrors -Sum).Sum
}

`$metrics | ConvertTo-Json | Out-File `$report
Write-Host "✅ Rapport sauvegardé : `$report"
"@

$monitorScript | Out-File -FilePath "C:\TwisterLab\scripts\daily_monitor.ps1" -Encoding UTF8
Write-Host "✅ Script monitoring créé : C:\TwisterLab\scripts\daily_monitor.ps1"
```

### 5.3 Tâche Planifiée
```powershell
# Créer tâche planifiée pour monitoring quotidien
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\TwisterLab\scripts\daily_monitor.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At "02:00"
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "TwisterLab-DailyMonitor" -Action $action -Trigger $trigger -Principal $principal -Description "Monitoring quotidien TwisterLab" -Force

Write-Host "✅ Tâche planifiée créée : TwisterLab-DailyMonitor (tous les jours à 2h)"
```

## 📊 Rapport Final

Après exécution complète, génère :

```markdown
# 🖥️ Rapport d'Optimisation PC TwisterLab

## Résumé Exécutif
- **Date** : {timestamp}
- **Durée** : {duration}
- **Espace libéré** : {freed_space_gb} GB
- **Performance** : CPU {before_cpu}% → {after_cpu}% | RAM {before_ram}% → {after_ram}%

## 🧹 Nettoyage
- ✅ Fichiers temp supprimés : {temp_files_gb} GB
- ✅ Docker cleanup : {docker_freed_gb} GB
- ✅ Python cache purgé : {python_cache_mb} MB
- ✅ Logs obsolètes : {logs_count} fichiers supprimés

## ⚡ Optimisation
- ✅ Services désactivés : {disabled_services_count}
- ✅ Réseau optimisé (TCP/IP tuning)
- ✅ Disk optimisé ({disk_type})
- ✅ Logiciels mis à jour : {updated_count}

## 🔒 Sécurité
- ✅ Firewall : {firewall_status}
- ✅ Windows Defender : {defender_status}
- ✅ Dernière analyse : {last_scan_date}
- ⚠️  Mises à jour en attente : {pending_updates_count}

## 📊 Monitoring
- ✅ Script monitoring créé
- ✅ Tâche planifiée configurée (quotidienne 2h)
- ✅ Collecteur Performance Monitor actif

## 🔮 Recommandations
1. {recommendation_1}
2. {recommendation_2}
3. {recommendation_3}

## 📈 Métriques Avant/Après
| Métrique | Avant | Après | Gain |
|----------|-------|-------|------|
| CPU Moyen | {before}% | {after}% | {delta}% |
| RAM Utilisée | {before}GB | {after}GB | {delta}GB |
| Disk Libre C: | {before}GB | {after}GB | +{delta}GB |
| Docker Images | {before} | {after} | -{delta} |
| Services Running | {before} | {after} | -{delta} |
```

## 🚀 Lancement

Pour démarrer l'optimisation PC :
```
@prompt optimize-pc
```

Continue va :
1. Diagnostiquer le système (30 min)
2. Demander confirmation avant nettoyages
3. Optimiser performance (30 min)
4. Vérifier sécurité (15 min)
5. Configurer monitoring (20 min)
6. Générer rapport final

**Temps estimé** : ~2 heures
**Espace libéré estimé** : 5-20 GB
**Amélioration performance** : 10-30%
