#Requires -RunAsAdministrator

Write-Host "🚀 Déploiement TwisterLab avec corrections des dashboards..." -ForegroundColor Green
Write-Host "Date: $(Get-Date)" -ForegroundColor Blue
Write-Host ""

# 1. Nettoyer l'ancien déploiement
Write-Host "🧹 Nettoyage ancien déploiement..." -ForegroundColor Blue
docker stack rm twisterlab_prod 2>$null
docker stack rm twisterlab-monitoring 2>$null
Start-Sleep -Seconds 15

# 2. Supprimer les anciens réseaux si nécessaire
Write-Host "🔧 Nettoyage des réseaux..." -ForegroundColor Blue
docker network rm traefik-net 2>$null
Start-Sleep -Seconds 5

# 3. Créer les réseaux
Write-Host "🌐 Création des réseaux..." -ForegroundColor Blue
docker network create --driver overlay --attachable traefik-net 2>$null
docker network create --driver overlay --attachable twisterlab_prod 2>$null
Start-Sleep -Seconds 5

# 4. Déployer la stack de monitoring corrigée
Write-Host "📊 Déploiement monitoring stack..." -ForegroundColor Blue
docker stack deploy -c docker-compose.monitoring.yml twisterlab-monitoring
Start-Sleep -Seconds 10

# 5. Déployer la stack principale corrigée
Write-Host "🐳 Déploiement production stack..." -ForegroundColor Blue
docker stack deploy -c docker-compose.production.yml twisterlab_prod
Start-Sleep -Seconds 30

# 6. Vérifier les services
Write-Host "🔍 Vérification des services..." -ForegroundColor Blue
$services = docker service ls --filter "name=twisterlab" --format "table {{.Name}}\t{{.Replicas}}\t{{.Ports}}"

if ($services) {
    Write-Host "Services déployés:" -ForegroundColor Green
    $services | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
} else {
    Write-Host "❌ Aucun service déployé" -ForegroundColor Red
    exit 1
}

# 7. Tester les endpoints
Write-Host "`n🧪 Tests des endpoints..." -ForegroundColor Blue
$endpoints = @(
    @{Name="Traefik Dashboard"; Url="http://localhost:8084"; ExpectedCode=200},
    @{Name="OpenWebUI"; Url="http://localhost:8083"; ExpectedCode=200},
    @{Name="Grafana"; Url="http://localhost:3000"; ExpectedCode=200},
    @{Name="Prometheus"; Url="http://localhost:9090"; ExpectedCode=200}
)

$allTestsPassed = $true
foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint.Url -TimeoutSec 15 -ErrorAction Stop
        if ($response.StatusCode -eq $endpoint.ExpectedCode) {
            Write-Host "✅ $($endpoint.Name): HTTP $($response.StatusCode)" -ForegroundColor Green
        } else {
            Write-Host "⚠️  $($endpoint.Name): HTTP $($response.StatusCode) (expected $($endpoint.ExpectedCode))" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ $($endpoint.Name): $($_.Exception.Message)" -ForegroundColor Red
        $allTestsPassed = $false
    }
}

# 8. Configuration DNS automatique
Write-Host "`n🔧 Configuration DNS automatique..." -ForegroundColor Blue
$hostsPath = "$env:windir\System32\drivers\etc\hosts"
$hostsContent = Get-Content $hostsPath -ErrorAction SilentlyContinue

# Nettoyer les anciennes entrées TwisterLab
$hostsContent = $hostsContent | Where-Object { $_ -notmatch "twisterlab\.local" }

# Ajouter les nouvelles entrées
$dnsEntries = @(
    "127.0.0.1 traefik.twisterlab.local",
    "127.0.0.1 webui.twisterlab.local",
    "127.0.0.1 grafana.twisterlab.local",
    "127.0.0.1 prometheus.twisterlab.local",
    "127.0.0.1 api.twisterlab.local"
)

foreach ($entry in $dnsEntries) {
    $hostsContent += $entry
}

# Écrire dans le fichier hosts
$hostsContent | Out-File -FilePath $hostsPath -Encoding ASCII -Force
Write-Host "✅ DNS configuré pour tous les domaines .twisterlab.local" -ForegroundColor Green

# 9. Résumé final
Write-Host "`n🎉 Déploiement terminé !" -ForegroundColor Green

if ($allTestsPassed) {
    Write-Host "✅ Tous les dashboards sont accessibles !" -ForegroundColor Green
} else {
    Write-Host "⚠️  Certains dashboards nécessitent une vérification supplémentaire" -ForegroundColor Yellow
}

Write-Host "`n📋 URLs des dashboards :" -ForegroundColor Blue
Write-Host "  • Traefik Dashboard: http://traefik.twisterlab.local ou http://localhost:8084" -ForegroundColor White
Write-Host "  • OpenWebUI: http://webui.twisterlab.local ou http://localhost:8083" -ForegroundColor White
Write-Host "  • Grafana: http://grafana.twisterlab.local ou http://localhost:3000" -ForegroundColor White
Write-Host "  • Prometheus: http://prometheus.twisterlab.local ou http://localhost:9090" -ForegroundColor White

Write-Host "`n🔍 Pour déboguer davantage :" -ForegroundColor Blue
Write-Host "  • docker service logs twisterlab_prod_traefik" -ForegroundColor White
Write-Host "  • docker service logs twisterlab_prod_webui" -ForegroundColor White
Write-Host "  • docker service logs twisterlab-monitoring_grafana" -ForegroundColor White
