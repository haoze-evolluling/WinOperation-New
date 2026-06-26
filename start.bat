@echo off
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0backend"
echo Starting WinOperation...
start "WinOperation Server" python app.py
timeout /t 2 /nobreak >nul
start http://localhost:5000
pause
