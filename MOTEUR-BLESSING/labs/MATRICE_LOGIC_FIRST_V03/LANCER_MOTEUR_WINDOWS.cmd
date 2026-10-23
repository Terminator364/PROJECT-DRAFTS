@echo off
setlocal EnableExtensions
REM MOTEUR D068 - launcher one action AFTER a local R8 source checkout is present.
REM No paid server, no Desktop Commander, no post-match information fabricated.
set "HERE=%~dp0"
set "SCRIPTPATH=%HERE%moteur_unique_v1.py"
set "R8_ROOT=%MOTEUR_R8_REPO%"
if not defined R8_ROOT if exist "%USERPROFILE%\ChatGPT-PC\MATRICE" set "R8_ROOT=%USERPROFILE%\ChatGPT-PC"
if not defined R8_ROOT if exist "%USERPROFILE%\Documents\GitHub\ChatGPT-PC\MATRICE" set "R8_ROOT=%USERPROFILE%\Documents\GitHub\ChatGPT-PC"
if not defined R8_ROOT if exist "%USERPROFILE%\Desktop\ChatGPT-PC\MATRICE" set "R8_ROOT=%USERPROFILE%\Desktop\ChatGPT-PC"
if not defined R8_ROOT if not "%~1"=="" set "R8_ROOT=%~1"
set "OUT=%LOCALAPPDATA%\MOTEUR_BLESSING\resultats"
if not exist "%OUT%" mkdir "%OUT%"
set "LOG=%OUT%\dernier_lancement.log"
echo [MOTEUR] audit debut: %date% %time% > "%LOG%"
if not exist "%SCRIPTPATH%" (
  echo ERREUR: moteur unique introuvable >> "%LOG%"
  goto FAILED
)
if not defined R8_ROOT (
  echo ERREUR: depot R8 ChatGPT-PC introuvable. >> "%LOG%"
  echo Definir MOTEUR_R8_REPO ou passer le chemin au lanceur. >> "%LOG%"
  goto FAILED
)
if not exist "%R8_ROOT%\MATRICE\R8_G3_DEEP_20261014" (
  echo ERREUR: le chemin R8 ne contient pas la source canonique. >> "%LOG%"
  goto FAILED
)
where py >nul 2>&1
if %errorlevel% equ 0 (
  set "RUNNER=py -3"
) else (
  where python >nul 2>&1
  if errorlevel 1 (
    echo ERREUR: Python 3 non installe ou absent du PATH. >> "%LOG%"
    goto FAILED
  )
  set "RUNNER=python"
)
%RUNNER% "%SCRIPTPATH%" --r8-repo-root "%R8_ROOT%" --outdir "%OUT%" --grid-1000 >> "%LOG%" 2>&1
if not %errorlevel% equ 0 goto FAILED
echo [MOTEUR] audit fin: succes %date% %time% >> "%LOG%"
echo MOTEUR : bilan technique et analyses synthetiques produits sous
echo %OUT%
exit /b 0
:FAILED
echo [MOTEUR] audit fin: echec %date% %time% >> "%LOG%"
echo Le moteur ne suppose aucune donnee manquante.
echo Lire le journal : %LOG%
start "" notepad.exe "%LOG%"
exit /b 1
