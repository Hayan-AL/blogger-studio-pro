# Blogger Studio Pro - Launch Native Deployment GUI
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Set-Location -Path $PSScriptRoot

& "$PSScriptRoot\studio_deploy_gui.ps1"
