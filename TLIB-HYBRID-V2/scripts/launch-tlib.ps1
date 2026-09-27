param([switch]$NoOpen)

$ErrorActionPreference="SilentlyContinue"
$AppRoot=(Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$DataDir=Join-Path $env:LOCALAPPDATA "TLIB-PC"
$Updater=Join-Path $AppRoot "scripts\update-tlib.ps1"
$Pending=Join-Path $DataDir "pending-update.json"
$StageStamp=Join-Path $DataDir "last-stage-check.txt"
$LaunchLog=Join-Path $DataDir "launcher.log"
New-Item -ItemType Directory -Force -Path $DataDir | Out-Null

function L([string]$msg){("{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"),$msg)|Add-Content -Encoding UTF8 $LaunchLog}
function Health {
  try{return Invoke-RestMethod -Uri "http://127.0.0.1:8787/api/health" -TimeoutSec 2}catch{return $null}
}

L "CLICK noOpen=$NoOpen"

if(Test-Path $Pending){
  L "PENDING_UPDATE_FOUND"
  try{
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Updater -Mode Apply | Out-Null
    L "PENDING_UPDATE_APPLIED"
  }catch{
    L ("PENDING_UPDATE_APPLY_FAILED "+$_.Exception.Message)
  }
}

try{
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Updater -Mode Repair | Out-Null
}catch{
  L ("REPAIR_FAILED "+$_.Exception.Message)
}

$h=Health
if(-not $h){
  L "HEALTH_FAILED"
  if(-not $NoOpen){
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show("TLIB n'a pas réussi à démarrer. Le système de réparation a été exécuté. Consulte le journal : $LaunchLog","TLIB") | Out-Null
  }
  exit 1
}
L ("READY build="+$h.build+" commit="+$h.commit+" pid="+$h.pid)

if(-not $NoOpen){
  $url="http://127.0.0.1:8787"
  $edgeCandidates=@(
    "$env:ProgramFiles (x86)\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "$env:LOCALAPPDATA\Microsoft\Edge\Application\msedge.exe"
  )
  $edge=$edgeCandidates | Where-Object {Test-Path $_} | Select-Object -First 1
  if($edge){Start-Process -FilePath $edge -ArgumentList "--app=$url","--start-maximized","--no-first-run"}
  else{Start-Process $url}
}

$shouldStage=$true
if(Test-Path $StageStamp){
  try{
    $last=[datetime]::Parse((Get-Content $StageStamp -Raw).Trim()).ToUniversalTime()
    if(((Get-Date).ToUniversalTime()-$last).TotalMinutes -lt 120){$shouldStage=$false}
  }catch{}
}
if($shouldStage){
  (Get-Date).ToUniversalTime().ToString("o") | Set-Content -Encoding ASCII $StageStamp
  $args='-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "'+$Updater+'" -Mode Stage'
  Start-Process -FilePath "powershell.exe" -ArgumentList $args -WindowStyle Hidden
  L "BACKGROUND_STAGE_STARTED"
}
