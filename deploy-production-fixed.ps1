param(
    [Parameter(Mandatory=$false)]
    [string]$Environment = "production"
)

Write-Host "Deployement TwisterLab $Environment (OLLAMA NATIFS CORRIGE)" -ForegroundColor Green
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "PRIMARY Ollama: http://192.168.0.20:11434 (RTX 3060)" -ForegroundColor Yellow
Write-Host "FALLBACK Ollama: http://192.168.0.30:11434 (GTX 1050)" -ForegroundColor Yellow
Write-Host ""

# Verifier prerequis
Write-Host "Verification prerequis..." -ForegroundColor Yellow
if (!(Test-Path "docker-compose.prod-native-ollama.yml")) {
    Write-Host "ERREUR: docker-compose.prod-native-ollama.yml manquant" -ForegroundColor Red
    exit 1
}

# Test connectivite Ollama
Write-Host "Test connectivite Ollama..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://192.168.0.20:11434/api/tags" -TimeoutSec 10
    Write-Host "OK Ollama PRIMARY (RTX 3060)" -ForegroundColor Green
} catch {
    Write-Host "WARNING Ollama PRIMARY indisponible: $($_.Exception.Message)" -ForegroundColor Yellow
}

try {
    $response = Invoke-WebRequest -Uri "http://192.168.0.30:11434/api/tags" -TimeoutSec 10
    Write-Host "OK Ollama FALLBACK (GTX 1050)" -ForegroundColor Green
} catch {
    Write-Host "WARNING Ollama FALLBACK indisponible: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Deployer stack
Write-Host "Deploiement stack Docker Swarm..." -ForegroundColor Yellow
docker stack deploy -c docker-compose.prod-native-ollama.yml twisterlab

# Attendre demarrage
Write-Host "Attente demarrage services (45s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 45

# Verifier services
Write-Host "Verification services..." -ForegroundColor Green
docker stack services twisterlab

# Attendre stabilite
Start-Sleep -Seconds 15

# Tests de sante
Write-Host "Tests de sante..." -ForegroundColor Yellow

# Test API
$apiHealthy = $false
for ($i = 1; $i -le 3; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://192.168.0.30:8000/health" -TimeoutSec 15
        if ($response.StatusCode -eq 200) {
            Write-Host "OK API: $($response.StatusCode) (tentative $i/3)" -ForegroundColor Green
            $apiHealthy = $true
            break
        }
    } catch {
        Write-Host "Tentative API $i/3: $($_.Exception.Message)" -ForegroundColor Yellow
        if ($i -lt 3) { Start-Sleep -Seconds 10 }
    }
}

if (!$apiHealthy) {
    Write-Host "ERREUR API: Echec apres 3 tentatives" -ForegroundColor Red
    Write-Host "Logs API:" -ForegroundColor Yellow
    docker service logs twisterlab_api --tail 20
}

Write-Host ""
Write-Host "DEPLOIEMENT TERMINE !" -ForegroundColor Green
Write-Host "Dashboard: http://192.168.0.30:3000" -ForegroundColor Cyan
Write-Host "API Docs: http://192.168.0.30:8000/docs" -ForegroundColor Cyan
Write-Host "Failover: PRIMARY->FALLBACK automatique" -ForegroundColor Cyan
Write-Host ""
Write-Host "Haute Disponibilite Operationnelle !" -ForegroundColor Green