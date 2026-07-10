@echo off
chcp 65001 >nul
title 科技投资观察站 - 数据服务器
echo ============================================
echo   科技投资观察站 - 数据服务器
echo ============================================
echo.
echo 正在启动 (端口 8765)...
echo.
cd /d E:\投资工具自用
python server.py
pause
