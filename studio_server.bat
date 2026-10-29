@echo off
setlocal
cd /d "%~dp0"
title Blogger Studio Pro - لوحة التحكم الاحترافية (Port 8000)

where powershell.exe >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PowerShell is required to run Blogger Studio Server Control Center.
    pause
    exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0studio_server.ps1" %*
exit /b %ERRORLEVEL%
