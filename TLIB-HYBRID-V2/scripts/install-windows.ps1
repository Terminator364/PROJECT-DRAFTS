param(
  [string]$RepoDir = (Resolve-Path (Join-Path $PSScriptRoot ".."))
)

$ErrorActionPreference = "Stop"
try { [System.Diagnostics.Process]::GetCurrentProcess().PriorityClass = "BelowNormal" } catch {}

$node = (Get-Command node -ErrorAction Stop).Source
$entry = Join-Path $RepoDir "src\tlib.mjs"
$verify = Join-Path $RepoDir "scripts\verify-build.mjs"
$slotUpdater = Join-Path $RepoDir "scripts\slot-update.mjs"
$bootstrapSource = Join-Path $RepoDir "scripts\bootstrap-tlib.ps1"
$dataDir = Join-Path $env:LOCALAPPDATA "TLIB-PC"
$bootstrapStable = Join-Path $dataDir "bootstrap.ps1"
$desktop = [Environment]::GetFolderPath("Desktop")
$startup = [Environment]::GetFolderPath("Startup")
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null

Write-Host "TLIB: verification du paquet d'installation..."
& $node --check $entry
if ($LASTEXITCODE -ne 0) { throw "Node syntax check failed" }
& $node $verify
if ($LASTEXITCODE -ne 0) { throw "Build verification failed" }

Write-Host "TLIB: preparation et activation d'un slot verifie..."
& $node $slotUpdater latest --force
if ($LASTEXITCODE -ne 0) { throw "Slot activation failed" }

$currentFile = Join-Path $dataDir "current-deployment.json"
if (-not (Test-Path $currentFile)) { throw "No current deployment pointer after slot activation" }

# Le bootstrap stable n'est pas dans le slot actif : il reste constant pendant les bascules.
Copy-Item $bootstrapSource $bootstrapStable -Force

# Nettoyage des anciens points d'entree.
Remove-Item (Join-Path $desktop "TLIB Cockpit.url") -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $startup "TLIB-PC-Agent.vbs") -Force -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName "TLIB-PC-Agent" -Confirm:$false -ErrorAction SilentlyContinue

# Démarrage automatique : tâche planifiée si autorisée, sinon fallback Startup utilisateur.
$startupInstalled = $false
try {
  $ps = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
  $args = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $bootstrapStable + '" -NoOpen'
  $action = New-ScheduledTaskAction -Execute $ps -Argument $args -WorkingDirectory $dataDir
  $trigger = New-ScheduledTaskTrigger -AtLogOn
  $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 0)
  Register-ScheduledTask -TaskName "TLIB-PC-Agent" -Action $action -Trigger $trigger -Settings $settings -Description "TLIB stable self-healing bootstrap" | Out-Null
  $startupInstalled = $true
  Write-Host "TLIB: startup task installed."
} catch {
  Write-Warning "Scheduled Task unavailable; using per-user Startup."
}

if (-not $startupInstalled) {
  $vbs = Join-Path $startup "TLIB-PC-Agent.vbs"
  $vbsContent = @(
    'Set sh = CreateObject("WScript.Shell")',
    'ps = sh.ExpandEnvironmentStrings("%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe")',
    'boot = sh.ExpandEnvironmentStrings("%LOCALAPPDATA%\TLIB-PC\bootstrap.ps1")',
    'sh.Run Chr(34) & ps & Chr(34) & " -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File " & Chr(34) & boot & Chr(34) & " -NoOpen", 0, False'
  )
  Set-Content -Path $vbs -Value $vbsContent -Encoding ASCII
}

# Raccourci bureau : un seul point d'entrée stable.
$shortcut = Join-Path $desktop "TLIB.lnk"
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut($shortcut)
$lnk.TargetPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$lnk.Arguments = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $bootstrapStable + '"'
$lnk.WorkingDirectory = $dataDir
$icon = Join-Path $dataDir "TLIB.ico"
if (Test-Path $icon) { $lnk.IconLocation = $icon + ",0" }
else { $lnk.IconLocation = "$env:SystemRoot\System32\SHELL32.dll,220" }
$lnk.Description = "TLIB - Bibliotheque intelligente"
$lnk.Save()

Write-Host "TLIB: verification du bootstrap stable..."
& "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File $bootstrapStable -NoOpen
if ($LASTEXITCODE -ne 0) { throw "Stable bootstrap failed" }

Write-Host "TLIB: installation slot-safe terminee."
