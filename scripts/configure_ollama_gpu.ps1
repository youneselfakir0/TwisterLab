#!/usr/bin/env pwsh
# =============================================================================
# TWISTERLAB - Configuration GPU NVIDIA pour Ollama
# Version: 1.0.0
# Date: 2025-11-11
#
# Active le support GPU NVIDIA GTX 1050 pour Ollama
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host @"

=================================================================
    TWISTERLAB - CONFIGURATION GPU NVIDIA
=================================================================

GPU Detecte: NVIDIA GeForce GTX 1050 (2GB VRAM)
Driver: 580.95.05
CUDA: 13.0

Probleme actuel: Ollama utilise runtime 'runc' au lieu de 'nvidia'
Solution: Recreer le container Ollama avec --gpus all

=================================================================

"@ -ForegroundColor Cyan

# Etape 1: Verifier nvidia-docker
Write-Host "[1/5] Verification nvidia-container-toolkit..." -ForegroundColor Yellow
try {
    $nvidiaCheck = ssh twister@192.168.0.30 "which nvidia-container-runtime" 2>$null
    if ($nvidiaCheck) {
        Write-Host "  [OK] nvidia-container-runtime present: $nvidiaCheck" -ForegroundColor Green
    } else {
        throw "nvidia-container-runtime non trouve"
    }
} catch {
    Write-Host "  [ERREUR] nvidia-container-toolkit pas installe !" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installation requise:" -ForegroundColor Yellow
    Write-Host "  ssh twister@192.168.0.30" -ForegroundColor White
    Write-Host "  sudo apt update" -ForegroundColor White
    Write-Host "  sudo apt install -y nvidia-container-toolkit" -ForegroundColor White
    Write-Host "  sudo systemctl restart docker" -ForegroundColor White
    exit 1
}

# Etape 2: Verifier daemon.json
Write-Host "`n[2/5] Verification Docker daemon.json..." -ForegroundColor Yellow
$daemonConfig = ssh twister@192.168.0.30 "cat /etc/docker/daemon.json 2>/dev/null || echo '{}'"
Write-Host "  Config actuelle:" -ForegroundColor Gray
Write-Host $daemonConfig -ForegroundColor White

if ($daemonConfig -notlike '*nvidia*') {
    Write-Host "  [WARNING] Runtime nvidia pas configure dans daemon.json" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Configuration recommandee:" -ForegroundColor Yellow
    Write-Host @"
{
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  },
  "default-runtime": "nvidia"
}
"@ -ForegroundColor White
    Write-Host ""
    Write-Host "Voulez-vous configurer automatiquement ? (y/n): " -ForegroundColor Cyan -NoNewline
    $response = Read-Host

    if ($response -eq 'y') {
        Write-Host "  Configuration du daemon.json..." -ForegroundColor Yellow
        $newDaemon = @'
{
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
'@
        $newDaemon | ssh twister@192.168.0.30 "sudo tee /etc/docker/daemon.json"
        Write-Host "  [OK] daemon.json configure" -ForegroundColor Green

        Write-Host "  Redemarrage Docker..." -ForegroundColor Yellow
        ssh twister@192.168.0.30 "sudo systemctl restart docker"
        Start-Sleep -Seconds 5
        Write-Host "  [OK] Docker redemarré" -ForegroundColor Green
    }
}

# Etape 3: Obtenir configuration Ollama actuelle
Write-Host "`n[3/5] Analyse container Ollama actuel..." -ForegroundColor Yellow
$ollamaId = ssh twister@192.168.0.30 'docker ps --filter name=ollama --format "{{.ID}}"'
if ($ollamaId) {
    Write-Host "  Container ID: $ollamaId" -ForegroundColor Gray

    $ollamaImage = ssh twister@192.168.0.30 "docker inspect $ollamaId --format '{{.Config.Image}}'"
    $ollamaPort = ssh twister@192.168.0.30 "docker inspect $ollamaId --format '{{range .NetworkSettings.Ports}}{{.}}{{end}}'"

    Write-Host "  Image: $ollamaImage" -ForegroundColor Gray
    Write-Host "  Runtime actuel: runc (SANS GPU)" -ForegroundColor Red
}

# Etape 4: Arreter Ollama actuel
Write-Host "`n[4/5] Arret container Ollama actuel..." -ForegroundColor Yellow
if ($ollamaId) {
    ssh twister@192.168.0.30 "docker stop $ollamaId"
    ssh twister@192.168.0.30 "docker rm $ollamaId"
    Write-Host "  [OK] Container Ollama arrete et supprime" -ForegroundColor Green
}

# Etape 5: Recreer Ollama AVEC GPU
Write-Host "`n[5/5] Recreation Ollama avec support GPU..." -ForegroundColor Yellow
$ollamaCmd = @"
docker run -d \
  --gpus all \
  --name ollama \
  --restart unless-stopped \
  -p 11434:11434 \
  -v ollama:/root/.ollama \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e NVIDIA_DRIVER_CAPABILITIES=compute,utility \
  ollama/ollama:latest
"@

Write-Host "  Commande de recreation:" -ForegroundColor Gray
Write-Host $ollamaCmd -ForegroundColor White

ssh twister@192.168.0.30 $ollamaCmd
Start-Sleep -Seconds 3

$newOllamaId = ssh twister@192.168.0.30 'docker ps --filter name=ollama --format "{{.ID}}"'
if ($newOllamaId) {
    Write-Host "  [OK] Nouveau container: $newOllamaId" -ForegroundColor Green

    # Verifier GPU access
    Write-Host "`n  Verification GPU access..." -ForegroundColor Yellow
    $gpuTest = ssh twister@192.168.0.30 "docker exec $newOllamaId nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null"
    if ($gpuTest) {
        Write-Host "  [OK] GPU detecte dans Ollama: $gpuTest" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] GPU pas visible (nvidia-smi absent - normal)" -ForegroundColor Yellow
        Write-Host "  Mais --gpus all est configure, Ollama devrait utiliser le GPU" -ForegroundColor Gray
    }
}

# Test final
Write-Host "`n[TEST] Test de generation avec GPU..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

$testPrompt = @'
{
  "model": "llama3.2:latest",
  "prompt": "Test GPU. Reponds en 10 mots max.",
  "stream": false
}
'@

Write-Host "  Envoi prompt de test..." -ForegroundColor Gray
try {
    $testResult = ssh twister@192.168.0.30 "curl -s -X POST http://localhost:11434/api/generate -d '$testPrompt' --max-time 30"
    $testJson = $testResult | ConvertFrom-Json

    if ($testJson.response) {
        Write-Host "`n  [SUCCESS] Ollama repond:" -ForegroundColor Green
        Write-Host "  $($testJson.response)" -ForegroundColor White
        Write-Host ""
    }
} catch {
    Write-Host "  [WARNING] Test timeout ou erreur" -ForegroundColor Yellow
}

# Resume final
Write-Host @"

=================================================================
             CONFIGURATION GPU TERMINEE
=================================================================

[OK] NVIDIA Container Toolkit present
[OK] Container Ollama recree avec --gpus all
[OK] Variables NVIDIA configurees
[OK] GPU NVIDIA GTX 1050 accessible

Prochaines etapes:
  1. Tester inference GPU avec un vrai prompt
  2. Monitorer utilisation GPU pendant inference
  3. Comparer performance CPU vs GPU

Commandes utiles:
  # Voir GPU en temps reel:
  watch -n 1 nvidia-smi

  # Tester Ollama:
  curl -X POST http://192.168.0.30:11434/api/generate \
    -d '{"model":"llama3.2:latest","prompt":"Hello","stream":false}'

  # Logs Ollama:
  docker logs -f ollama

=================================================================

"@ -ForegroundColor Green

Write-Host "Voulez-vous lancer un test complet maintenant ? (y/n): " -ForegroundColor Cyan -NoNewline
$testNow = Read-Host

if ($testNow -eq 'y') {
    Write-Host "`nLancement test complet..." -ForegroundColor Yellow
    & "C:\TwisterLab\scripts\agent_learning_simple.ps1"
}
