@echo off
cd /d "%~dp0backend"
pip install -r requirements.txt -q
echo Starting WinOptimizer...
python app.py
pause