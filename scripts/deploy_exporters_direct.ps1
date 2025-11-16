# Script de deploiement des exporters Redis et PostgreSQL
# Deploie uniquement les nouveaux services sans perturber le stack existant

# Function to read secret from Docker secret file or environment variable
function Get-Secret {
    param(
        [string]$SecretName,
        [string]$DefaultValue = $null
    )
    $secretPath = "/run/secrets/$SecretName"
    if (Test-Path $secretPath) {
        return (Get-Content $secretPath).Trim()
    }
    $envValue = Get-Item ENV:$SecretName -ErrorAction SilentlyContinue
    if ($envValue) {
        return $envValue.Value
    }
    if ($DefaultValue) {
        return $DefaultValue
    }
    throw "Secret '$SecretName' not found in Docker secrets or environment variables."
}

$RedisPassword = Get-Secret -SecretName "redis_password"
$PostgresPassword = Get-Secret -SecretName "postgres_password"

# 1. Copier le docker-compose sur edgeserver
Write-Host "[1/4] Copie du docker-compose sur edgeserver..." -ForegroundColor Yellow
scp $composeFile "${user}@${edgeserver}:/home/twister/docker-compose.unified.yml"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ECHEC de la copie" -ForegroundColor Red
    exit 1
}
Write-Host "Fichier copie avec succes" -ForegroundColor Green
Write-Host ""

# 2. Deployer les nouveaux services
Write-Host "[2/4] Deploiement des exporters..." -ForegroundColor Yellow
Write-Host "Deploiement de redis-exporter..." -ForegroundColor Cyan
ssh "${user}@${edgeserver}" @"
docker service create \
  --name twisterlab_redis-exporter \
  --network twisterlab_prod \
  --network twisterlab_backend \
  --publish 9121:9121 \
  --constraint 'node.role==manager' \
  --label prometheus.scrape=true \
  --label prometheus.port=9121 \
  --secret redis_password \
  oliver006/redis_exporter:latest \
  --redis.addr=twisterlab_redis:6379 \
  --redis.password-file=/run/secrets/redis_password
"@

Write-Host ""
Write-Host "Deploiement de postgres-exporter..." -ForegroundColor Cyan
ssh "${user}@${edgeserver}" @"
docker service create \
  --name twisterlab_postgres-exporter \
  --network twisterlab_prod \
  --network twisterlab_backend \
  --publish 9187:9187 \
  --constraint 'node.role==manager' \
  --env DATA_SOURCE_NAME='postgresql://twisterlab:$(cat /run/secrets/postgres_password)@twisterlab_postgres:5432/twisterlab_prod?sslmode=disable' \
  --label prometheus.scrape=true \
  --label prometheus.port=9187 \
  --secret postgres_password \
  prometheuscommunity/postgres-exporter:latest
"@

Write-Host ""
Write-Host "Services deployes" -ForegroundColor Green
Write-Host ""

# 3. Attendre le demarrage
Write-Host "[3/4] Attente du demarrage (30 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# 4. Verifier les services
Write-Host "[4/4] Verification des services..." -ForegroundColor Yellow
Write-Host ""
ssh "${user}@${edgeserver}" "docker service ls --filter name=exporter"

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "DEPLOIEMENT TERMINE!" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaine etape: Configurer Prometheus" -ForegroundColor Cyan
Write-Host ""
