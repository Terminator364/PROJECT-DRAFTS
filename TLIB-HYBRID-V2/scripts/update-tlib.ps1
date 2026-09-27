param(
  [ValidateSet("Stage","Apply","Repair","Latest","Verify","Status")]
  [string]$Mode = "Stage"
)

$ErrorActionPreference = "Stop"
try { [System.Diagnostics.Process]::GetCurrentProcess().PriorityClass = "BelowNormal" } catch {}

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$node = (Get-Command node -ErrorAction Stop).Source
$slotUpdater = Join-Path $root "scripts\slot-update.mjs"
$verifier = Join-Path $root "scripts\verify-build.mjs"
$entry = Join-Path $root "src\tlib.mjs"

if ($Mode -eq "Verify") {
  & $node --check $entry
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  & $node $verifier
  exit $LASTEXITCODE
}

$map = @{
  Stage = "stage"
  Apply = "apply"
  Repair = "repair"
  Latest = "latest"
  Status = "status"
}
$slotMode = $map[$Mode]
& $node $slotUpdater $slotMode
exit $LASTEXITCODE
