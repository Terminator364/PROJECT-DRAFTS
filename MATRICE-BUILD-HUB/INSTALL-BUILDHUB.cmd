@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0bootstrap-pc.ps1"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo INSTALLATION BUILD HUB EN ECHEC.
  echo Note le code d'erreur affiche ci-dessus et envoie-le dans la conversation BUILDHUB.
  pause
)
exit /b %RC%
