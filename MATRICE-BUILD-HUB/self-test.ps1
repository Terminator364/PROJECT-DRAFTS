$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot=Split-Path -Parent $Root
$errors=@()

function Pass([string]$Message){Write-Host ("PASS "+$Message)}
function FailCheck([string]$Message){$script:errors+=$Message}
function Require-Token([string]$File,[string]$Token,[string]$Code){
  $p=Join-Path $Root $File
  if(-not(Test-Path $p -PathType Leaf)){FailCheck ("MISSING_FILE: "+$File);return}
  $text=Get-Content $p -Raw
  if($text.Contains($Token)){Pass ($Code+": "+$File)}else{FailCheck ($Code+": "+$File+" missing token "+$Token)}
}

Write-Host "MATRICE BUILD HUB V0.2 - STATIC SELF TEST" -ForegroundColor Cyan

$requiredFiles=@(
  "hub.ps1","launcher.ps1","bootstrap-pc.ps1","remote-runner.sh",
  "local-sign-apk.ps1","migrate-signing.ps1","migrate-durable-inputs.ps1",
  "setup-local-signing-tools.ps1","export-disaster-recovery.ps1",
  "verify-disaster-recovery.ps1","projects.json","AX150K_CONTEXT.json",
  "AX150K_ADAPTER.json","AX150K_HARNESS.json",
  ".ax15go\buildhub_static_harness.py",
  "adapters\phonemouse.sh","adapters\p2pcr95.sh","adapters\chatgpt-pc.sh"
)
foreach($name in $requiredFiles){
  if(Test-Path (Join-Path $Root $name) -PathType Leaf){Pass ("exists: "+$name)}
  else{FailCheck ("MISSING_FILE: "+$name)}
}

$psFiles=Get-ChildItem $Root -File -Filter "*.ps1"
foreach($f in $psFiles){
  $tokens=$null
  $parseErrors=$null
  [void][System.Management.Automation.Language.Parser]::ParseFile($f.FullName,[ref]$tokens,[ref]$parseErrors)
  if($parseErrors -and $parseErrors.Count -gt 0){
    foreach($e in $parseErrors){FailCheck ("POWERSHELL_PARSE: "+$f.Name+": "+$e.Message)}
  }else{
    Pass ("PowerShell parse: "+$f.Name)
  }
}

$jsonFiles=@("projects.json","AX150K_CONTEXT.json","AX150K_ADAPTER.json","AX150K_HARNESS.json","CHATGPT_PC_TUNNEL_CONTRACT.json","managed-app\\manifest.template.json")
$json=@{}
foreach($name in $jsonFiles){
  $p=Join-Path $Root $name
  try{
    $json[$name]=Get-Content $p -Raw|ConvertFrom-Json
    Pass ("JSON: "+$name)
  }catch{FailCheck ("JSON_PARSE: "+$name+": "+$_.Exception.Message)}
}

if($json.ContainsKey("projects.json")){
  $registry=$json["projects.json"]
  if([string]$registry.version -eq "0.2"){Pass "registry version 0.2"}else{FailCheck "REGISTRY_VERSION"}
  if([int]$registry.policy.actions_hosted_default_minutes_per_day -eq 0){Pass "hosted Actions default 0"}else{FailCheck "HOSTED_ACTIONS_POLICY"}
  if($registry.policy.codespaces_prebuilds -eq $false){Pass "Codespaces prebuilds disabled"}else{FailCheck "PREBUILD_POLICY"}
  if([string]$registry.policy.signing_mode -eq "LOCAL_WINDOWS_DPAPI"){Pass "local DPAPI signing mode"}else{FailCheck "SIGNING_MODE"}
  foreach($name in @("PhoneMouse","P2PCR95","ChatGPT-PC")){
    $cfg=$registry.projects.$name
    if(-not $cfg){FailCheck ("REGISTRY_PROJECT_MISSING: "+$name);continue}
    if([string]$cfg.recipe_path -eq ".matrix-build/build.sh"){Pass ("source-owned recipe: "+$name)}else{FailCheck ("RECIPE_PATH: "+$name)}
  }
}

if($json.ContainsKey("AX150K_CONTEXT.json")){
  $status=@{}
  foreach($source in @($json["AX150K_CONTEXT.json"].sources)){$status[[string]$source.id]=[string]$source.status}
  foreach($remoteId in @("github_phonemouse_beta11","github_p2pcr95_beta03","github_chatgpt_pc_active")){
    if($status[$remoteId] -eq "referenced"){Pass ("AX15 remote source referenced: "+$remoteId)}
    else{FailCheck ("AX15_REMOTE_SOURCE_FALSE_MATERIALIZATION: "+$remoteId+"="+$status[$remoteId])}
  }
  if($status["user_pc_runtime"] -eq "inaccessible_until_field_run"){Pass "AX15 real PC evidence pending honestly"}else{FailCheck "AX15_PC_EVIDENCE_STATUS"}
  if($status["github_codespaces_runtime"] -eq "inaccessible_until_field_run"){Pass "AX15 Codespaces evidence pending honestly"}else{FailCheck "AX15_CODESPACE_EVIDENCE_STATUS"}
}

if($json.ContainsKey("AX150K_ADAPTER.json")){
  $gates=@($json["AX150K_ADAPTER.json"].certification_gates)
  foreach($gate in @(
    "STATIC_AUDIT_PASS","ZERO_AUTO_ACTIONS_ACTIVE_BRANCHES","LOCAL_BOOTSTRAP_PASS",
    "LOCAL_SIGNING_VAULT_PASS","DISASTER_RECOVERY_EXPORT_PASS",
    "DISASTER_RECOVERY_RESTORE_TEST_PASS","CLOUD_SMOKE_PASS","ANDROID_CLOUD_BUILD_PASS",
    "LOCAL_SIGNATURE_PASS","RELEASE_ASSET_DIGESTS_PASS",
    "UPDATE_OVER_EXISTING_APP_PASS","SECOND_INDEPENDENT_BUILD_PASS"
  )){
    if($gates -contains $gate){Pass ("AX15 gate: "+$gate)}else{FailCheck ("AX15_GATE_MISSING: "+$gate)}
  }
}

Require-Token "hub.ps1" "Local\MatriceBuildHub.SingleBuild" "MUTEX"
Require-Token "hub.ps1" "PREBUILD_DETECTED" "PREBUILD_GUARD"
Require-Token "hub.ps1" "SOURCE_MISMATCH" "SOURCE_SHA_GUARD"
Require-Token "hub.ps1" '--target $Sha' "RELEASE_TARGET_SHA"
Require-Token "hub.ps1" "RELEASE_DIGEST_MISMATCH" "RELEASE_DIGEST_GUARD"
Require-Token "hub.ps1" "RELEASE_ASSET_DIGESTS_PASS" "RELEASE_DIGEST_GATE"
Require-Token "hub.ps1" "AssertRecoveryMarker" "RECOVERY_MARKER_VALIDATION"
Require-Token "hub.ps1" "INTERNAL_BUDGET_RESERVATION" "PROJECTED_BUDGET_GUARD"
Require-Token "hub.ps1" "CODESPACE_DELETE_FAILED" "CLEANUP_CERTIFICATION_GUARD"
Require-Token "remote-runner.sh" 'bash -n "$SCRIPT"' "SELECTED_RECIPE_PARSE"
Require-Token "setup-local-signing-tools.ps1" "SDKMANAGER_TIMEOUT" "SDKMANAGER_TIMEOUT_GUARD"
Require-Token "launcher.ps1" "HUB_UPDATE_FAILED" "STALE_LAUNCHER_GUARD"
Require-Token "bootstrap-pc.ps1" "HUB_FETCH_FAILED" "BOOTSTRAP_REFRESH_GUARD"
Require-Token "migrate-signing.ps1" "CERT_MISMATCH" "MIGRATION_CERT_GUARD"
Require-Token "migrate-signing.ps1" "ProtectedData" "DPAPI_GUARD"
Require-Token "local-sign-apk.ps1" "APP_ID_MISMATCH" "APK_PACKAGE_GUARD"
Require-Token "local-sign-apk.ps1" "CERT_MISMATCH" "APK_CERT_GUARD"
Require-Token "verify-disaster-recovery.ps1" "mbh-disaster-recovery-restore-test-v2" "RECOVERY_V2"
Require-Token "verify-disaster-recovery.ps1" "RECOVERY_CERT_MISMATCH" "RECOVERY_CERT_GUARD"
Require-Token "verify-disaster-recovery.ps1" "RECOVERY_KEYSTORE_OPEN_FAILED" "RECOVERY_KEYSTORE_GUARD"
Require-Token "export-disaster-recovery.ps1" 'if($plainBundle -and (Test-Path $plainBundle))' "RECOVERY_PLAINTEXT_CLEANUP"
Require-Token "managed-app\\bridge.py" "OPERATIONS={" "MANAGED_FIXED_OPERATIONS"
Require-Token "managed-app\\bridge.py" "shell=False" "MANAGED_NO_SHELL"
Require-Token "managed-app\\manifest.template.json" "R2_MISSION_SCOPED_ZERO_CLICK" "MANAGED_R2_ACTIVATION"
Require-Token "CHATGPT_PC_TUNNEL_CONTRACT.json" "CHATGPT_PC_CONTROL_BUS" "TUNNEL_NORMAL_ENTRYPOINT"
Require-Token "CHATGPT_PC_TUNNEL_CONTRACT.json" "BREAK_GLASS_ONLY" "MANUAL_BREAK_GLASS_ONLY"

$hubText=Get-Content (Join-Path $Root "hub.ps1") -Raw
$runtimeEntryCount=[regex]::Matches($hubText,'Need "gh" "GH_MISSING"').Count
$releaseVerifierCount=[regex]::Matches($hubText,'function VerifyReleaseAssets').Count
$recoveryVerifierCount=[regex]::Matches($hubText,'function AssertRecoveryMarker').Count
if($runtimeEntryCount -ne 1 -or $releaseVerifierCount -ne 1 -or $recoveryVerifierCount -ne 1){
  FailCheck ("HUB_DUPLICATION_GUARD: runtime="+$runtimeEntryCount+" release="+$releaseVerifierCount+" recovery="+$recoveryVerifierCount)
}else{Pass "hub duplication guard"}

if($hubText.ToLowerInvariant().Contains("workflow run") -or $hubText.ToLowerInvariant().Contains("actions/workflows")){
  FailCheck "HOSTED_ACTIONS_DISPATCH_PRESENT"
}else{Pass "no hosted Actions dispatch in hub"}

if($hubText.Contains("KEYSTORE_B64") -or $hubText.Contains("gh secret set")){
  FailCheck "CLOUD_SIGNING_SECRET_PATH_PRESENT"
}else{Pass "no cloud signing secret upload in hub"}

$attr=Join-Path $RepoRoot ".gitattributes"
if(Test-Path $attr -PathType Leaf){
  $attrText=Get-Content $attr -Raw
  if($attrText -match '(?m)^\*\.sh\s+text\s+eol=lf\s*$'){Pass "shell scripts forced to LF"}
  else{FailCheck "GITATTRIBUTES_SH_LF_MISSING"}
}else{FailCheck "GITATTRIBUTES_MISSING"}

$bash=$null
$bashCmd=Get-Command bash -ErrorAction SilentlyContinue
if($bashCmd){$bash=$bashCmd.Source}
foreach($candidate in @(
  (Join-Path $env:ProgramFiles "Git\bin\bash.exe"),
  (Join-Path $env:LOCALAPPDATA "Programs\Git\bin\bash.exe")
)){
  if(-not $bash -and $candidate -and (Test-Path $candidate)){$bash=$candidate}
}
if(-not $bash){
  FailCheck "BASH_MISSING_FOR_SHELL_SYNTAX"
}else{
  foreach($name in @("remote-runner.sh","adapters\phonemouse.sh","adapters\p2pcr95.sh","adapters\chatgpt-pc.sh")){
    $p=Join-Path $Root $name
    & $bash -n $p
    if($LASTEXITCODE -eq 0){Pass ("Bash parse: "+$name)}else{FailCheck ("BASH_PARSE: "+$name)}
  }
}

$python=Get-Command python -ErrorAction SilentlyContinue
if(-not $python){$python=Get-Command py -ErrorAction SilentlyContinue}
if($python){
  $script=Join-Path $Root ".ax15go\buildhub_static_harness.py"
  if($python.Name -eq "py.exe"){
    & $python.Source -3 $script
  }else{
    & $python.Source $script
  }
  if($LASTEXITCODE -ne 0){FailCheck "AX150K_STATIC_HARNESS_FAILED"}else{Pass "AX150K independent Python harness"}
  foreach($managed in @("managed-app\\bridge.py","managed-app\\selftest.py","managed-app\\make-package.py")){
    $mp=Join-Path $Root $managed
    if($python.Name -eq "py.exe"){
      & $python.Source -3 -m py_compile $mp
    }else{
      & $python.Source -m py_compile $mp
    }
    if($LASTEXITCODE -ne 0){FailCheck ("MANAGED_PYTHON_PARSE: "+$managed)}else{Pass ("managed Python parse: "+$managed)}
  }
}else{
  Write-Host "Python independent harness unavailable locally; PowerShell structural gates remain authoritative for bootstrap." -ForegroundColor Yellow
}

if($errors.Count -gt 0){
  Write-Host ""
  $errors|ForEach-Object{Write-Host $_ -ForegroundColor Red}
  throw "[STATIC_SELF_TEST_FAILED] $($errors.Count) checks failed."
}

Write-Host "STATIC_SELF_TEST_PASS" -ForegroundColor Green
