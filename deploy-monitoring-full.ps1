# Script pour déployer la stack de monitoring complète TwisterLab
param(
    [string]$Server = "192.168.0.30",
    [string]$Username = "twister",
    [string]$RedisPassword = "twisterlab_redis_password"
)

Write-Host ">>> Déploiement de la stack de monitoring complète TwisterLab" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Étape 1: Copier les fichiers de configuration
Write-Host "`n>>> Étape 1: Copie des fichiers de configuration..." -ForegroundColor Yellow

$ConfigFiles = @(
    "docker-compose.monitoring-full.yml",
    "docker-compose.redis.yml",
    "monitoring/prometheus.yml",
    "monitoring/alert_rules.yml",
    "monitoring/alertmanager.yml",
    "monitoring/blackbox.yml"
)

foreach ($file in $ConfigFiles) {
    if (Test-Path $file) {
        Write-Host "Copie de $file vers le serveur..." -ForegroundColor White
        scp $file ${Username}@${Server}:/home/twister/
    } else {
        Write-Warning "Fichier $file non trouvé"
    }
}

# Étape 2: Déployer Redis
Write-Host "`n>>> Étape 2: Déploiement de Redis..." -ForegroundColor Yellow

$RedisEnv = @"
REDIS_PASSWORD=$RedisPassword
"@

ssh ${Username}@${Server} "echo '$RedisEnv' > /home/twister/.env.redis"
ssh ${Username}@${Server} "docker stack deploy -c docker-compose.redis.yml twisterlab"

Start-Sleep -Seconds 10

# Étape 3: Déployer la stack de monitoring complète
Write-Host "`n>>> Étape 3: Déploiement de la stack de monitoring..." -ForegroundColor Yellow

ssh ${Username}@${Server} "docker stack deploy -c docker-compose.monitoring-full.yml twisterlab"

# Étape 4: Attendre que les services soient prêts
Write-Host "`n>>> Étape 4: Attente du démarrage des services..." -ForegroundColor Yellow

Start-Sleep -Seconds 30

# Étape 5: Vérifier l'état des services
Write-Host "`n>>> Étape 5: Vérification de l'état des services..." -ForegroundColor Yellow

$Services = ssh ${Username}@${Server} "docker service ls --filter name=twisterlab --format 'table {{.Name}}\t{{.Replicas}}'"

Write-Host "État des services TwisterLab:" -ForegroundColor Green
Write-Host $Services

# Étape 6: Tester les endpoints de monitoring
Write-Host "`n>>> Étape 6: Test des endpoints de monitoring..." -ForegroundColor Yellow

$Endpoints = @(
    @{Name="Prometheus"; Url="http://$Server`:9090/-/healthy"},
    @{Name="Grafana"; Url="http://$Server`:3000/api/health"},
    @{Name="Node Exporter"; Url="http://$Server`:9100/metrics"},
    @{Name="PostgreSQL Exporter"; Url="http://$Server`:9187/metrics"},
    @{Name="Redis Exporter"; Url="http://$Server`:9121/metrics"},
    @{Name="Alertmanager"; Url="http://$Server`:9093/-/healthy"},
    @{Name="cAdvisor"; Url="http://$Server`:8080/containers/"},
    @{Name="Blackbox Exporter"; Url="http://$Server`:9115/-/healthy"}
)

foreach ($endpoint in $Endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint.Url -TimeoutSec 10 -ErrorAction Stop
        Write-Host "OK $($endpoint.Name) accessible" -ForegroundColor Green
    } catch {
        Write-Host "WARNING $($endpoint.Name) non accessible: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Étape 7: Instructions finales
Write-Host "`nSUCCESS Stack de monitoring déployée!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

Write-Host "`nURLs d'accès:" -ForegroundColor Cyan
Write-Host "• Grafana: http://$Server`:3000 (admin/admin)" -ForegroundColor White
Write-Host "• Prometheus: http://$Server`:9090" -ForegroundColor White
Write-Host "• Alertmanager: http://$Server`:9093" -ForegroundColor White

Write-Host "`nMétriques activées:" -ForegroundColor Cyan
Write-Host "• Système (CPU, RAM, Disque, Réseau)" -ForegroundColor White
Write-Host "• PostgreSQL (connexions, requêtes, taille)" -ForegroundColor White
Write-Host "• Redis (cache, hit rate, opérations)" -ForegroundColor White
Write-Host "• Docker (containers, ressources)" -ForegroundColor White
Write-Host "• API (latence, erreurs, disponibilité)" -ForegroundColor White
Write-Host "• Agents (activité, succès, performance)" -ForegroundColor White
Write-Host "• Alertes automatiques configurées" -ForegroundColor White

Write-Host "`nProchaines étapes:" -ForegroundColor Yellow
Write-Host "1. Vérifier le dashboard Grafana" -ForegroundColor White
Write-Host "2. Configurer les notifications d'alertes" -ForegroundColor White
Write-Host "3. Ajuster les seuils d'alertes si nécessaire" -ForegroundColor White

Write-Host "`nNote: Les métriques des agents TwisterLab nécessitent l'ajout d'un endpoint /metrics dans l'API" -ForegroundColor Magenta
