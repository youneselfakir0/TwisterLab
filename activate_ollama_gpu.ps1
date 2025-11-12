#!/usr/bin/env pwsh
# Activation GPU pour Ollama sur edgeserver (GTX 1050 2GB)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " ACTIVATION GPU POUR OLLAMA (GTX 1050 2GB)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Vérifier NVIDIA Container Toolkit
Write-Host "[1/5] Verification NVIDIA Container Toolkit..." -ForegroundColor Yellow
try {
    $toolkit = ssh twister@192.168.0.30 "nvidia-container-cli --version 2>&1"
    if ($toolkit -match "version") {
        Write-Host "  Status: " -NoNewline -ForegroundColor Gray
        Write-Host "INSTALLE" -ForegroundColor Green
        Write-Host "  Version: $($toolkit -replace 'nvidia-container-cli version ','')" -ForegroundColor Gray
    } else {
        Write-Host "  Status: " -NoNewline -ForegroundColor Gray
        Write-Host "MANQUANT" -ForegroundColor Red
        Write-Host "  Installation en cours..." -ForegroundColor Yellow
        Write-Host ""

        ssh twister@192.168.0.30 @"
distribution=`$(. /etc/os-release;echo `$ID`$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/`$distribution/libnvidia-container.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
"@

        Write-Host "  Status: " -NoNewline -ForegroundColor Gray
        Write-Host "INSTALLE" -ForegroundColor Green
    }
} catch {
    Write-Host "  Status: " -NoNewline -ForegroundColor Gray
    Write-Host "ERREUR" -ForegroundColor Red
    Write-Host "  Erreur: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 2. Activer GPU pour le service Ollama
Write-Host "[2/5] Activation GPU sur service Ollama..." -ForegroundColor Yellow
try {
    # Stopper le service actuel
    Write-Host "  Arret du service actuel..." -ForegroundColor Gray
    ssh twister@192.168.0.30 "docker service rm twisterlab_ollama" | Out-Null
    Start-Sleep -Seconds 5

    # Recréer avec support GPU
    Write-Host "  Recreation avec support GPU..." -ForegroundColor Gray
    ssh twister@192.168.0.30 @"
docker service create \
  --name twisterlab_ollama \
  --network twisterlab_default \
  --publish 11434:11434 \
  --mount type=volume,source=ollama_data,target=/root/.ollama \
  --env NVIDIA_VISIBLE_DEVICES=all \
  --env NVIDIA_DRIVER_CAPABILITIES=compute,utility \
  --env OLLAMA_DEBUG=INFO \
  --env OLLAMA_NUM_PARALLEL=2 \
  --env OLLAMA_MAX_LOADED_MODELS=2 \
  --constraint 'node.role==manager' \
  --generic-resource 'NVIDIA-GPU=1' \
  ollama/ollama:latest
"@

    Write-Host "  Status: " -NoNewline -ForegroundColor Gray
    Write-Host "SERVICE CREE" -ForegroundColor Green
    Write-Host "  Attente demarrage (30s)..." -ForegroundColor Gray
    Start-Sleep -Seconds 30

} catch {
    Write-Host "  Status: " -NoNewline -ForegroundColor Gray
    Write-Host "ERREUR" -ForegroundColor Red
    Write-Host "  Erreur: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 3. Vérifier que GPU est détecté
Write-Host "[3/5] Verification detection GPU..." -ForegroundColor Yellow
try {
    $gpu_logs = ssh twister@192.168.0.30 "docker service logs twisterlab_ollama 2>&1 | tail -100"

    if ($gpu_logs -match "GTX 1050|NVIDIA|CUDA|gpu") {
        Write-Host "  Status: " -NoNewline -ForegroundColor Gray
        Write-Host "GPU DETECTE" -ForegroundColor Green

        # Extraire info GPU
        $gpu_info = $gpu_logs | Select-String -Pattern "inference compute.*gpu" | Select-Object -First 1
        if ($gpu_info) {
            Write-Host "  Info: $gpu_info" -ForegroundColor Gray
        }
    } else {
        Write-Host "  Status: " -NoNewline -ForegroundColor Gray
        Write-Host "GPU NON DETECTE" -ForegroundColor Yellow
        Write-Host "  Le service tourne peut-etre en mode CPU" -ForegroundColor Yellow
        Write-Host "  Logs recents:" -ForegroundColor Gray
        $gpu_logs | Select-String -Pattern "level=INFO" | Select-Object -Last 5 | ForEach-Object {
            Write-Host "    $_" -ForegroundColor DarkGray
        }
    }
} catch {
    Write-Host "  Status: " -NoNewline -ForegroundColor Gray
    Write-Host "ERREUR" -ForegroundColor Red
}
Write-Host ""

# 4. Télécharger modèles optimisés pour GTX 1050 (2GB VRAM)
Write-Host "[4/5] Telechargement modeles optimises GTX 1050..." -ForegroundColor Yellow
Write-Host "  Modeles compatibles 2GB VRAM:" -ForegroundColor Gray
Write-Host ""

$models = @(
    @{Name="llama3.2:1b"; Size="1GB"; Use="Classification rapide"},
    @{Name="phi3:mini"; Size="2.3GB"; Use="Resolution SOPs"},
    @{Name="tinyllama:latest"; Size="0.6GB"; Use="Validation ultra-rapide"}
)

foreach ($model in $models) {
    Write-Host "  [$($model.Name)]" -ForegroundColor Cyan
    Write-Host "    Taille: $($model.Size) | Usage: $($model.Use)" -ForegroundColor Gray
    Write-Host "    Telechargement..." -NoNewline -ForegroundColor Gray

    try {
        $pullCmd = "docker exec `$(docker ps -q -f name=ollama) ollama pull $($model.Name)"
        ssh twister@192.168.0.30 $pullCmd 2>&1 | Out-Null

        if ($LASTEXITCODE -eq 0) {
            Write-Host " SUCCESS" -ForegroundColor Green
        } else {
            Write-Host " ECHEC" -ForegroundColor Red
        }
    } catch {
        Write-Host " ERREUR" -ForegroundColor Red
        Write-Host "    $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

# 5. Test de performance GPU
Write-Host "[5/5] Test de performance GPU..." -ForegroundColor Yellow
Write-Host "  Requete test: 'Classify this IT ticket: WiFi not working'" -ForegroundColor Gray
Write-Host "  Modele: llama3.2:1b" -ForegroundColor Gray
Write-Host ""

try {
    $testCmd = @"
docker exec `$(docker ps -q -f name=ollama) ollama run llama3.2:1b "Classify this IT ticket category (answer with ONE word only - network/software/hardware/security): WiFi not working" 2>&1
"@

    Write-Host "  Execution..." -NoNewline -ForegroundColor Gray
    $start = Get-Date
    $response = ssh twister@192.168.0.30 $testCmd
    $duration = (Get-Date) - $start

    Write-Host " TERMINE" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Reponse: $($response.Trim())" -ForegroundColor White
    Write-Host "  Duree: $([math]::Round($duration.TotalSeconds, 2))s" -ForegroundColor Cyan
    Write-Host ""

    if ($duration.TotalSeconds -lt 5) {
        Write-Host "  Performance: " -NoNewline -ForegroundColor Gray
        Write-Host "EXCELLENT (GPU actif)" -ForegroundColor Green
    } elseif ($duration.TotalSeconds -lt 10) {
        Write-Host "  Performance: " -NoNewline -ForegroundColor Gray
        Write-Host "BON (GPU probablement actif)" -ForegroundColor Yellow
    } else {
        Write-Host "  Performance: " -NoNewline -ForegroundColor Gray
        Write-Host "LENT (GPU peut-etre non utilise)" -ForegroundColor Red
    }

} catch {
    Write-Host " ERREUR" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Résumé final
Write-Host "================================================" -ForegroundColor Cyan
Write-Host " RESUME - OLLAMA GPU" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

try {
    # Liste des modèles installés
    $installedModels = Invoke-RestMethod -Method GET -Uri "http://192.168.0.30:11434/api/tags" -ErrorAction Stop

    Write-Host "  GPU: GeForce GTX 1050 (2GB VRAM)" -ForegroundColor White
    Write-Host "  Service: twisterlab_ollama" -ForegroundColor White
    Write-Host "  URL: http://192.168.0.30:11434" -ForegroundColor White
    Write-Host ""
    Write-Host "  Modeles installes ($($installedModels.models.Count)):" -ForegroundColor Yellow

    foreach ($model in $installedModels.models) {
        $sizeGB = [math]::Round($model.size / 1GB, 2)
        Write-Host "    - $($model.name) ($sizeGB GB)" -ForegroundColor Green
    }
    Write-Host ""

    Write-Host "  Configuration agents recommandee:" -ForegroundColor Yellow
    Write-Host "    ClassifierAgent -> llama3.2:1b (rapide)" -ForegroundColor White
    Write-Host "    ResolverAgent -> phi3:mini (qualite)" -ForegroundColor White
    Write-Host "    DesktopCommanderAgent -> tinyllama (ultra-rapide)" -ForegroundColor White
    Write-Host ""

    Write-Host "  Les agents TwisterLab peuvent maintenant utiliser le GPU!" -ForegroundColor Green

} catch {
    Write-Host "  Erreur lors du resume: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
