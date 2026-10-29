@echo off
setlocal
cd /d "%~dp0"
call "%~dp0tekmilo_server.bat" %*
exit /b %ERRORLEVEL%
