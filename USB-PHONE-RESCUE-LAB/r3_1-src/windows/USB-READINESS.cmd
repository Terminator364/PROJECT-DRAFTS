@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Usb-Readiness.ps1"
echo Aucune configuration Windows n'a ete modifiee par ce diagnostic.
pause