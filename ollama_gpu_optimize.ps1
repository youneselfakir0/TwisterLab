# Ollama GPU Optimization Script
# Generated for RTX 3060 (4GB VRAM)

# Set environment variables for GPU optimization
$env:OLLAMA_GPU_LAYERS = "35"  # Adjust based on model size
$env:OLLAMA_MAX_LOADED_MODELS = "2"  # Limit concurrent models
$env:OLLAMA_NUM_THREAD = "-1"  # Auto-detect CPU threads
$env:OLLAMA_NUM_GPU = "1"  # Use 1 GPU

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
