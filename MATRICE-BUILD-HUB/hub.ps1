param(
  [ValidateSet("PhoneMouse","P2PCR95","ChatGPT-PC")][string]$Project,
  [string]$Branch,
  [ValidateSet("Build","Smoke","Doctor")][string]$Mode="Build",
  [switch]$NoPublish
)

$ErrorActionPreference="Stop"
$HubVersion="0.2"
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
  Write-Host "4. Diagnostic cloud seulement"
  $x=Read-Host "Choix"
  switch($x){
    "1"{return @("PhoneMouse","Build")}
    "2"{return @("P2PCR95","Build")}
    "3"{return @("ChatGPT-PC","Build")}
    "4"{return @("PhoneMouse","Smoke")}
    default{Fail "INVALID_CHOICE" "Choix invalide."}
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
  CleanupStale

  $usage=Ledger
  $cap=[double]$Registry.policy.internal_monthly_core_hour_cap
  if([double]$usage.Data.estimated_core_hours -ge $cap){
    Fail "INTERNAL_BUDGET_GUARD" ("Estimated BuildHub use is "+$usage.Data.estimated_core_hours+" core-hours; internal cap is "+$cap+".")
  }

  $Sha=ResolveSha $Repo $Branch
  $Short=$Sha.Substring(0,12)
  $Stamp=Get-Date -Format "yyyyMMdd-HHmmss"
  $BuildId=("mbh-"+$Project.ToLower().Replace("-","")+"-"+$Short+"-"+$Stamp)
  if($BuildId.Length -gt 48){$BuildId=$BuildId.Substring(0,48)}
  $Dest=Join-Path $OutputRoot $BuildId
  New-Item -ItemType Directory -Force -Path $Dest|Out-Null

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
