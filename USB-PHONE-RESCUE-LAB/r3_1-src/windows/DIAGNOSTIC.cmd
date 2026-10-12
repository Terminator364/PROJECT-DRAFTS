@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Usb-Readiness.ps1"
echo.
echo Verification de la supervision (lecture seule) :
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-Bridge.ps1" -DiagnoseOnly
pause