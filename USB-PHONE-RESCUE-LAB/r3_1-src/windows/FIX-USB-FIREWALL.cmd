@echo off
setlocal
cd /d "%~dp0"
echo BCP USB Rescue: ouvre une fenetre Windows UAC uniquement pour le reseau USB.
echo Branche le telephone, active le partage USB, puis accepte Windows UAC.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Request-UsbFirewall.ps1"
if errorlevel 1 echo Echec ou autorisation annulee. Aucun reglage volontaire n'a ete conserve.
pause