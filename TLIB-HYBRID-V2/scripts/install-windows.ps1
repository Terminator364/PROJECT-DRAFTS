param(
  [string]$RepoDir = (Resolve-Path (Join-Path $PSScriptRoot ".."))
)

$ErrorActionPreference = "Stop"
$node = (Get-Command node -ErrorAction Stop).Source
$entry = Join-Path $RepoDir "src\tlib.mjs"
$verify = Join-Path $RepoDir "scripts\verify-build.mjs"
$launcher = Join-Path $RepoDir "scripts\launch-tlib.ps1"
$desktop = [Environment]::GetFolderPath("Desktop")
$dataDir = Join-Path $env:LOCALAPPDATA "TLIB-PC"
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null

Write-Host "TLIB-PC: verification du build..."
& $node --check $entry
if ($LASTEXITCODE -ne 0) { throw "TLIB Node syntax check failed" }
& $node $verify
if ($LASTEXITCODE -ne 0) { throw "TLIB build verification failed" }

# Retire les anciens points d'entree qui contournaient le launcher.
Remove-Item (Join-Path $desktop "TLIB Cockpit.url") -Force -ErrorAction SilentlyContinue
$startup = [Environment]::GetFolderPath("Startup")
Remove-Item (Join-Path $startup "TLIB-PC-Agent.vbs") -Force -ErrorAction SilentlyContinue

$startupInstalled = $false
$taskName = "TLIB-PC-Agent"
try {
  $ps = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
  $args = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $launcher + '" -NoOpen'
  $action = New-ScheduledTaskAction -Execute $ps -Argument $args -WorkingDirectory $RepoDir
  $trigger = New-ScheduledTaskTrigger -AtLogOn
  $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 0)
  Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
  Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "TLIB self-healing launcher" | Out-Null
  Write-Host "TLIB-PC: startup task installed."
  $startupInstalled = $true
} catch {
  Write-Warning "Scheduled Task unavailable; installation du fallback utilisateur."
}

if (-not $startupInstalled) {
  $vbs = Join-Path $startup "TLIB-PC-Agent.vbs"
  $vbsContent = @(
    'Set sh = CreateObject("WScript.Shell")',
    'ps = sh.ExpandEnvironmentStrings("%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe")',
    'launcher = sh.ExpandEnvironmentStrings("%LOCALAPPDATA%\TLIB-PC-LAB\TLIB-HYBRID-V2\scripts\launch-tlib.ps1")',
    'sh.Run Chr(34) & ps & Chr(34) & " -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File " & Chr(34) & launcher & Chr(34) & " -NoOpen", 0, False'
  )
  Set-Content -Path $vbs -Value $vbsContent -Encoding ASCII
  Write-Host "TLIB-PC: per-user Startup fallback installed."
}

# Raccourci unique vers le launcher versionne.
$shortcut = Join-Path $desktop "TLIB.lnk"
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut($shortcut)
$lnk.TargetPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$lnk.Arguments = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $launcher + '"'
$lnk.WorkingDirectory = $RepoDir
$customIcon = Join-Path $dataDir "TLIB.ico"
if (Test-Path $customIcon) { $lnk.IconLocation = $customIcon + ",0" }
else { $lnk.IconLocation = "$env:SystemRoot\System32\SHELL32.dll,220" }
$lnk.Description = "TLIB - Bibliotheque intelligente"
$lnk.Save()

Write-Host "TLIB-PC: launcher desktop installe."
Write-Host "TLIB-PC: verification/reparation du moteur..."
& "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File $launcher -NoOpen
if ($LASTEXITCODE -ne 0) { throw "TLIB launcher repair/start failed" }

Write-Host "TLIB-PC: installation terminee."
