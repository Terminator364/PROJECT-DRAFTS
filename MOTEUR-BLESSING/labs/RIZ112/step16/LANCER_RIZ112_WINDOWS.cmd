@echo off
setlocal
cd /d "%~dp0.."
where py >nul 2>nul
if errorlevel 1 (set "PYTHON=python") else (set "PYTHON=py -3")
%PYTHON% step16\riz112_unified.py --lab-root . --packet step6\examples\A_couvercle_ajuste_112.json --require-h3 --output step16\RESULTAT_AB_C.json
if errorlevel 1 (
 echo [ERREUR] Le moteur a refuse une entree, un module absent ou un calcul. Voir le message ci-dessus.
 pause
 exit /b 1
)
echo.
echo [OK] Resultats dans step16\RESULTAT_AB_C.json
pause