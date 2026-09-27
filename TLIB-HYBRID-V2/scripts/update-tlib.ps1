param(
  [ValidateSet("Stage","Apply","Repair","Latest","Verify")]
  [string]$Mode = "Stage"
)

$ErrorActionPreference = "Stop"
try { [System.Diagnostics.Process]::GetCurrentProcess().PriorityClass = "BelowNormal" } catch {}
try { [System.Diagnostics.Process]::GetCurrentProcess().PriorityClass = "BelowNormal" } catch {}
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$AppRoot = Join-Path $RepoRoot "TLIB-HYBRID-V2"
$DataDir = Join-Path $env:LOCALAPPDATA "TLIB-PC"
$Node = (Get-Command node -ErrorAction Stop).Source
$Entry = Join-Path $AppRoot "src\tlib.mjs"
$Branch = "lab/tlib-hybrid-v2"
$PendingFile = Join-Path $DataDir "pending-update.json"
$LastGoodFile = Join-Path $DataDir "last-good.json"
$RuntimeFile = Join-Path $DataDir "runtime.json"
$LogFile = Join-Path $DataDir "update-audit.jsonl"
$LockFile = Join-Path $DataDir "update.lock"
New-Item -ItemType Directory -Force -Path $DataDir | Out-Null

function Write-UpdateLog([string]$event,[string]$detail="",[string]$status="INFO"){
  $obj=[ordered]@{at=(Get-Date).ToUniversalTime().ToString("o");event=$event;status=$status;detail=$detail;mode=$Mode}
  ($obj | ConvertTo-Json -Compress) | Add-Content -Encoding UTF8 $LogFile
}

$lock=$null
try{
  $lock=[System.IO.File]::Open($LockFile,[System.IO.FileMode]::OpenOrCreate,[System.IO.FileAccess]::ReadWrite,[System.IO.FileShare]::None)
}catch{
  Write-UpdateLog "UPDATE_ALREADY_RUNNING" $_.Exception.Message "SKIP"
  exit 0
}

function Git([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args){
  $out=& git -C $RepoRoot @Args 2>&1
  if($LASTEXITCODE -ne 0){ throw "git $($Args -join ' ') failed: $($out -join ' ')" }
  return (($out -join [Environment]::NewLine).Trim())
}
function Get-Health {
  try { return Invoke-RestMethod -Uri "http://127.0.0.1:8787/api/health" -TimeoutSec 2 }
  catch { return $null }
}
function Get-WorkerPid {
  $h=Get-Health
  if($h -and $h.pid){ return [int]$h.pid }
  if(Test-Path $RuntimeFile){
    try{
      $r=Get-Content $RuntimeFile -Raw | ConvertFrom-Json
      $pidValue=[int]$r.pid
      $p=Get-CimInstance Win32_Process -Filter "ProcessId=$pidValue" -ErrorAction SilentlyContinue
      if($p -and $p.CommandLine -like "*tlib.mjs*"){ return $pidValue }
    }catch{}
  }
  return $null
}
function Stop-Worker {
  $targets=@()
  $pidValue=Get-WorkerPid
  if($pidValue){ $targets += [int]$pidValue }
  try{
    $targets += @(Get-CimInstance Win32_Process -Filter "Name='node.exe'" -ErrorAction SilentlyContinue |
      Where-Object { $_.CommandLine -like "*TLIB-HYBRID-V2*src*tlib.mjs*agent*" } |
      ForEach-Object { [int]$_.ProcessId })
  }catch{}
  $targets=@($targets | Sort-Object -Unique)
  foreach($p in $targets){
    Write-UpdateLog "WORKER_STOP" "pid=$p"
    Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
  }
  if($targets.Count){
    for($i=0;$i -lt 30;$i++){ Start-Sleep -Milliseconds 200; if(-not (Get-Health)){ break } }
  }
}
function Start-Worker([string]$ExpectedCommit){
  Write-UpdateLog "WORKER_START" "expected=$ExpectedCommit"
  Start-Process -FilePath $Node -ArgumentList ('"' + $Entry + '" agent') -WorkingDirectory $RepoRoot -WindowStyle Hidden
  for($i=0;$i -lt 60;$i++){
    Start-Sleep -Milliseconds 350
    $h=Get-Health
    if($h -and $h.ok){
      if($ExpectedCommit -and $h.commit -ne $ExpectedCommit){ continue }
      try{
        $dups=@(Get-CimInstance Win32_Process -Filter "Name='node.exe'" -ErrorAction SilentlyContinue |
          Where-Object { $_.CommandLine -like "*TLIB-HYBRID-V2*src*tlib.mjs*agent*" })
        if($dups.Count -gt 1){
          Write-UpdateLog "DUPLICATE_WORKERS_DETECTED" ("count="+$dups.Count) "FAIL"
          foreach($p in $dups){ if([int]$p.ProcessId -ne [int]$h.pid){ Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue } }
        }
      }catch{}
      Write-UpdateLog "WORKER_HEALTHY" "pid=$($h.pid); build=$($h.build); commit=$($h.commit)" "PASS"
      return $h
    }
  }
  throw "TLIB worker failed health/version check for commit $ExpectedCommit"
}
function Verify-App([string]$CandidateAppRoot){
  Write-UpdateLog "VERIFY_BEGIN" $CandidateAppRoot
  $candidateEntry=Join-Path $CandidateAppRoot "src\tlib.mjs"
  $candidateVerifier=Join-Path $CandidateAppRoot "scripts\verify-build.mjs"
  & $Node --check $candidateEntry
  if($LASTEXITCODE -ne 0){ throw "Node syntax verification failed" }
  & $Node $candidateVerifier
  if($LASTEXITCODE -ne 0){ throw "UI/build verification failed" }
  $tmp=Join-Path $DataDir ("verify-"+[guid]::NewGuid().ToString("N"))
  New-Item -ItemType Directory -Force -Path $tmp | Out-Null
  $old=$env:TLIB_DATA_DIR
  try{
    $env:TLIB_DATA_DIR=$tmp
    & $Node $candidateEntry selftest
    if($LASTEXITCODE -ne 0){ throw "TLIB selftest failed" }
  }finally{
    $env:TLIB_DATA_DIR=$old
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
  }
  Write-UpdateLog "VERIFY_PASS" $CandidateAppRoot "PASS"
}
function Stage-Latest {
  $env:GIT_TERMINAL_PROMPT="0"
  Write-UpdateLog "FETCH_BEGIN" $Branch
  Git fetch origin $Branch --prune | Out-Null
  $target=Git rev-parse ("origin/"+$Branch)
  $current=Git rev-parse HEAD
  if($target -eq $current){
    Remove-Item $PendingFile -Force -ErrorAction SilentlyContinue
    Write-UpdateLog "NO_UPDATE" "commit=$current" "PASS"
    return $null
  }
  $short=$target.Substring(0,12)
  $stage=Join-Path $DataDir ("stage-"+$short)
  Git worktree prune | Out-Null
  if(Test-Path $stage){
    try{ Git worktree remove --force $stage | Out-Null }catch{ Remove-Item $stage -Recurse -Force -ErrorAction SilentlyContinue }
  }
  try{
    Git worktree add --detach --force $stage $target | Out-Null
    Verify-App (Join-Path $stage "TLIB-HYBRID-V2")
  }finally{
    try{ Git worktree remove --force $stage | Out-Null }catch{ Remove-Item $stage -Recurse -Force -ErrorAction SilentlyContinue }
    Git worktree prune | Out-Null
  }
  $pending=[ordered]@{target=$target;previous=$current;branch=$Branch;verified=$true;staged_at=(Get-Date).ToUniversalTime().ToString("o")}
  $pending | ConvertTo-Json | Set-Content -Encoding UTF8 $PendingFile
  Write-UpdateLog "UPDATE_STAGED" "from=$current; to=$target" "PASS"
  return $target
}
function Apply-Pending {
  if(-not (Test-Path $PendingFile)){
    Write-UpdateLog "NO_PENDING_UPDATE" "" "PASS"
    return
  }
  $p=Get-Content $PendingFile -Raw | ConvertFrom-Json
  if(-not $p.verified){ throw "Pending update is not verified" }
  $target=[string]$p.target
  Git cat-file -e ($target+"^{commit}") | Out-Null
  $current=Git rev-parse HEAD
  if($current -eq $target){
    Remove-Item $PendingFile -Force -ErrorAction SilentlyContinue
    Repair-Current
    return
  }
  $dirty=Git status --porcelain --untracked-files=no
  if($dirty){
    Write-UpdateLog "APPLY_BLOCKED_DIRTY_TREE" $dirty "BLOCKED"
    throw "Tracked local modifications detected; refusing destructive update"
  }
  [ordered]@{commit=$current;created_at=(Get-Date).ToUniversalTime().ToString("o")} | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $DataDir "rollback.json")
  Stop-Worker
  try{
    Git reset --hard $target | Out-Null
    Verify-App $AppRoot
    $h=Start-Worker $target
    [ordered]@{commit=$target;build=$h.build;activated_at=(Get-Date).ToUniversalTime().ToString("o")} | ConvertTo-Json | Set-Content -Encoding UTF8 $LastGoodFile
    Remove-Item $PendingFile -Force -ErrorAction SilentlyContinue
    Write-UpdateLog "UPDATE_ACTIVATED" "from=$current; to=$target; build=$($h.build)" "PASS"
  }catch{
    $reason=$_.Exception.Message
    Write-UpdateLog "UPDATE_ACTIVATION_FAILED" $reason "FAIL"
    try{
      Stop-Worker
      Git reset --hard $current | Out-Null
      $old=Start-Worker $current
      Write-UpdateLog "ROLLBACK_PASS" "commit=$current; build=$($old.build)" "PASS"
      if(Test-Path $PendingFile){
        $failed=Join-Path $DataDir ("failed-update-"+(Get-Date -Format "yyyyMMdd-HHmmss")+".json")
        Move-Item $PendingFile $failed -Force
        Write-UpdateLog "FAILED_UPDATE_QUARANTINED" $failed "PASS"
      }
    }catch{
      Write-UpdateLog "ROLLBACK_FAILED" $_.Exception.Message "CRITICAL"
    }
    throw $reason
  }
}
function Repair-Current {
  $current=Git rev-parse HEAD
  $h=Get-Health
  if($h -and $h.ok -and $h.commit -eq $current){
    Write-UpdateLog "REPAIR_NOT_NEEDED" "pid=$($h.pid); commit=$current" "PASS"
    return $h
  }
  Write-UpdateLog "REPAIR_REQUIRED" "expected=$current; observed=$($h.commit)"
  Stop-Worker
  Verify-App $AppRoot
  return Start-Worker $current
}

try{
  switch($Mode){
    "Verify" { Verify-App $AppRoot }
    "Stage" { Stage-Latest | Out-Null }
    "Apply" { Apply-Pending }
    "Repair" { Repair-Current | Out-Null }
    "Latest" { Stage-Latest | Out-Null; Apply-Pending }
  }
  Write-UpdateLog "UPDATE_COMMAND_PASS" $Mode "PASS"
}catch{
  Write-UpdateLog "UPDATE_COMMAND_FAIL" $_.Exception.Message "FAIL"
  throw
}finally{
  if($lock){$lock.Dispose()}
}
