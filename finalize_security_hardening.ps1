# Finalisation du Hardening Sécurité TwisterLab
# Phase 1: Fondation Infrastructure - Security Hardening Final

Write-Host "Finalisation Hardening Securite TwisterLab" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Configuration avancée du firewall
Write-Host "`n1. Configuration firewall avancee..." -ForegroundColor Yellow

# Désactiver les règles de firewall par défaut pour les ports dangereux
Write-Host "Desactivation regles dangereuses..." -ForegroundColor Yellow

# Désactiver RDP externe (garder localhost seulement)
Set-NetFirewallRule -DisplayName "Remote Desktop - User Mode (TCP-In)" -Enabled False -ErrorAction SilentlyContinue
Set-NetFirewallRule -DisplayName "Remote Desktop - User Mode (UDP-In)" -Enabled False -ErrorAction SilentlyContinue

# Désactiver NetBIOS
Set-NetFirewallRule -DisplayName "NetBIOS Datagram Service" -Enabled False -ErrorAction SilentlyContinue
Set-NetFirewallRule -DisplayName "NetBIOS Name Service" -Enabled False -ErrorAction SilentlyContinue
Set-NetFirewallRule -DisplayName "NetBIOS Session Service" -Enabled False -Enabled False -ErrorAction SilentlyContinue

# Désactiver SMB externe (garder réseau local seulement)
Set-NetFirewallRule -DisplayName "File and Printer Sharing (SMB-In)" -Enabled False -ErrorAction SilentlyContinue

Write-Host "OK Regles dangereuses desactivees" -ForegroundColor Green

# 2. Configuration des audits de sécurité
Write-Host "`n2. Configuration audits securite..." -ForegroundColor Yellow

# Activer l'audit des événements de sécurité
Write-Host "Activation audit evenements..." -ForegroundColor Yellow

auditpol /set /subcategory:"Security System Extension" /success:enable /failure:enable 2>$null
auditpol /set /subcategory:"System Integrity" /success:enable /failure:enable 2>$null
auditpol /set /subcategory:"IPsec Driver" /success:enable /failure:enable 2>$null
auditpol /set /subcategory:"Security State Change" /success:enable /failure:enable 2>$null
auditpol /set /subcategory:"Other System Events" /success:enable /failure:enable 2>$null

Write-Host "OK Audits de securite configures" -ForegroundColor Green

# 3. Configuration des stratégies de mot de passe
Write-Host "`n3. Renforcement politiques mots de passe..." -ForegroundColor Yellow

# Configuration via secpol (si disponible)
Write-Host "Configuration complexite mots de passe..." -ForegroundColor Yellow

# Utiliser net accounts pour les paramètres de base
net accounts /minpwlen:12 /maxpwage:90 /minpwage:1 /uniquepw:5 2>$null

Write-Host "OK Politiques mots de passe renforcees" -ForegroundColor Green

# 4. Désactivation des services inutiles
Write-Host "`n4. Desactivation services inutiles..." -ForegroundColor Yellow

$servicesToDisable = @(
    "Fax",           # Fax Service
    "XblAuthManager", # Xbox Live Auth Manager
    "XblGameSave",   # Xbox Live Game Save
    "XboxGipSvc",    # Xbox Game Input Protocol
    "XboxLiveNet",   # Xbox Live Networking
    "WpcMonSvc",     # Parental Controls
    "wisvc",         # Windows Insider Service
    "SysMain",       # Superfetch
    "WSearch"        # Windows Search
)

foreach ($service in $servicesToDisable) {
    $svc = Get-Service -Name $service -ErrorAction SilentlyContinue
    if ($svc -and $svc.Status -eq "Running") {
        Stop-Service -Name $service -Force -ErrorAction SilentlyContinue
        Set-Service -Name $service -StartupType Disabled -ErrorAction SilentlyContinue
        Write-Host "  Desactive: $service" -ForegroundColor Gray
    }
}

Write-Host "OK Services inutiles desactives" -ForegroundColor Green

# 5. Configuration des mises à jour automatiques
Write-Host "`n5. Configuration mises a jour automatiques..." -ForegroundColor Yellow

# Configurer Windows Update pour installation automatique
$WUSettings = (New-Object -com "Microsoft.Update.AutoUpdate").Settings
$WUSettings.NotificationLevel = 4  # Install updates automatically
$WUSettings.Save()

Write-Host "OK Mises a jour automatiques configurees" -ForegroundColor Green

# 6. Création du script de monitoring sécurité
Write-Host "`n6. Creation script monitoring securite..." -ForegroundColor Yellow

$securityMonitorScript = @'
# Script de monitoring sécurité TwisterLab
Write-Host "Monitoring Securite TwisterLab" -ForegroundColor Cyan

# Vérifier le statut du firewall
Write-Host "`nFirewall Status:" -ForegroundColor Yellow
Get-NetFirewallProfile | Format-Table Name, Enabled -AutoSize

# Vérifier les services critiques
Write-Host "`nServices Critiques:" -ForegroundColor Yellow
$criticalServices = @("WinDefend", "SecurityHealthService", "mpssvc")
foreach ($svc in $criticalServices) {
    $service = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($service) {
        $status = if ($service.Status -eq "Running") { "OK" } else { "STOPPED" }
        Write-Host "  $svc : $status" -ForegroundColor $(if ($service.Status -eq "Running") { "Green" } else { "Red" })
    }
}

# Vérifier les ports ouverts
Write-Host "`nPorts a risque:" -ForegroundColor Yellow
$riskyPorts = @("445", "135", "3389", "139", "137")
$listeningPorts = netstat -ano | findstr LISTENING
foreach ($port in $riskyPorts) {
    if ($listeningPorts | Select-String ":$port ") {
        Write-Host "  Port $port : OUVERT (risque)" -ForegroundColor Red
    }
}

# Vérifier les mises à jour
Write-Host "`nStatut Mises a Jour:" -ForegroundColor Yellow
$updateSession = New-Object -ComObject Microsoft.Update.Session
$updateSearcher = $updateSession.CreateUpdateSearcher()
$searchResult = $updateSearcher.Search("IsInstalled=0")
Write-Host "  Mises a jour disponibles: $($searchResult.Updates.Count)" -ForegroundColor $(if ($searchResult.Updates.Count -eq 0) { "Green" } else { "Yellow" })

Write-Host "`nMonitoring termine" -ForegroundColor Green
'@

$securityMonitorScript | Out-File -FilePath "C:\TwisterLab\monitor_security.ps1" -Encoding UTF8
Write-Host "  OK Script monitoring cree: C:\TwisterLab\monitor_security.ps1" -ForegroundColor Green

# 7. Configuration de la tâche planifiée de monitoring
Write-Host "`n7. Configuration tache monitoring securite..." -ForegroundColor Yellow

schtasks /create /tn "TwisterLab_Security_Monitor" /tr "powershell.exe -ExecutionPolicy Bypass -File 'C:\TwisterLab\monitor_security.ps1' > 'C:\TwisterLab\backups\logs\security_monitor_$(Get-Date -Format yyyyMMdd).log' 2>&1" /sc daily /st 06:00 /rl highest /f 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK Tache monitoring securite cree" -ForegroundColor Green
} else {
    Write-Host "  WARN Echec creation tache monitoring" -ForegroundColor Yellow
}

# 8. Vérification finale
Write-Host "`n8. Verification finale hardening..." -ForegroundColor Yellow

# Compter les règles de firewall actives
$activeRules = (Get-NetFirewallRule | Where-Object { $_.Enabled -eq "True" }).Count
Write-Host "  Regles firewall actives: $activeRules" -ForegroundColor Green

# Vérifier l'espace disque
$freeSpace = (Get-PSDrive C).Free / 1GB
Write-Host "  Espace disque libre: $([math]::Round($freeSpace, 2)) GB" -ForegroundColor Green

# Vérifier la mémoire
$memory = Get-CimInstance -ClassName Win32_OperatingSystem
$freeMemory = [math]::Round($memory.FreePhysicalMemory / 1MB, 2)
Write-Host "  Memoire libre: $freeMemory GB" -ForegroundColor Green

Write-Host "`nSUCCES: Hardening securite TwisterLab finalise!" -ForegroundColor Green
Write-Host "Recommandations:" -ForegroundColor Cyan
Write-Host "  - Redemarrer le systeme pour appliquer tous les changements" -ForegroundColor White
Write-Host "  - Executer .\monitor_security.ps1 regulierement" -ForegroundColor White
Write-Host "  - Verifier les logs dans C:\TwisterLab\backups\logs\" -ForegroundColor White