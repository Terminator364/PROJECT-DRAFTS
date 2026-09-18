param([Parameter(ValueFromRemainingArguments=$true)][string[]]$ForwardArgs)

$ErrorActionPreference="Stop"
$Hub=Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot=Split-Path -Parent $Hub

if(Test-Path (Join-Path $RepoRoot ".git")){
  try{
    & git -C $RepoRoot fetch origin main --quiet
    if($LASTEXITCODE -ne 0){throw "git fetch origin main failed."}
    & git -C $RepoRoot reset --hard origin/main --quiet
    if($LASTEXITCODE -ne 0){throw "git reset --hard origin/main failed."}
  }catch{
    throw ("[HUB_UPDATE_FAILED] Refusing to build with a potentially stale orchestrator. "+$_.Exception.Message)
  }
}

$Core=Join-Path $Hub "hub.ps1"
if(-not(Test-Path $Core)){throw "hub.ps1 is missing."}
$SelfTest=Join-Path $Hub "self-test.ps1"
if(-not(Test-Path $SelfTest)){throw "self-test.ps1 is missing."}
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $SelfTest
if($LASTEXITCODE -ne 0){throw "BuildHub static self-test failed; build blocked."}

if($ForwardArgs -and $ForwardArgs.Count -gt 0){
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Core @ForwardArgs
}else{
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Core
}
exit $LASTEXITCODE
