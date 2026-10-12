# Manual one-time installation for the CURRENT Windows user; does not silently open a firewall.
param([switch]$SkipTask)
$ErrorActionPreference='Stop'
$src=Split-Path -Parent $PSScriptRoot
$dst=Join-Path $env:LOCALAPPDATA 'BCP-USB-Rescue'
$bin=Join-Path $dst 'windows'
$pyLauncher = Get-Command py -ErrorAction SilentlyContinue
$pythonDirect = Get-Command python -ErrorAction SilentlyContinue
if(-not $pyLauncher -and -not $pythonDirect) {
  throw 'Python 3 absent. Install Python 3.10+ from python.org before retrying.'
}
# Reject insufficient Python versions at installation, not after a failing login loop.
$pythonValid=$false
foreach($cmd in @('py','python')) {
  if(-not (Get-Command $cmd -ErrorAction SilentlyContinue)){continue}
  $args=if($cmd -eq 'py'){@('-3','-c','import sys;sys.exit(0 if sys.version_info >= (3,10) else 3)')}else{@('-c','import sys;sys.exit(0 if sys.version_info >= (3,10) else 3)')}
  try { & $cmd @args 2>$null; if($LASTEXITCODE -eq 0){$pythonValid=$true;break} } catch {}
}
if(-not $pythonValid){throw 'A compatible Python 3.10+ runtime is required.'}
New-Item -ItemType Directory -Path $bin -Force|Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'bridge_agent.py') -Destination $bin -Force
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'Start-Bridge.ps1') -Destination $bin -Force
foreach($file in @('SHOW-PAIRING-KEY.cmd','DIAGNOSTIC.cmd','START-NOW.cmd','REMOVE.cmd','Usb-Readiness.ps1','USB-READINESS.cmd','Fix-UsbFirewall.ps1','Request-UsbFirewall.ps1','FIX-USB-FIREWALL.cmd','REMOVE-USB-FIREWALL.cmd')) { Copy-Item -LiteralPath (Join-Path $PSScriptRoot $file) -Destination $bin -Force }
New-Item -ItemType Directory -Path (Join-Path $dst 'private-state'),(Join-Path $dst 'workspace'),(Join-Path $dst 'logs') -Force|Out-Null
$state=Join-Path $dst 'private-state'
# Secure state storage to the installing user; no console printing of key.
try {
  $account=[System.Security.Principal.WindowsIdentity]::GetCurrent().Name
  & icacls.exe $state /inheritance:r /grant:r "$($account):(OI)(CI)F" "*S-1-5-18:(OI)(CI)F" "*S-1-5-32-544:(OI)(CI)F" | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "icacls failure exit $LASTEXITCODE" }
} catch { throw "SECURITY_BLOCK: pairing secret directory ACL hardening failed: $($_.Exception.Message)" }
if(-not $SkipTask) {
  $action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "'+(Join-Path $bin 'Start-Bridge.ps1')+'"')
  $trigger=New-ScheduledTaskTrigger -AtLogOn -User ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name)
  $settings=New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Seconds 0)
  Register-ScheduledTask -TaskName 'BCP USB Rescue Guardian' -Action $action -Trigger $trigger -Settings $settings -Description 'Local USB bridge agent, current user session only' -Force | Out-Null
  Write-Host 'Task Scheduler created: BCP USB Rescue Guardian (on logon).'
}
Write-Host "Installed to: $dst"
Write-Host 'The agent only works while Windows is on and the Android USB tether adapter has an IP.'
Write-Host 'The local task does not grant firewall privileges or bypass Windows sign-in.'
Write-Host 'First setup: connect Android USB, enable USB tethering, then double-click START-NOW.cmd from the installed windows folder.'
Write-Host 'The startup guardian waits if the USB cable is absent, and checks for reconnection automatically.'
Write-Host "Secret stored at: $(Join-Path $state 'pairing-key.txt') (created at first agent startup)."