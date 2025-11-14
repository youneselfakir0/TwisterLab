# TwisterLab v1.0.0 - GPU Optimization for Ollama
# Phase 1: Fondation Infrastructure - GPU Optimization
# Date: November 13, 2025
# Author: GitHub Copilot (LLM DevOps Expert)

Write-Host "=== GPU Optimization for Ollama ===" -ForegroundColor Cyan
Write-Host "Optimizing RTX 3060 for AI workloads..." -ForegroundColor Yellow
Write-Host ""

# Check GPU status
Write-Host "1. CHECKING GPU STATUS" -ForegroundColor Green
try {
    $gpu = Get-WmiObject Win32_VideoController | Where-Object { $_.Name -like "*RTX*" -or $_.Name -like "*NVIDIA*" }
    if ($gpu) {
        Write-Host "GPU Found: $($gpu.Name)" -ForegroundColor Green
        Write-Host "VRAM: $([math]::Round($gpu.AdapterRAM/1GB,1))GB" -ForegroundColor Green
        Write-Host "Driver: $($gpu.DriverVersion)" -ForegroundColor Green
    } else {
        Write-Host "ERROR: No NVIDIA GPU detected!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERROR: Could not check GPU: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Check Ollama installation
Write-Host "`n2. CHECKING OLLAMA INSTALLATION" -ForegroundColor Green
try {
    $ollamaPath = Get-Command ollama -ErrorAction SilentlyContinue
    if ($ollamaPath) {
        Write-Host "Ollama found at: $($ollamaPath.Source)" -ForegroundColor Green
        $ollamaVersion = & ollama --version 2>$null
        Write-Host "Version: $ollamaVersion" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Ollama not found in PATH!" -ForegroundColor Red
        Write-Host "Please install Ollama from: https://ollama.com/download" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "ERROR: Could not check Ollama: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Check current models
Write-Host "`n3. CHECKING CURRENT MODELS" -ForegroundColor Green
try {
    $models = & ollama list 2>$null
    if ($models) {
        Write-Host "Current models:" -ForegroundColor Green
        $models | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
    } else {
        Write-Host "No models currently installed" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: Could not list models: $($_.Exception.Message)" -ForegroundColor Red
}

# GPU Memory optimization
Write-Host "`n4. GPU MEMORY OPTIMIZATION" -ForegroundColor Green

# Calculate available VRAM (leave 1GB for system)
$gpuVRAM = [math]::Round($gpu.AdapterRAM/1GB,1)
$availableVRAM = $gpuVRAM - 1  # Reserve 1GB for system
Write-Host "Total GPU VRAM: ${gpuVRAM}GB" -ForegroundColor White
Write-Host "Available for AI: ${availableVRAM}GB" -ForegroundColor White

# Create optimized model configurations
Write-Host "`n5. CREATING OPTIMIZED MODEL CONFIGS" -ForegroundColor Green

# Model size recommendations based on available VRAM
$recommendations = @()

if ($availableVRAM -ge 8) {
    $recommendations += "Large models (8B-70B parameters) with 4-bit quantization"
    $maxModelSize = "70B"
} elseif ($availableVRAM -ge 6) {
    $recommendations += "Medium models (3B-13B parameters) with 4-bit quantization"
    $maxModelSize = "13B"
} elseif ($availableVRAM -ge 4) {
    $recommendations += "Small models (1B-3B parameters) with 4-bit quantization"
    $maxModelSize = "3B"
} else {
    $recommendations += "Very small models (<1B parameters) or CPU fallback"
    $maxModelSize = "1B"
}

$recommendations | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }

# Create optimization script
Write-Host "`n6. CREATING GPU OPTIMIZATION SCRIPT" -ForegroundColor Green

$optimizationScript = @"
# Ollama GPU Optimization Script
# Generated for RTX 3060 (${gpuVRAM}GB VRAM)

# Set environment variables for GPU optimization
`$env:OLLAMA_GPU_LAYERS = "35"  # Adjust based on model size
`$env:OLLAMA_MAX_LOADED_MODELS = "2"  # Limit concurrent models
`$env:OLLAMA_NUM_THREAD = "-1"  # Auto-detect CPU threads
`$env:OLLAMA_NUM_GPU = "1"  # Use 1 GPU

# Model recommendations for your GPU:
# - llama3.2:1b (lightweight, fast)
# - llama3:8b (balanced performance)
# - deepseek-r1:8b (reasoning tasks)
# - codellama:7b (code generation)

# To pull models with GPU acceleration:
# ollama pull llama3.2:1b
# ollama pull llama3:8b

# To run models:
# ollama run llama3.2:1b --gpu

Write-Host "GPU optimization environment variables set!" -ForegroundColor Green
"@

$optimizationScript | Out-File -FilePath "ollama_gpu_optimize.ps1" -Encoding UTF8
Write-Host "Created: ollama_gpu_optimize.ps1" -ForegroundColor Green

# Create model cleanup script
Write-Host "`n7. CREATING MODEL MANAGEMENT SCRIPT" -ForegroundColor Green

$modelManagementScript = @"
# Ollama Model Management Script
# Keep only essential models to save GPU memory

Write-Host "Current Ollama models:" -ForegroundColor Cyan
ollama list

Write-Host "`nRecommended models to keep:" -ForegroundColor Yellow
Write-Host "  - llama3.2:1b (fast chat, ~1GB VRAM)"
Write-Host "  - llama3:8b (balanced, ~4GB VRAM)"
Write-Host "  - deepseek-r1:latest (reasoning, ~5GB VRAM)"
Write-Host "  - codellama:latest (coding, ~4GB VRAM)"

Write-Host "`nTo remove unused models:" -ForegroundColor Yellow
Write-Host "  ollama rm <model_name>"
Write-Host "  Example: ollama rm mistral:latest"

Write-Host "`nTo check GPU memory usage:" -ForegroundColor Yellow
Write-Host "  nvidia-smi --query-gpu=memory.used,memory.total --format=csv"
"@

$modelManagementScript | Out-File -FilePath "ollama_model_management.ps1" -Encoding UTF8
Write-Host "Created: ollama_model_management.ps1" -ForegroundColor Green

# Performance monitoring setup
Write-Host "`n8. SETTING UP PERFORMANCE MONITORING" -ForegroundColor Green

$monitoringScript = @"
# GPU Performance Monitoring for Ollama
# Run this in a separate PowerShell window

while (`$true) {
    Clear-Host
    Write-Host "=== Ollama GPU Performance Monitor ===" -ForegroundColor Cyan
    Write-Host "Time: `$(Get-Date -Format 'HH:mm:ss')" -ForegroundColor White

    # GPU usage
    try {
        $gpuInfo = nvidia-smi --query-gpu=memory.used,memory.total,temperature.gpu,utilization.gpu --format=csv,noheader,nounits
        if ($gpuInfo) {
            $gpuData = $gpuInfo -split ','
            Write-Host "GPU Memory: $($gpuData[0])/$($gpuData[1]) MB" -ForegroundColor Green
            $tempColor = if ([int]$gpuData[2] -gt 80) { "Red" } elseif ([int]$gpuData[2] -gt 70) { "Yellow" } else { "Green" }
            Write-Host "GPU Temp: $($gpuData[2])°C" -ForegroundColor $tempColor
            $utilColor = if ([int]$gpuData[3] -gt 90) { "Red" } elseif ([int]$gpuData[3] -gt 80) { "Yellow" } else { "Green" }
            Write-Host "GPU Util: $($gpuData[3])%" -ForegroundColor $utilColor
        }
    } catch {
        Write-Host "GPU monitoring unavailable" -ForegroundColor Red
    }

    # Ollama process
    `$ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
    if (`$ollamaProcess) {
        Write-Host "Ollama CPU: `$(`$ollamaProcess.CPU.ToString('F1'))%" -ForegroundColor Green
        Write-Host "Ollama Memory: `$(`$ollamaProcess.WorkingSet64/1MB -as [int]) MB" -ForegroundColor Green
    } else {
        Write-Host "Ollama not running" -ForegroundColor Yellow
    }

    Start-Sleep -Seconds 5
}
"@

$monitoringScript | Out-File -FilePath "ollama_gpu_monitor.ps1" -Encoding UTF8
Write-Host "Created: ollama_gpu_monitor.ps1" -ForegroundColor Green

# Summary and recommendations
Write-Host "`n9. OPTIMIZATION SUMMARY" -ForegroundColor Green
Write-Host "GPU: RTX 3060 (${gpuVRAM}GB VRAM)" -ForegroundColor White
Write-Host "Available VRAM: ${availableVRAM}GB for AI workloads" -ForegroundColor White
Write-Host "Max recommended model size: ${maxModelSize} parameters" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run: .\ollama_gpu_optimize.ps1" -ForegroundColor White
Write-Host "2. Run: .\ollama_model_management.ps1" -ForegroundColor White
Write-Host "3. Monitor: .\ollama_gpu_monitor.ps1" -ForegroundColor White
Write-Host "4. Test: ollama run llama3.2:1b --gpu" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "GPU optimization completed!" -ForegroundColor Green
