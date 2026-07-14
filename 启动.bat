@echo off
title 投资观察站 - 启动器
cd /d E:\投资工具自用

echo ============================================
echo   投资观察站 - 一键启动
echo ============================================
echo.

REM 端口占用检查
netstat -ano | findstr ":8765 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [提示] 服务器已在运行，直接打开浏览器...
    start http://localhost:8765/
    ping -n 3 127.0.0.1 >nul
    exit /b 0
)

echo 正在启动数据服务器（独立窗口运行）...
start "投资观察站-服务器" python server.py

echo 等待服务器就绪...
set /a tries=0
:wait_loop
set /a tries+=1
python -c "import urllib.request;urllib.request.urlopen('http://localhost:8765/api/ping',timeout=2)" >nul 2>&1
if %errorlevel% equ 0 goto ready
if %tries% geq 15 goto timeout
echo   尝试 %tries%/15...
ping -n 2 127.0.0.1 >nul
goto wait_loop

:ready
echo [成功] 服务器已就绪！
start http://localhost:8765/
echo 浏览器已打开 http://localhost:8765/
echo.
echo 服务器在独立窗口运行，关闭那个窗口即可停止服务。
ping -n 4 127.0.0.1 >nul
exit /b 0

:timeout
echo [失败] 服务器启动超时（15秒未响应）。
echo 请查看"投资观察站-服务器"窗口的错误信息，
echo 或运行"启动服务器.bat"在前台查看详细日志。
pause
exit /b 1
