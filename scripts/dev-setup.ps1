param(
    [switch]$Force
)

# dev-setup.ps1 - Prepare local dev environment and venv (Windows PowerShell)
# Usage: .\scripts\dev-setup.ps1 [-Force]

function Get-PythonVersion {
    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) { return $null }
    $out = & python -c "import sys,json; print(json.dumps({'major':sys.version_info.major,'minor':sys.version_info.minor,'micro':sys.version_info.micro}))"
    try { return (ConvertFrom-Json $out) } catch { return $null }
}

$pv = Get-PythonVersion
if (-not $pv) {
    Write-Error "Could not find 'python' in PATH. Install Python 3.11 and ensure 'python' points to it."
    exit 1
}

$major = $pv.major
$minor = $pv.minor

Write-Host "Detected Python version: $major.$minor"
if (($major -ne 3 -or $minor -ne 11) -and (-not $Force)) {
    Write-Error "Recommended Python version is 3.11.x (CI uses Python 3.11).\nRun with -Force to override, or install 3.11 and re-run this script."
    exit 1
}

$venvPath = Join-Path -Path $PSScriptRoot -ChildPath "..\.venv" | Resolve-Path -Relative
$venvFullPath = Join-Path -Path $PSScriptRoot -ChildPath "..\.venv"

if (-not (Test-Path $venvFullPath)) {
    Write-Host "Creating virtual environment at .venv..."
    & python -m venv $venvFullPath
}

Write-Host "Installing required packages from requirements.txt into venv..."
$pip = Join-Path $venvFullPath 'Scripts\pip.exe'
if (-not (Test-Path $pip)) { $pip = 'python -m pip' }
& $pip install --upgrade pip
& $pip install -r (Join-Path -Path $PSScriptRoot -ChildPath "..\requirements.txt")

Write-Host "Dev setup complete. Activate the venv with:`n  & .\.venv\Scripts\Activate.ps1"
Write-Host "Then run tests via:`n  python -m pytest -q -m 'not e2e'"
