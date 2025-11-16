# TwisterLab Diagnostic Script
# Vérifie l’état des services Ollama et API, les ports ouverts, et la connectivité réseau
# Usage: Exécuter sur CoreRTX et edgeserver

# --- Vérification Ollama sur CoreRTX ---
Write-Host "[CoreRTX] Vérification du service Ollama..."
try {
    $ollamaStatus = Invoke-Command -ComputerName 192.168.0.20 -ScriptBlock { Get-Service -Name ollama -ErrorAction SilentlyContinue }
    if ($ollamaStatus.Status -eq 'Running') {
        Write-Host "Ollama: OK (en cours d'exécution)"
    } else {
        Write-Host "Ollama: NON DÉMARRÉ"
    }
} catch { Write-Host "Ollama: Erreur d'accès ou service introuvable" }

# --- Vérification TwisterLab API sur edgeserver ---
Write-Host "[edgeserver] Vérification du service TwisterLab API..."
try {
    $apiStatus = Invoke-Command -ComputerName 192.168.0.30 -ScriptBlock { Get-Service -Name twisterlab-api -ErrorAction SilentlyContinue }
    if ($apiStatus.Status -eq 'Running') {
        Write-Host "TwisterLab API: OK (en cours d'exécution)"
    } else {
        Write-Host "TwisterLab API: NON DÉMARRÉ"
    }
} catch { Write-Host "TwisterLab API: Erreur d'accès ou service introuvable" }

# --- Vérification des ports ouverts ---
Write-Host "[CoreRTX] Vérification du port Ollama (11434)..."
try {
    $ollamaPort = Invoke-Command -ComputerName 192.168.0.20 -ScriptBlock { netstat -ano | Select-String ":11434" }
    if ($ollamaPort) {
        Write-Host "Port 11434: OUVERT"
    } else {
        Write-Host "Port 11434: FERMÉ ou non utilisé"
    }
} catch { Write-Host "Port 11434: Erreur d'accès" }

Write-Host "[edgeserver] Vérification du port API (8000)..."
try {
    $apiPort = Invoke-Command -ComputerName 192.168.0.30 -ScriptBlock { netstat -ano | Select-String ":8000" }
    if ($apiPort) {
        Write-Host "Port 8000: OUVERT"
    } else {
        Write-Host "Port 8000: FERMÉ ou non utilisé"
    }
} catch { Write-Host "Port 8000: Erreur d'accès" }

# --- Vérification de la connectivité réseau ---
Write-Host "[CoreRTX] Ping edgeserver..."
try {
    $pingResult = Invoke-Command -ComputerName 192.168.0.20 -ScriptBlock { Test-Connection -ComputerName 192.168.0.30 -Count 2 -Quiet }
    if ($pingResult) {
        Write-Host "Connectivité CoreRTX → edgeserver: OK"
    } else {
        Write-Host "Connectivité CoreRTX → edgeserver: ÉCHEC"
    }
} catch { Write-Host "Ping: Erreur d'accès" }

Write-Host "[edgeserver] Ping CoreRTX..."
try {
    $pingResult2 = Invoke-Command -ComputerName 192.168.0.30 -ScriptBlock { Test-Connection -ComputerName 192.168.0.20 -Count 2 -Quiet }
    if ($pingResult2) {
        Write-Host "Connectivité edgeserver → CoreRTX: OK"
    } else {
        Write-Host "Connectivité edgeserver → CoreRTX: ÉCHEC"
    }
} catch { Write-Host "Ping: Erreur d'accès" }

Write-Host "--- Diagnostic terminé ---"
