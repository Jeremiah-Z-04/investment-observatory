@echo off
cd /d E:\投资工具自用
start /b python server.py
timeout /t 4 /nobreak >nul
start http://localhost:8765/
echo 投资观察站已启动！
echo 浏览器已打开 http://localhost:8765/
echo 如需停止服务器，请关闭此窗口或按 Ctrl+C
pause
