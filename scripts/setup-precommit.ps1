# Install pre-commit hooks
Write-Host "Installing pre-commit hooks..." -ForegroundColor Cyan
if (-Not (Get-Command pre-commit -ErrorAction SilentlyContinue)) {
    Write-Host "pre-commit not found. Installing to virtualenv..." -ForegroundColor Yellow
    python -m pip install --user pre-commit
}
pre-commit install
Write-Host "Pre-commit hooks installed." -ForegroundColor Green
