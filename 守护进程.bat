@echo off
title 投资观察站 - 进程自愈守护
cd /d E:\投资工具自用

echo ============================================
echo   投资观察站 - 进程自愈守护 (watchdog)
echo ============================================
echo.
echo 守护进程将持续监控 8765 端口，服务崩溃后自动拉起。
echo 停止方式：在同一目录创建 watchdog.stop 文件，或关闭本窗口。
echo 服务运行日志：server_runtime.log   守护日志：watchdog.log
echo.

python watchdog.py
pause
