@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_green_metrics.ps1" %*
exit /b %ERRORLEVEL%
