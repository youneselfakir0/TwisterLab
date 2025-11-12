#!/bin/sh

# Simple API startup
echo "Starting TwisterLab API..."
cd /app
python -c "import sys; print('Python version:', sys.version)"
python api/main.py
