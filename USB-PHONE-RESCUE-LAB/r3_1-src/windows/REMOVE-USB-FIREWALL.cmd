@echo off
setlocal
cd /d "%~dp0"
echo BCP USB Rescue: retire exclusivement sa regle USB, sur demande de l'utilisateur.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Request-UsbFirewall.ps1" -Undo
if errorlevel 1 echo Suppression echouee ou autorisation annulee.
pause