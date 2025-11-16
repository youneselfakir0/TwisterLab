Write-Host "Installing Playwright Python and browsers..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install
Write-Host "Playwright installation complete."
