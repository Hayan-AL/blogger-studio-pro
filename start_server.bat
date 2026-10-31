@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title Blogger Studio Pro - Local Server (Port 8000)

echo =========================================================================
echo       BLOGGER STUDIO PRO - START SERVER [PORT 8000]
echo =========================================================================

:: Ensure port 8000 is clean
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"

:: Automatically open browser after 2 seconds
start "" /b cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8000/"

:: Locate python
where python.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python run.py --no-browser
    exit /b %ERRORLEVEL%
)

where py.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    py run.py --no-browser
    exit /b %ERRORLEVEL%
)

if exist "C:\Python314\python.exe" (
    "C:\Python314\python.exe" run.py --no-browser
    exit /b %ERRORLEVEL%
)

echo [ERROR] Python was not found in PATH!
pause
exit /b 1
