@echo off
setlocal
chcp 65001 >nul
title Desktop Commander Remote - Rescue V3
echo.
echo ====================================================
echo   DESKTOP COMMANDER REMOTE - RESCUE V3
echo   Sans installation npm / sans suppression de compte
echo ====================================================
echo.
where node.exe >nul 2>&1
if errorlevel 1 (
 echo ERREUR: Node.js est introuvable. Aucune modification effectuee.
 pause
 exit /b 2
)
node.exe "%~dp0rescue.mjs"
set "RESULT=%ERRORLEVEL%"
echo.
echo Session terminee. Code: %RESULT%
echo Journal: %%LOCALAPPDATA%%\BlessingPC\remote-rescue-v3\logs\rescue.log
echo Etat: %%LOCALAPPDATA%%\BlessingPC\remote-rescue-v3\status.json
pause
exit /b %RESULT%
