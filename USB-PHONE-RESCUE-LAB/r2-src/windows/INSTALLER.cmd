@echo off
setlocal
cd /d "%~dp0"
echo BCP USB Rescue R1 - Windows installer (current user)
echo This does not install a driver or open firewall ports automatically.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-Rescue.ps1"
if errorlevel 1 echo INSTALLATION FAILED: see messages above.
pause