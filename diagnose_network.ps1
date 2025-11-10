# Script de diagnostic réseau TwisterLab
# Usage: .\diagnose_network.ps1

Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║         🔍 TWISTERLAB - DIAGNOSTIC RÉSEAU COMPLET 🔍          ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

$edgeserver = "192.168.0.30"

# 1. Configuration IP locale
Write-Host "`n📡 1. CONFIGURATION IP LOCALE" -ForegroundColor Yellow
Write-Host "═══════════════════════════════`n" -ForegroundColor Gray

$adapters = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"}
foreach ($adapter in $adapters) {
    Write-Host "Interface: $($adapter.InterfaceAlias)" -ForegroundColor Cyan
    Write-Host "  IP: $($adapter.IPAddress)" -ForegroundColor White
    Write-Host "  Subnet: $($adapter.PrefixLength)-bit`n" -ForegroundColor Gray
}

# 2. Passerelle par défaut
Write-Host "🚪 2. PASSERELLE PAR DÉFAUT" -ForegroundColor Yellow
Write-Host "════════════════════════════`n" -ForegroundColor Gray

$gateway = Get-NetRoute -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($gateway) {
    Write-Host "  Gateway: $($gateway.NextHop)" -ForegroundColor Green
} else {
    Write-Host "  ❌ Aucune passerelle configurée" -ForegroundColor Red
}

# 3. Test connectivité edgeserver
Write-Host "`n🔌 3. CONNECTIVITÉ EDGESERVER ($edgeserver)" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════`n" -ForegroundColor Gray

$ping = Test-Connection -ComputerName $edgeserver -Count 4 -ErrorAction SilentlyContinue

if ($ping) {
    $avgTime = ($ping | Measure-Object -Property ResponseTime -Average).Average
    Write-Host "  ✅ Ping réussi" -ForegroundColor Green
    Write-Host "  Temps moyen: $([math]::Round($avgTime, 2)) ms" -ForegroundColor Cyan
    Write-Host "  Paquets: $($ping.Count)/4 reçus`n" -ForegroundColor Gray
} else {
    Write-Host "  ❌ Ping échoué - Serveur injoignable`n" -ForegroundColor Red
}

# 4. Test ports dashboards
Write-Host "🌐 4. TEST PORTS DASHBOARDS" -ForegroundColor Yellow
Write-Host "═══════════════════════════`n" -ForegroundColor Gray

$ports = @(
    @{Name="Grafana"; Port=3000},
    @{Name="Prometheus"; Port=9090},
    @{Name="Jaeger"; Port=16686},
    @{Name="AlertManager"; Port=9093},
    @{Name="API"; Port=8000},
    @{Name="WebUI"; Port=8083}
)

foreach ($service in $ports) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect($edgeserver, $service.Port)
        $tcp.Close()
        Write-Host "  ✅ $($service.Name) (port $($service.Port)): Accessible" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ $($service.Name) (port $($service.Port)): Bloqué" -ForegroundColor Red
    }
}

# 5. Pare-feu Windows
Write-Host "`n🛡️  5. ÉTAT PARE-FEU WINDOWS" -ForegroundColor Yellow
Write-Host "═══════════════════════════`n" -ForegroundColor Gray

$firewallProfiles = Get-NetFirewallProfile
foreach ($profile in $firewallProfiles) {
    $status = if ($profile.Enabled) {"[ON] Active"} else {"[OFF] Desactive"}
    Write-Host "  $($profile.Name): $status" -ForegroundColor $(if($profile.Enabled){'Yellow'}else{'Green'})
}

# 6. Règles pare-feu TwisterLab
Write-Host "`n🔐 6. RÈGLES PARE-FEU TWISTERLAB" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════`n" -ForegroundColor Gray

$rules = Get-NetFirewallRule -DisplayName "TwisterLab-*" -ErrorAction SilentlyContinue
if ($rules) {
    foreach ($rule in $rules) {
        $status = if ($rule.Enabled) {"[OK] Activee"} else {"[X] Desactivee"}
        Write-Host "  $($rule.DisplayName): $status" -ForegroundColor $(if($rule.Enabled){'Green'}else{'Red'})
    }
} else {
    Write-Host "  [!] Aucune regle TwisterLab trouvee" -ForegroundColor Yellow
}

# 7. Test HTTP complet
Write-Host "`n🌐 7. TEST HTTP COMPLET" -ForegroundColor Yellow
Write-Host "═══════════════════════════`n" -ForegroundColor Gray

foreach ($service in $ports) {
    $url = "http://${edgeserver}:$($service.Port)"
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        Write-Host "  ✅ $($service.Name): HTTP $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ $($service.Name): $($_.Exception.Message)" -ForegroundColor Red
    }
}

# CONCLUSION
Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║                    📊 DIAGNOSTIC TERMINÉ                       ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

Write-Host "[!] Si des services sont inaccessibles:" -ForegroundColor Yellow
Write-Host "   1. Verifiez que edgeserver est allume" -ForegroundColor Gray
Write-Host "   2. Verifiez les services Docker" -ForegroundColor Gray
Write-Host "   3. Executez: .\open_dashboards.ps1" -ForegroundColor Gray
Write-Host ""
