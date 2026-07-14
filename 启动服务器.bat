@echo off
title 科技投资观察站 - 数据服务器
cd /d E:\投资工具自用

echo ============================================
echo   科技投资观察站 - 数据服务器
echo ============================================
echo.

REM 端口占用检查
netstat -ano | findstr ":8765 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [警告] 端口 8765 已被占用，服务器可能已在运行。
    echo.
    echo 如需重启，请先关闭已有的服务器窗口，
    echo 或执行以下命令强制结束所有 Python 进程：
    echo.
    echo     taskkill /F /IM python.exe
    echo.
    pause
    exit /b 1
)

echo 端口 8765 空闲，正在启动服务器...
echo.
echo --------------------------------------------
echo  按 Ctrl+C 可停止服务
echo  直接关闭本窗口也会停止服务
echo --------------------------------------------
echo.
python server.py

echo.
echo ============================================
echo  [提示] 服务器已停止（退出码 %errorlevel%）。
echo ============================================
pause
