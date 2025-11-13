# GPU Performance Monitoring for Ollama
# Run this in a separate PowerShell window

while ($true) {
    Clear-Host
    Write-Host "=== Ollama GPU Performance Monitor ===" -ForegroundColor Cyan
    Write-Host "Time: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor White

    # GPU usage
    try {
         = nvidia-smi --query-gpu=memory.used,memory.total,temperature.gpu,utilization.gpu --format=csv,noheader,nounits
        if () {
             =  -split ','
            Write-Host "GPU Memory: / MB" -ForegroundColor Green
             = if ([int][2] -gt 80) { "Red" } elseif ([int][2] -gt 70) { "Yellow" } else { "Green" }
            Write-Host "GPU Temp: Â°C" -ForegroundColor 
             = if ([int][3] -gt 90) { "Red" } elseif ([int][3] -gt 80) { "Yellow" } else { "Green" }
            Write-Host "GPU Util: %" -ForegroundColor 
        }
    } catch {
        Write-Host "GPU monitoring unavailable" -ForegroundColor Red
    }

    # Ollama process
    $ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
    if ($ollamaProcess) {
        Write-Host "Ollama CPU: $($ollamaProcess.CPU.ToString('F1'))%" -ForegroundColor Green
        Write-Host "Ollama Memory: $($ollamaProcess.WorkingSet64/1MB -as [int]) MB" -ForegroundColor Green
    } else {
        Write-Host "Ollama not running" -ForegroundColor Yellow
    }

    Start-Sleep -Seconds 5
}
