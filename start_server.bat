@echo off
echo Starting TwisterLab API Server...
cd /d C:\TwisterLab
call .\.venv_new\Scripts\activate.bat
python start_server.py
pause