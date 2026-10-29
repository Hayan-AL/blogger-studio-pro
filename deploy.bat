@echo off
chcp 65001 >nul
cd /d "%~dp0"

where powershell.exe >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PowerShell is required to run Blogger Studio Deployment Manager.
    pause
    exit /b 1
)

start "" powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0studio_deploy_gui.ps1"
exit /b 0
