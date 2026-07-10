@echo off
cd /d "E:\??????"
echo Starting server...
start /B python -u server.py >nul 2>&1
timeout /t 10 /nobreak >nul
start http://localhost:8765/
echo Browser opened. Server running at http://localhost:8765/
