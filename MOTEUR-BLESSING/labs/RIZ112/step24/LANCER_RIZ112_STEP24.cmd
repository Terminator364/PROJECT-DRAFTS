@echo off
setlocal EnableExtensions
cd /d "%~dp0.." || exit /b 20
where py >nul 2>nul
if errorlevel 1 (set "PY=python") else (set "PY=py -3")
call step20\LANCER_RIZ112_STEP20.cmd
if errorlevel 1 goto :failed
%PY% step21\quality_priority.py --draft step20\PROTOCOLE_Q_14_SORTIES_DRAFT.json --out step21\PC_PRIORITY_CHECK.json
if errorlevel 1 goto :failed
%PY% step23\evidence_gate.py --priority step21\PRIORITY_CONFIRMED_NO_WEIGHTS.json --quality step20\PROTOCOLE_Q_14_SORTIES_DRAFT.json --out step23\PC_READINESS_NO_TRIALS.json
if errorlevel 1 goto :failed
%PY% step24\interaction_matrix.py --packet step6\examples\A_couvercle_ajuste_112.json --assumptions step20\ASSUMPTIONS_SYNTHETIQUES_NON_CALIBREES.json --out step24\PC_INTERACTIONS_36.json
if errorlevel 1 goto :failed
for %%S in (21 22 23 24) do (
  %PY% -m unittest discover -s step%%S -p "test_*.py" -q
  if errorlevel 1 goto :failed
)
echo RIZ112_STEP24_LAUNCH_OK__47_TESTS_AND_IC_SCIENTIFIC_NULL
exit /b 0
:failed
echo RIZ112_STEP24_LAUNCH_FAILED
exit /b 2
