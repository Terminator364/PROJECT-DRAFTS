# User-facing elevation boundary: Windows UAC, never automatic during installation.
param([switch]$Undo)
$ErrorActionPreference='Stop'
$script=Join-Path $PSScriptRoot 'Fix-UsbFirewall.ps1'
if(-not (Test-Path -LiteralPath $script)){throw "Missing repair helper: $script"}
$args=@('-NoProfile','-ExecutionPolicy','Bypass','-NoExit','-File',('"'+$script+'"'))
if($Undo){$args+= '-Undo'}
try {
  Start-Process -FilePath 'powershell.exe' -Verb RunAs -ArgumentList $args -Wait -ErrorAction Stop | Out-Null
} catch {
  Write-Warning ('Permission refusée ou erreur de lancement : '+$_.Exception.Message)
  exit 1
}