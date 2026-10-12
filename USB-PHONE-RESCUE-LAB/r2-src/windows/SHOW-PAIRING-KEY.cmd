@echo off
setlocal
set "PAIRFILE=%LOCALAPPDATA%\BCP-USB-Rescue\private-state\pairing-key.txt"
if not exist "%PAIRFILE%" (
 echo Cle introuvable. Connecte le telephone, active le partage USB, lance le superviseur, puis reessaie.
) else (
 echo Cle secrete d'appairage. A SAISIR UNIQUEMENT dans l'application Android BCP USB Rescue.
 type "%PAIRFILE%"
 echo.
 echo Ne partage pas cette cle dans ChatGPT, WhatsApp, ni une capture d'ecran.
)
pause