@echo off
chcp 65001 >nul
title Blogger Studio Pro - مركز النشر السحابي
cd /d "%~dp0"

echo [1/2] Checking local server...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/hub/status' -TimeoutSec 2; exit 0 } catch { exit 1 }"
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Starting Blogger Studio background server...
    start "" /b python run.py --no-browser
    timeout /t 2 /nobreak >nul
)

echo [2/2] Opening Deployment Hub in Microsoft Edge...
start msedge "http://127.0.0.1:8000/deployment-hub"
if %ERRORLEVEL% NEQ 0 (
    start "" "http://127.0.0.1:8000/deployment-hub"
)
exit /b 0
