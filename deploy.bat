@echo off
chcp 65001 >nul
title Tekmilo Studio Pro - Deployment Wizard
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.9+ to run the deployment wizard.
    pause
    exit /b 1
)

python deploy.py %*
if %errorlevel% neq 0 (
    pause
)
