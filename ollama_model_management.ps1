# Ollama Model Management Script
# Keep only essential models to save GPU memory

Write-Host "Current Ollama models:" -ForegroundColor Cyan
ollama list

Write-Host "
Recommended models to keep:" -ForegroundColor Yellow
Write-Host "  - llama3.2:1b (fast chat, ~1GB VRAM)"
Write-Host "  - llama3:8b (balanced, ~4GB VRAM)"
Write-Host "  - deepseek-r1:latest (reasoning, ~5GB VRAM)"
Write-Host "  - codellama:latest (coding, ~4GB VRAM)"

Write-Host "
To remove unused models:" -ForegroundColor Yellow
Write-Host "  ollama rm <model_name>"
Write-Host "  Example: ollama rm mistral:latest"

Write-Host "
To check GPU memory usage:" -ForegroundColor Yellow
Write-Host "  nvidia-smi --query-gpu=memory.used,memory.total --format=csv"
