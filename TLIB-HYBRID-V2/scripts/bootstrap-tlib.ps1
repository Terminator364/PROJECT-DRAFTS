param([switch]$NoOpen)

$ErrorActionPreference = "SilentlyContinue"
try { [System.Diagnostics.Process]::GetCurrentProcess().PriorityClass = "BelowNormal" } catch {}

$data = Join-Path $env:LOCALAPPDATA "TLIB-PC"
$currentFile = Join-Path $data "current-deployment.json"
$pendingFile = Join-Path $data "pending-deployment.json"
$stamp = Join-Path $data "last-slot-stage-check.txt"
$log = Join-Path $data "bootstrap.log"
New-Item -ItemType Directory -Force -Path $data | Out-Null

function L([string]$m) {
  ("{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m) | Add-Content -Encoding UTF8 $log
}
function Current {
  try { return Get-Content $currentFile -Raw | ConvertFrom-Json } catch { return $null }
}
function Updater {
  $c = Current
  if ($c -and $c.path) {
    $p = Join-Path $c.path "scripts\slot-update.mjs"
    if (Test-Path $p) { return $p }
  }
  return $null
}
function Health {
  try { return Invoke-RestMethod "http://127.0.0.1:8787/api/health" -TimeoutSec 2 } catch { return $null }
}

L "BOOTSTRAP_BEGIN noOpen=$NoOpen"

$updater = Updater
if (-not $updater) {
  L "NO_CURRENT_SLOT"
  if (-not $NoOpen) {
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show("TLIB n'a pas encore de déploiement actif vérifié. Lance l'installateur TLIB une fois pour initialiser le système de slots.","TLIB") | Out-Null
  }
  exit 2
}

# Si une version vérifiée attend, elle est activée avant ouverture.
if (Test-Path $pendingFile) {
  L "PENDING_SLOT_FOUND"
  & node $updater apply | Out-Null
  $updater = Updater
}

# Répare uniquement si le worker actif ne correspond pas au slot courant.
& node $updater repair | Out-Null
$h = Health
if (-not $h -or -not $h.ok) {
  L "HEALTH_FAILED"
  if (-not $NoOpen) {
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show("TLIB n'a pas réussi à se réparer automatiquement. Consulte le journal : $log","TLIB") | Out-Null
  }
  exit 1
}
L ("READY build="+$h.build+" commit="+$h.commit+" pid="+$h.pid)

if (-not $NoOpen) {
  $url = "http://127.0.0.1:8787"
  $edgeCandidates = @(
    "$env:ProgramFiles (x86)\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "$env:LOCALAPPDATA\Microsoft\Edge\Application\msedge.exe"
  )
  $edge = $edgeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
  if ($edge) { Start-Process $edge -ArgumentList "--app=$url","--start-maximized","--no-first-run" }
  else { Start-Process $url }
}

# Découverte de mise à jour au maximum toutes les 6 heures.
$stage = $true
if (Test-Path $stamp) {
  try {
    $last = [datetime]::Parse((Get-Content $stamp -Raw).Trim()).ToUniversalTime()
    if (((Get-Date).ToUniversalTime() - $last).TotalHours -lt 6) { $stage = $false }
  } catch {}
}
if ($stage) {
  (Get-Date).ToUniversalTime().ToString("o") | Set-Content -Encoding ASCII $stamp
  $updater = Updater
  if ($updater) {
    Start-Process -FilePath "node" -ArgumentList ('"' + $updater + '" stage') -WindowStyle Hidden
    L "BACKGROUND_STAGE_STARTED"
  }
}
