# Script pour ouvrir tous les dashboards TwisterLab
# Usage: .\open_dashboards.ps1

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "                                                                      " -ForegroundColor Cyan
Write-Host "        TwisterLab v1.0.0 - DASHBOARDS LAUNCHER                       " -ForegroundColor Cyan
Write-Host "                                                                      " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$edgeserver = "192.168.0.30"

# Vérifier la connectivité
Write-Host "[1] Verification connectivite vers edgeserver ($edgeserver)..." -ForegroundColor Yellow
$ping = Test-Connection -ComputerName $edgeserver -Count 1 -Quiet

if (-not $ping) {
    Write-Host "[X] ERREUR: Impossible de joindre edgeserver ($edgeserver)" -ForegroundColor Red
    Write-Host "    Verifiez votre connexion reseau" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Connectivite OK" -ForegroundColor Green
Write-Host ""

# Dashboards à ouvrir
$dashboards = @(
    @{Name="Grafana"; Port=3000; Desc="Visualisation & Dashboards"},
    @{Name="Prometheus"; Port=9090; Desc="Metriques & Monitoring"},
    @{Name="Jaeger"; Port=16686; Desc="Distributed Tracing"},
    @{Name="AlertManager"; Port=9093; Desc="Gestion des Alertes"},
    @{Name="API"; Port=8000; Desc="TwisterLab API"},
    @{Name="WebUI"; Port=8083; Desc="Ollama AI Assistant"},
    @{Name="Ollama"; Port=11434; Desc="Ollama API"}
)

Write-Host "[2] Ouverture des dashboards:" -ForegroundColor Yellow
Write-Host ""

foreach ($dash in $dashboards) {
    $url = "http://${edgeserver}:$($dash.Port)"
    
    # Tester l'accessibilité
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        Write-Host "  [OK] $($dash.Name) (port $($dash.Port))" -ForegroundColor Green
        Write-Host "       -> $($dash.Desc)" -ForegroundColor Gray
        Write-Host "       -> $url" -ForegroundColor Cyan
        Write-Host ""
        
        # Ouvrir dans le navigateur
        Start-Process $url
        Start-Sleep -Milliseconds 500
        
    } catch {
        Write-Host "  [X] $($dash.Name) (port $($dash.Port)) - Non accessible" -ForegroundColor Red
        Write-Host "      -> $($_.Exception.Message)" -ForegroundColor Gray
        Write-Host ""
    }
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "                                                                      " -ForegroundColor Green  
Write-Host "              DASHBOARDS OUVERTS DANS NAVIGATEUR                      " -ForegroundColor Green
Write-Host "                                                                      " -ForegroundColor Green
Write-Host "  Grafana:       http://$edgeserver:3000                              " -ForegroundColor Green
Write-Host "  Prometheus:    http://$edgeserver:9090                              " -ForegroundColor Green
Write-Host "  Jaeger:        http://$edgeserver:16686                             " -ForegroundColor Green
Write-Host "  AlertManager:  http://$edgeserver:9093                              " -ForegroundColor Green
Write-Host "  API:           http://$edgeserver:8000                              " -ForegroundColor Green
Write-Host "  WebUI:         http://$edgeserver:8083                              " -ForegroundColor Green
Write-Host "  Ollama:        http://$edgeserver:11434                             " -ForegroundColor Green
Write-Host "                                                                      " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "[!] Astuce: Ajoutez ces URLs en favoris pour acces rapide" -ForegroundColor Yellow
Write-Host ""
