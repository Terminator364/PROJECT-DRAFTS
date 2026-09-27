param(
  [string]$RepoDir = (Resolve-Path (Join-Path $PSScriptRoot ".."))
)

$ErrorActionPreference = "Stop"
$node = (Get-Command node -ErrorAction Stop).Source
$entry = Join-Path $RepoDir "src\tlib.mjs"

Write-Host "TLIB-PC: running self-test..."
& $node $entry selftest
if ($LASTEXITCODE -ne 0) { throw "TLIB self-test failed" }

$startupInstalled = $false
$taskName = "TLIB-PC-Agent"
try {
  $action = New-ScheduledTaskAction -Execute $node -Argument ('"' + $entry + '" agent') -WorkingDirectory $RepoDir
  $trigger = New-ScheduledTaskTrigger -AtLogOn
  $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 0)
  Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
  Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "TLIB lightweight local worker and cockpit" | Out-Null
  Write-Host "TLIB-PC: startup task installed."
  $startupInstalled = $true
} catch {
  Write-Warning "Scheduled Task unavailable; installing per-user Startup fallback."
}

if (-not $startupInstalled) {
  $startup = [Environment]::GetFolderPath("Startup")
  $vbs = Join-Path $startup "TLIB-PC-Agent.vbs"
  $vbsContent = @(
    'Set sh = CreateObject("WScript.Shell")',
    'node = sh.ExpandEnvironmentStrings("%ProgramFiles%\nodejs\node.exe")',
    'entry = sh.ExpandEnvironmentStrings("%LOCALAPPDATA%\TLIB-PC-LAB\TLIB-HYBRID-V2\src\tlib.mjs")',
    'sh.Run Chr(34) & node & Chr(34) & " " & Chr(34) & entry & Chr(34) & " agent", 0, False'
  )
  Set-Content -Path $vbs -Value $vbsContent -Encoding ASCII
  Write-Host "TLIB-PC: per-user Startup fallback installed."
}

$desktop = [Environment]::GetFolderPath("Desktop")
$urlFile = Join-Path $desktop "TLIB Cockpit.url"
@"
[InternetShortcut]
URL=http://127.0.0.1:8787
IconFile=$env:SystemRoot\System32\SHELL32.dll
IconIndex=220
"@ | Set-Content -Encoding ASCII $urlFile

Write-Host "TLIB-PC: desktop cockpit shortcut created."
Write-Host "TLIB-PC: starting agent now..."
Start-Process -FilePath $node -ArgumentList ('"' + $entry + '" agent') -WorkingDirectory $RepoDir -WindowStyle Hidden
Start-Sleep -Seconds 2
Write-Host "Open: http://127.0.0.1:8787"
