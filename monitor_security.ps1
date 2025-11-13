# Script de monitoring sÃ©curitÃ© TwisterLab
Write-Host "Monitoring Securite TwisterLab" -ForegroundColor Cyan

# VÃ©rifier le statut du firewall
Write-Host "`nFirewall Status:" -ForegroundColor Yellow
Get-NetFirewallProfile | Format-Table Name, Enabled -AutoSize

# VÃ©rifier les services critiques
Write-Host "`nServices Critiques:" -ForegroundColor Yellow
$criticalServices = @("WinDefend", "SecurityHealthService", "mpssvc")
foreach ($svc in $criticalServices) {
    $service = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($service) {
        $status = if ($service.Status -eq "Running") { "OK" } else { "STOPPED" }
        Write-Host "  $svc : $status" -ForegroundColor $(if ($service.Status -eq "Running") { "Green" } else { "Red" })
    }
}

# VÃ©rifier les ports ouverts
Write-Host "`nPorts a risque:" -ForegroundColor Yellow
$riskyPorts = @("445", "135", "3389", "139", "137")
$listeningPorts = netstat -ano | findstr LISTENING
foreach ($port in $riskyPorts) {
    if ($listeningPorts | Select-String ":$port ") {
        Write-Host "  Port $port : OUVERT (risque)" -ForegroundColor Red
    }
}

# VÃ©rifier les mises Ã  jour
Write-Host "`nStatut Mises a Jour:" -ForegroundColor Yellow
$updateSession = New-Object -ComObject Microsoft.Update.Session
$updateSearcher = $updateSession.CreateUpdateSearcher()
$searchResult = $updateSearcher.Search("IsInstalled=0")
Write-Host "  Mises a jour disponibles: $($searchResult.Updates.Count)" -ForegroundColor $(if ($searchResult.Updates.Count -eq 0) { "Green" } else { "Yellow" })

Write-Host "`nMonitoring termine" -ForegroundColor Green
