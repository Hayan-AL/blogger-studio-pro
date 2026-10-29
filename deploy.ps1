# Tekmilo Studio Pro - PowerShell Deployment Shortcut
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Set-Location -Path $PSScriptRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python is not installed or not in PATH!" -ForegroundColor Red
    exit 1
}

python deploy.py $args
