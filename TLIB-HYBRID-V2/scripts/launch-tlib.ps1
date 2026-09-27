param([switch]$NoOpen)

$ErrorActionPreference = "SilentlyContinue"
$data = Join-Path $env:LOCALAPPDATA "TLIB-PC"
$stable = Join-Path $data "bootstrap.ps1"

if (Test-Path $stable) {
  & "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File $stable @($NoOpen ? "-NoOpen" : @())
  exit $LASTEXITCODE
}

# Fallback uniquement avant la première installation slot-safe.
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$slot = Join-Path $root "scripts\slot-update.mjs"
if (-not (Test-Path $slot)) { exit 2 }

if (-not (Test-Path (Join-Path $data "current-deployment.json"))) {
  & node $slot latest
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$bootstrapSource = Join-Path $root "scripts\bootstrap-tlib.ps1"
if (Test-Path $bootstrapSource) {
  Copy-Item $bootstrapSource $stable -Force
  & "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File $stable @($NoOpen ? "-NoOpen" : @())
  exit $LASTEXITCODE
}

exit 3
