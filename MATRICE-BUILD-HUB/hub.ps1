param(
  [ValidateSet("PhoneMouse","P2PCR95","ChatGPT-PC","BROWSER4G")][string]$Project,
  [string]$Branch,
  [ValidateSet("Build","Smoke","Doctor")][string]$Mode="Build",
  [switch]$NoPublish
)

$ErrorActionPreference="Stop"
$HubVersion="0.3"
$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$Registry=Get-Content (Join-Path $Root "projects.json") -Raw | ConvertFrom-Json
$DataRoot=Join-Path $env:LOCALAPPDATA "MatriceBuildHub"
$StateRoot=Join-Path $DataRoot "state"
$OutputRoot=Join-Path ([Environment]::GetFolderPath("UserProfile")) "Downloads\MatriceBuildHub"
New-Item -ItemType Directory -Force -Path $StateRoot,$OutputRoot | Out-Null

function Fail($Code,$Message){ throw "[$Code] $Message" }
function Need($Name,$Code){ if(-not(Get-Command $Name -ErrorAction SilentlyContinue)){ Fail $Code "$Name is not installed." } }
function SafeBranch($Value){
  if([string]::IsNullOrWhiteSpace($Value) -or $Value -notmatch "^[A-Za-z0-9._/-]+$" -or $Value.Contains("..") -or $Value.Contains("//")){
    Fail "INVALID_BRANCH" "Unsupported branch name: $Value"
  }
}
function ResolveSha($Repo,$Ref){
  $encoded=[uri]::EscapeDataString($Ref)
  $raw=& gh api ("repos/"+$Repo+"/branches/"+$encoded) 2>$null
  if($LASTEXITCODE -ne 0 -or -not $raw){ Fail "BRANCH_NOT_FOUND" "Cannot resolve $Repo/$Ref." }
  return [string](($raw|ConvertFrom-Json).commit.sha)
}
function Ledger(){
  $month=Get-Date -Format "yyyy-MM"
  $path=Join-Path $StateRoot ("codespaces-"+$month+".json")
  if(Test-Path $path){ try{ return @{Path=$path;Data=(Get-Content $path -Raw|ConvertFrom-Json)} }catch{} }
  return @{Path=$path;Data=[pscustomobject]@{month=$month;estimated_core_hours=0.0;builds=0}}
}
function AddUsage([double]$Hours){
  if($Hours -le 0){return}
  $l=Ledger
  $o=[pscustomobject]@{
    month=(Get-Date -Format "yyyy-MM")
    estimated_core_hours=[math]::Round(([double]$l.Data.estimated_core_hours+$Hours),4)
    builds=([int]$l.Data.builds+1)
    updated=(Get-Date).ToString("o")
  }
  $o|ConvertTo-Json|Set-Content -Encoding UTF8 $l.Path
}
function CleanupStale(){
  try{$all=& gh codespace list --limit 100 --json name,displayName,state,createdAt|ConvertFrom-Json}catch{return}
  $cut=(Get-Date).ToUniversalTime().AddHours(-[double]$Registry.policy.cleanup_stale_hub_codespaces_after_hours)
  foreach($c in @($all)){
    if($c.displayName -like "mbh-*" -and ([datetime]$c.createdAt).ToUniversalTime() -lt $cut){
      Write-Host ("Cleaning stale builder "+$c.name) -ForegroundColor Yellow
      & gh codespace stop -c $c.name *> $null
      & gh codespace delete -c $c.name --force *> $null
    }
  }
}
function Pick(){
  Write-Host ""
  Write-Host "MATRICE BUILD HUB V$HubVersion" -ForegroundColor Cyan
  Write-Host "1. PhoneMouse"
  Write-Host "2. P2PCR95"
  Write-Host "3. ChatGPT-PC"
  Write-Host "4. BROWSER4G (build Windows local)"
  Write-Host "5. Diagnostic cloud seulement"
  $x=Read-Host "Choix"
  switch($x){
    "1"{return @("PhoneMouse","Build")}
    "2"{return @("P2PCR95","Build")}
    "3"{return @("ChatGPT-PC","Build")}
    "4"{return @("BROWSER4G","Build")}
    "5"{return @("PhoneMouse","Smoke")}
    default{Fail "INVALID_CHOICE" "Choix invalide."}
  }
}

function InvokeLocalWindowsProject($Project,$Cfg,$Repo,$Branch,$Sha,$BuildId,$Dest,$Mode){
  if($env:OS -ne "Windows_NT"){Fail "LOCAL_WINDOWS_REQUIRED" "This project requires a real Windows builder."}
  $Timeout=[int]$Cfg.build_timeout_minutes
  if($Timeout -lt 1){$Timeout=20}

  $WorkRoot=Join-Path $DataRoot "work"
  $SourceDir=Join-Path $WorkRoot $BuildId
  $ResultDir=Join-Path $Dest ".matrix-build-output"
  New-Item -ItemType Directory -Force -Path $WorkRoot,$ResultDir|Out-Null
  if(Test-Path $SourceDir){Remove-Item -Recurse -Force $SourceDir}

  Write-Host ""
  Write-Host ("Project : "+$Project) -ForegroundColor Green
  Write-Host ("Branch  : "+$Branch)
  Write-Host ("SHA     : "+$Sha)
  Write-Host "Builder : LOCAL_WINDOWS"
  Write-Host ("Mode    : "+$Mode)

  try{
    & gh repo clone $Repo $SourceDir -- --filter=blob:none --no-checkout
    if($LASTEXITCODE -ne 0){Fail "LOCAL_CLONE_FAILED" "Cannot clone the exact source for the Windows build."}

    $SparsePaths=@($Cfg.local_sparse_paths)
    if($SparsePaths.Count -gt 0){
      foreach($sp in $SparsePaths){
        if([string]::IsNullOrWhiteSpace([string]$sp) -or [IO.Path]::IsPathRooted([string]$sp) -or ([string]$sp).Contains("..")){
          Fail "LOCAL_SPARSE_PATH_UNSAFE" ("Unsafe sparse path: "+$sp)
        }
      }
      & git -C $SourceDir sparse-checkout init --cone
      if($LASTEXITCODE -ne 0){Fail "LOCAL_SPARSE_INIT_FAILED" "Cannot initialize sparse checkout."}
      & git -C $SourceDir sparse-checkout set -- $SparsePaths
      if($LASTEXITCODE -ne 0){Fail "LOCAL_SPARSE_SET_FAILED" "Cannot configure sparse checkout."}
    }

    & git -C $SourceDir checkout --detach $Sha
    if($LASTEXITCODE -ne 0){Fail "LOCAL_CHECKOUT_FAILED" "Cannot checkout the requested source SHA."}
    $Actual=([string](& git -C $SourceDir rev-parse HEAD)).Trim()
    if($LASTEXITCODE -ne 0 -or $Actual -ne $Sha){Fail "LOCAL_SOURCE_MISMATCH" "Local Windows source SHA differs from the requested SHA."}

    $RecipeRel=[string]$Cfg.recipe_path
    if([string]::IsNullOrWhiteSpace($RecipeRel) -or [IO.Path]::IsPathRooted($RecipeRel)){
      Fail "LOCAL_RECIPE_PATH" "Local Windows recipe must be a repository-relative path."
    }
    $SourcePrefix=[IO.Path]::GetFullPath($SourceDir+[IO.Path]::DirectorySeparatorChar)
    $RecipePath=[IO.Path]::GetFullPath((Join-Path $SourceDir $RecipeRel))
    if(-not $RecipePath.StartsWith($SourcePrefix,[StringComparison]::OrdinalIgnoreCase)){
      Fail "LOCAL_RECIPE_ESCAPE" "Local Windows recipe escapes the exact-SHA source root."
    }
    if(-not(Test-Path $RecipePath -PathType Leaf)){Fail "LOCAL_RECIPE_MISSING" ("Missing local Windows recipe: "+$RecipeRel)}

    $Job=Start-Job -ScriptBlock {
      param($RecipePath,$Mode,$ResultDir,$Sha)
      & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $RecipePath -Mode $Mode -OutputDir $ResultDir -SourceSha $Sha
      if($LASTEXITCODE -ne 0){throw ("recipe exit code "+$LASTEXITCODE)}
    } -ArgumentList $RecipePath,$Mode,$ResultDir,$Sha

    $Done=Wait-Job -Job $Job -Timeout ($Timeout*60)
    if(-not $Done){
      Stop-Job -Job $Job -ErrorAction SilentlyContinue
      Remove-Job -Job $Job -Force -ErrorAction SilentlyContinue
      Fail "LOCAL_BUILD_TIMEOUT" ("Local Windows build exceeded "+$Timeout+" minutes.")
    }
    $JobOutput=Receive-Job -Job $Job -ErrorAction SilentlyContinue
    $State=[string]$Job.State
    $JobOutput|ForEach-Object{Write-Host $_}
    $Reason=$null
    if($Job.ChildJobs.Count -gt 0){$Reason=$Job.ChildJobs[0].JobStateInfo.Reason}
    Remove-Job -Job $Job -Force -ErrorAction SilentlyContinue
    if($State -ne "Completed"){
      $detail=if($Reason){[string]$Reason.Message}else{"recipe job failed"}
      Fail "LOCAL_BUILD_FAILED" $detail
    }

    $ResultFile=Join-Path $ResultDir "result.json"
    if(-not(Test-Path $ResultFile -PathType Leaf)){Fail "RESULT_MISSING" "Local Windows result.json missing."}
    try{$Result=Get-Content $ResultFile -Raw|ConvertFrom-Json}catch{Fail "RESULT_JSON_INVALID" "Local Windows result.json is invalid."}
    if([string]$Result.schema -ne "mbh-result-v1"){Fail "RESULT_SCHEMA" "Unsupported result schema."}
    if([string]$Result.source_sha -ne $Sha){Fail "SOURCE_MISMATCH" "Built SHA differs from requested SHA."}
    if($Cfg.publish_gate -eq "FIELD_PASS_REQUIRED" -and $Result.publish -eq $true){
      Fail "FIELD_GATE_BYPASS" "Project cannot publish before the field-validation gate passes."
    }

    $Files=@()
    foreach($name in @($Result.deliverables)){
      if([string]::IsNullOrWhiteSpace([string]$name)){continue}
      if([string]$name -match "[\\/]"){Fail "UNSAFE_DELIVERABLE" "Deliverables must be root filenames."}
      $p=Join-Path $ResultDir ([string]$name)
      if(-not(Test-Path $p -PathType Leaf)){Fail "DELIVERABLE_MISSING" ("Missing: "+$name)}
      $Files+=$p
    }
    if($Files.Count -eq 0){Fail "NO_DELIVERABLES" "No local Windows deliverables declared."}

    $Exe=@($Files|Where-Object{$_ -like "*.exe"}|Select-Object -First 1)
    if($Exe.Count -eq 1){
      $Sidecar=$Exe[0]+".sha256"
      if(Test-Path $Sidecar -PathType Leaf){
        $Expected=((Get-Content $Sidecar -Raw).Trim() -split "\s+")[0].ToLowerInvariant()
        $ActualHash=(Get-FileHash -Algorithm SHA256 $Exe[0]).Hash.ToLowerInvariant()
        if($Expected -ne $ActualHash){Fail "LOCAL_ARTIFACT_HASH_MISMATCH" "Windows executable SHA-256 differs from its sidecar."}
      }
    }

    $Evidence=Join-Path $Dest ("MBH-EVIDENCE-"+$Project+"-"+$Sha.Substring(0,12)+".zip")
    Compress-Archive -Path (Join-Path $ResultDir "*") -DestinationPath $Evidence -Force
    Write-Host "LOCAL_WINDOWS_BUILD_VERIFIED" -ForegroundColor Green
    Write-Host ("OUTPUT: "+$ResultDir) -ForegroundColor Cyan
    [IO.File]::WriteAllLines((Join-Path $DataRoot "LAST_BUILD.txt"),@($Project,$Branch,$Sha,"LOCAL_WINDOWS",$ResultDir))
    return $ResultDir
  }
  finally{
    if(Test-Path $SourceDir){Remove-Item -Recurse -Force $SourceDir -ErrorAction SilentlyContinue}
  }
}

function FailureClass($Text){
  $t=$Text.ToLowerInvariant()
  if($t -match "quota|spending limit|included usage|billing|payment method"){return "QUOTA_BLOCKED"}
  if($t -match "signing_secret_missing|keystore|signing identity"){return "SIGNING_NOT_READY"}
  if($t -match "timed out|timeout|exit code 124"){return "BUILD_TIMEOUT"}
  if($t -match "could not resolve|connection reset|network is unreachable|temporary failure"){return "NETWORK_TRANSIENT"}
  if($t -match "sdkmanager|android sdk|gradle|java_home|jdk"){return "TOOLCHAIN_FAILURE"}
  return "BUILD_FAILED"
}


function VerifyReleaseAssets($Repo,$Tag,$Files){
  $encoded=[uri]::EscapeDataString($Tag)
  $raw=& gh api ("repos/"+$Repo+"/releases/tags/"+$encoded) 2>$null
  if($LASTEXITCODE -ne 0 -or -not $raw){Fail "RELEASE_VERIFY_QUERY" "Cannot query the published release for verification."}
  $release=$raw|ConvertFrom-Json
  $assets=@($release.assets)
  foreach($local in @($Files)){
    if(-not(Test-Path $local -PathType Leaf)){Fail "RELEASE_LOCAL_ASSET_MISSING" ("Local asset disappeared before verification: "+$local)}
    $name=Split-Path $local -Leaf
    $found=@($assets|Where-Object{[string]$_.name -eq $name})
    if($found.Count -ne 1){Fail "RELEASE_ASSET_CARDINALITY" ("Expected exactly one uploaded asset named "+$name+"; found "+$found.Count+".")}
    $asset=$found[0]
    if([string]$asset.state -ne "uploaded"){Fail "RELEASE_ASSET_STATE" ("Release asset is not fully uploaded: "+$name)}
    $digest=[string]$asset.digest
    if([string]::IsNullOrWhiteSpace($digest) -or $digest -notmatch '^sha256:[0-9A-Fa-f]{64}$'){

      Fail "RELEASE_DIGEST_MISSING" ("GitHub did not expose a usable SHA-256 digest for "+$name+".")
    }
    $localHash=(Get-FileHash -Algorithm SHA256 $local).Hash.ToLowerInvariant()
    $remoteHash=$digest.Substring(7).ToLowerInvariant()
    if($localHash -ne $remoteHash){Fail "RELEASE_DIGEST_MISMATCH" ("Published asset digest differs from local verified artifact: "+$name)}
    if([long]$asset.size -ne [long](Get-Item $local).Length){Fail "RELEASE_SIZE_MISMATCH" ("Published asset size differs from local artifact: "+$name)}
  }
  return $release
}
function AssertRecoveryMarker(){
  $path=Join-Path $DataRoot "vault\DISASTER_RECOVERY_RESTORE_TEST_PASS.json"
  if(-not(Test-Path $path -PathType Leaf)){
    Fail "DISASTER_RECOVERY_NOT_VERIFIED" "Signed APK production is blocked until the encrypted signing backup has passed a functional restore test."
  }
  try{$marker=Get-Content $path -Raw|ConvertFrom-Json}catch{Fail "DISASTER_RECOVERY_MARKER_INVALID" "The recovery PASS marker is unreadable."}
  if([string]$marker.schema -ne "mbh-disaster-recovery-restore-test-v2" -or [string]$marker.result -ne "PASS"){
    Fail "DISASTER_RECOVERY_MARKER_STALE" "The recovery PASS marker is not the required V0.2 functional proof."
  }
  $profiles=@($marker.profiles)
  $evidence=@($marker.certificate_evidence)
  foreach($name in @("PhoneMouse","P2PCR95")){
    if($profiles -notcontains $name){Fail "DISASTER_RECOVERY_PROFILE_MISSING" ("Recovery proof is missing "+$name+".")}
    $expected=[string]$Registry.projects.$name.signing.certificate_sha256
    $found=@($evidence|Where-Object{[string]$_.profile -eq $name})
    if($found.Count -ne 1){Fail "DISASTER_RECOVERY_CERT_EVIDENCE" ("Recovery certificate evidence cardinality is invalid for "+$name+".")}
    if($found[0].keystore_opened -ne $true){Fail "DISASTER_RECOVERY_KEYSTORE_EVIDENCE" ("Recovery proof did not open the "+$name+" keystore.")}
    if(([string]$found[0].certificate_sha256).ToLowerInvariant() -ne $expected){
      Fail "DISASTER_RECOVERY_CERT_MISMATCH" ("Recovery proof certificate does not match the canonical "+$name+" identity.")
    }
  }
  return $marker
}

Need "gh" "GH_MISSING"
Need "git" "GIT_MISSING"
& gh auth status -h github.com *> $null
if($LASTEXITCODE -ne 0){Fail "GH_AUTH" "GitHub CLI is not authenticated."}

if($Mode -eq "Doctor"){
  & gh codespace list --limit 1 *> $null
  if($LASTEXITCODE -ne 0){Fail "CODESPACES_ACCESS" "Codespaces access missing; rerun bootstrap."}
  Write-Host "BUILD_HUB_DOCTOR_PASS" -ForegroundColor Green
  exit 0
}

$mutex=New-Object System.Threading.Mutex($false,"Local\MatriceBuildHub.SingleBuild")
$locked=$false
try{
  $locked=$mutex.WaitOne(0)
  if(-not $locked){Fail "BUILD_ALREADY_RUNNING" "Another BuildHub job is running on this PC."}

  if(-not $Project){
    $p=Pick
    $Project=$p[0]
    $Mode=$p[1]
  }

  $Cfg=$Registry.projects.$Project
  if(-not $Cfg){Fail "PROJECT_UNKNOWN" "Unknown project: $Project"}
  $Repo=[string]$Cfg.repo
  $RepoName=($Repo -split "/")[-1]
  if(-not $Branch){$Branch=[string]$Cfg.default_branch}
  SafeBranch $Branch

  $BuilderKind=[string]$Cfg.builder_kind
  if([string]::IsNullOrWhiteSpace($BuilderKind)){$BuilderKind="CODESPACES_LINUX"}
  if($BuilderKind -notin @("CODESPACES_LINUX","LOCAL_WINDOWS")){Fail "BUILDER_KIND_UNKNOWN" ("Unsupported builder kind: "+$BuilderKind)}

  $Sha=ResolveSha $Repo $Branch
  $Short=$Sha.Substring(0,12)
  $Stamp=Get-Date -Format "yyyyMMdd-HHmmss"
  $BuildId=("mbh-"+$Project.ToLower().Replace("-","")+"-"+$Short+"-"+$Stamp)
  if($BuildId.Length -gt 48){$BuildId=$BuildId.Substring(0,48)}
  $Dest=Join-Path $OutputRoot $BuildId
  New-Item -ItemType Directory -Force -Path $Dest|Out-Null

  if($BuilderKind -eq "LOCAL_WINDOWS"){
    InvokeLocalWindowsProject $Project $Cfg $Repo $Branch $Sha $BuildId $Dest $Mode|Out-Null
    return
  }

  CleanupStale
  $usage=Ledger
  $cap=[double]$Registry.policy.internal_monthly_core_hour_cap
  if([double]$usage.Data.estimated_core_hours -ge $cap){
    Fail "INTERNAL_BUDGET_GUARD" ("Estimated BuildHub use is "+$usage.Data.estimated_core_hours+" core-hours; internal cap is "+$cap+".")
  }

  $raw=& gh api ("repos/"+$Repo+"/codespaces/machines")
  if($LASTEXITCODE -ne 0){Fail "MACHINE_QUERY_FAILED" "Cannot query Codespaces machines."}
  $machines=($raw|ConvertFrom-Json).machines|Sort-Object cpus
  if(-not $machines){Fail "NO_MACHINE" "No Codespaces machine available."}
  $want=[int]$Registry.policy.preferred_machine_cores
  $M=$machines|Where-Object{[int]$_.cpus -eq $want}|Select-Object -First 1
  if(-not $M){$M=$machines|Select-Object -First 1}
  $Machine=[string]$M.name
  $Cores=[int]$M.cpus

  $Fallback=Join-Path $Root ([string]$Cfg.fallback_adapter)
  $Runner=Join-Path $Root "remote-runner.sh"
  if(-not(Test-Path $Fallback)){Fail "ADAPTER_MISSING" "Missing fallback adapter."}
  if(-not(Test-Path $Runner)){Fail "RUNNER_MISSING" "Missing remote-runner.sh."}
  $Recipe=[string]$Cfg.recipe_path
  $Timeout=[int]$Cfg.build_timeout_minutes

  Write-Host ""
  Write-Host ("Project : "+$Project) -ForegroundColor Green
  Write-Host ("Branch  : "+$Branch)
  Write-Host ("SHA     : "+$Sha)
  Write-Host ("Machine : "+$Machine+" ("+$Cores+" cores)")
  Write-Host ("Mode    : "+$Mode)
  Write-Host ("Ledger  : "+$usage.Data.estimated_core_hours+" / "+$cap+" core-hours")

  $CS=$null
  $Started=$null
  try{
    $Started=Get-Date
    & gh codespace create -R $Repo -b $Branch -d $BuildId -m $Machine --idle-timeout 10m --retention-period 1h --default-permissions|Out-Host
    if($LASTEXITCODE -ne 0){Fail "CODESPACE_CREATE_FAILED" "Codespace creation failed; quota or permissions may be blocking it."}

    for($i=0;$i -lt 45 -and -not $CS;$i++){
      Start-Sleep -Seconds 2
      $list=& gh codespace list -R $Repo --limit 100 --json name,displayName,state,createdAt|ConvertFrom-Json
      $CS=($list|Where-Object{$_.displayName -eq $BuildId}|Sort-Object createdAt -Descending|Select-Object -First 1).name
    }
    if(-not $CS){Fail "CODESPACE_DISCOVERY_FAILED" "Created Codespace cannot be located."}

    $view=$null
    for($i=0;$i -lt 120;$i++){
      $view=& gh codespace view -c $CS --json state,machineName,prebuild|ConvertFrom-Json
      if($view.state -eq "Available"){break}
      if([string]$view.state -match "Failed|Unavailable"){break}
      Start-Sleep -Seconds 3
    }
    if($view.state -ne "Available"){Fail "CODESPACE_NOT_READY" ("State: "+$view.state)}
    if($view.prebuild){Fail "PREBUILD_DETECTED" "This Codespace used a prebuild. Disable Codespaces prebuilds to preserve Actions minutes."}

    & gh codespace cp -c $CS $Runner "remote:/tmp/mbh-remote-runner.sh"|Out-Host
    if($LASTEXITCODE -ne 0){Fail "RUNNER_COPY_FAILED" "Cannot copy remote runner."}
    & gh codespace cp -c $CS $Fallback "remote:/tmp/matrix-build-fallback.sh"|Out-Host
    if($LASTEXITCODE -ne 0){Fail "ADAPTER_COPY_FAILED" "Cannot copy fallback adapter."}

    $cmd="bash /tmp/mbh-remote-runner.sh '$RepoName' '$Branch' '$Sha' '$Recipe' '$Timeout' '$Repo' '$BuildId' '$Mode'"
    $remote=& gh codespace ssh -c $CS $cmd 2>&1
    $rc=$LASTEXITCODE
    $text=$remote|Out-String
    $remote|ForEach-Object{Write-Host $_}

    & gh codespace cp -r -c $CS ("remote:/workspaces/"+$RepoName+"/.matrix-build-output") $Dest|Out-Host
    $copyRc=$LASTEXITCODE
    $ResultDir=Join-Path $Dest ".matrix-build-output"
    if($copyRc -ne 0 -or -not(Test-Path $ResultDir)){
      $ResultDir=$Dest
      Set-Content -Encoding UTF8 (Join-Path $ResultDir "REMOTE_OUTPUT.txt") $text
    }

    if($rc -ne 0){
      $class=FailureClass $text
      [IO.File]::WriteAllLines((Join-Path $DataRoot "LAST_FAILURE.txt"),@($class,$Project,$Branch,$Sha,$ResultDir))
      Fail $class ("Remote job failed. Diagnostics: "+$ResultDir)
    }

    $ResultFile=Join-Path $ResultDir "result.json"
    if(-not(Test-Path $ResultFile)){Fail "RESULT_MISSING" "result.json missing."}
    $Result=Get-Content $ResultFile -Raw|ConvertFrom-Json
    if($Result.schema -ne "mbh-result-v1"){Fail "RESULT_SCHEMA" "Unsupported result schema."}
    if([string]$Result.source_sha -ne $Sha){Fail "SOURCE_MISMATCH" "Built SHA differs from requested SHA."}

    if($Mode -eq "Smoke"){
      Write-Host "CLOUD_SMOKE_PASS" -ForegroundColor Green
      [IO.File]::WriteAllLines((Join-Path $DataRoot "LAST_SMOKE.txt"),@($Project,$Branch,$Sha,$ResultDir))
      return
    }

    $localSignedFiles=@()
    if($Result.local_signing -and $Result.local_signing.required -eq $true){
      if(-not $Cfg.signing){Fail "LOCAL_SIGN_CONFIG" "Repository requested local signing but registry has no signing profile."}
      if([string]$Result.local_signing.profile -ne [string]$Cfg.signing.profile){
        Fail "LOCAL_SIGN_PROFILE_MISMATCH" "Build result requested an unexpected signing profile."
      }

      $unsignedName=[string]$Result.local_signing.unsigned_apk
      $signedName=[string]$Result.local_signing.signed_apk
      foreach($name in @($unsignedName,$signedName)){
        if([string]::IsNullOrWhiteSpace($name) -or $name -match "[\\/]"){
          Fail "LOCAL_SIGN_PATH_UNSAFE" "APK filenames must be root filenames."
        }
      }

      $unsignedPath=Join-Path $ResultDir $unsignedName
      $signedPath=Join-Path $ResultDir $signedName
      if(-not(Test-Path $unsignedPath -PathType Leaf)){Fail "UNSIGNED_APK_MISSING" "Cloud build did not return the unsigned APK."}

      $RecoveryMarker=Join-Path $DataRoot "vault\DISASTER_RECOVERY_RESTORE_TEST_PASS.json"
      if(-not(Test-Path $RecoveryMarker)){
        Fail "DISASTER_RECOVERY_NOT_VERIFIED" "Signed APK production is blocked until the encrypted signing backup has passed a restore test."
      }
      $Signer=Join-Path $Root "local-sign-apk.ps1"
      if(-not(Test-Path $Signer)){Fail "LOCAL_SIGNER_MISSING" "local-sign-apk.ps1 is missing."}

      Write-Host "Cloud build verified. Performing lightweight local APK signing..." -ForegroundColor Cyan
      & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Signer -Project $Project -UnsignedApk $unsignedPath -SignedApk $signedPath -ExpectedVersionCode ([string]$Result.local_signing.version_code) -ExpectedVersionName ([string]$Result.local_signing.version_name)
      if($LASTEXITCODE -ne 0){Fail "LOCAL_SIGNING_FAILED" "Local APK signing or identity verification failed."}

      foreach($p in @($signedPath,$signedPath+".sha256",$signedPath+".signature.txt",$signedPath+".identity.txt")){
        if(-not(Test-Path $p -PathType Leaf)){Fail "LOCAL_SIGN_EVIDENCE_MISSING" "Local signing evidence is missing: $p"}
        $localSignedFiles+=$p
      }

      Set-Content -Encoding ASCII -Path (Join-Path $ResultDir "LOCAL_SIGNING_PASS.txt") -Value ("profile="+$Result.local_signing.profile+"; source_sha="+$Sha)
      $unsignedHash=(Get-FileHash -Algorithm SHA256 $unsignedPath).Hash.ToLowerInvariant()
      Set-Content -Encoding ASCII -Path (Join-Path $ResultDir "CLOUD_UNSIGNED_APK_SHA256.txt") -Value ($unsignedHash+"  "+$unsignedName)
      Remove-Item $unsignedPath -Force
      if(Test-Path ($unsignedPath+".sha256")){Remove-Item ($unsignedPath+".sha256") -Force}
      if(Test-Path $unsignedPath){Fail "UNSIGNED_APK_CLEANUP" "Unsigned APK could not be removed after successful local signing."}
    }

    $files=@()
    foreach($name in @($Result.deliverables)){
      if([string]::IsNullOrWhiteSpace([string]$name)){continue}
      if([string]$name -match "[\\/]"){Fail "UNSAFE_DELIVERABLE" "Deliverables must be root filenames."}
      $f=Join-Path $ResultDir ([string]$name)
      if(-not(Test-Path $f -PathType Leaf)){Fail "DELIVERABLE_MISSING" "Missing: $name"}
      $files+=$f
    }
    if($files.Count -eq 0){Fail "NO_DELIVERABLES" "No deliverables declared."}
    $files+=@($localSignedFiles)
    if($files.Count -eq 0){Fail "NO_FINAL_ARTIFACTS" "No final artifacts are available after local signing."}

    $evidence=Join-Path $Dest ("MBH-EVIDENCE-"+$Project+"-"+$Short+".zip")
    Compress-Archive -Path (Join-Path $ResultDir "*") -DestinationPath $evidence -Force
    $files+=$evidence

    Write-Host "BUILD_VERIFIED" -ForegroundColor Green

    if(-not $NoPublish -and $Result.publish -eq $true){
      $base=[string]$Result.tag
      if([string]::IsNullOrWhiteSpace($base)){$base="buildhub-"+$Project.ToLower()}
      $Tag=$base+"-"+$Short
      $Title=[string]$Result.title
      if([string]::IsNullOrWhiteSpace($Title)){$Title=$Project+" BuildHub "+$Short}

      & gh release view $Tag -R $Repo *> $null
      if($LASTEXITCODE -eq 0){
        $existing=& gh release view $Tag -R $Repo --json url,targetCommitish,assets,isDraft,isPrerelease|ConvertFrom-Json
        if($existing.targetCommitish -and [string]$existing.targetCommitish -ne $Sha){
          Fail "RELEASE_TARGET_MISMATCH" "Existing release tag points at a different source."
        }
        if($existing.isDraft -eq $true){Fail "RELEASE_INCOMPLETE" "Existing release is still a draft."}
        if($existing.isPrerelease -ne $true){Fail "RELEASE_MODE_MISMATCH" "BuildHub release must remain a prerelease."}
        $expectedNames=@($files|ForEach-Object{Split-Path $_ -Leaf}|Sort-Object -Unique)
        $remoteNames=@($existing.assets|ForEach-Object{[string]$_.name})
        $missing=@($expectedNames|Where-Object{$remoteNames -notcontains $_})
        if($missing.Count -gt 0){
          Fail "RELEASE_ASSET_MISMATCH" ("Existing release is missing assets: "+($missing -join ", "))
        }
        $Url=[string]$existing.url
      }else{
        $notes="MATRICE BUILD HUB V$HubVersion`nSource: $Repo@$Sha`nBranch: $Branch`nHosted GitHub Actions minutes used by BuildHub: 0"
        & gh release create $Tag @files -R $Repo --prerelease --latest=false --target $Sha --title $Title --notes $notes|Out-Host
        if($LASTEXITCODE -ne 0){Fail "RELEASE_FAILED" "Build passed but prerelease publication failed."}
        $Url=[string]((& gh release view $Tag -R $Repo --json url|ConvertFrom-Json).url)
      }

      Write-Host ("LINK: "+$Url) -ForegroundColor Cyan
      [IO.File]::WriteAllLines((Join-Path $DataRoot "LAST_BUILD.txt"),@($Project,$Branch,$Sha,$Url,$ResultDir))
    }
  }
  finally{
    if($CS){
      & gh codespace stop -c $CS *> $null
      $deleted=$false
      for($n=0;$n -lt 3 -and -not $deleted;$n++){
        & gh codespace delete -c $CS --force *> $null
        if($LASTEXITCODE -eq 0){$deleted=$true}else{Start-Sleep -Seconds 3}
      }
      if(-not $deleted){Write-Host "WARNING: builder stopped but deletion was not confirmed." -ForegroundColor Red}
    }
    if($Started -and $Cores -gt 0){
      AddUsage (((Get-Date)-$Started).TotalHours*[double]$Cores)
    }
  }
}
finally{
  if($locked){$mutex.ReleaseMutex()|Out-Null}
  $mutex.Dispose()
}
