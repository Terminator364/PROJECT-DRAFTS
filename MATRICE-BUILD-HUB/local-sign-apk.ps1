param(
  [Parameter(Mandatory=$true)][ValidateSet("PhoneMouse","P2PCR95")][string]$Project,
  [Parameter(Mandatory=$true)][string]$UnsignedApk,
  [Parameter(Mandatory=$true)][string]$SignedApk,
  [Parameter(Mandatory=$true)][string]$ExpectedVersionCode,
  [Parameter(Mandatory=$true)][string]$ExpectedVersionName
)

$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$Registry=Get-Content (Join-Path $Root "projects.json") -Raw|ConvertFrom-Json
$Cfg=$Registry.projects.$Project
if(-not $Cfg -or -not $Cfg.signing){throw "[SIGNING_CONFIG] Signing config missing for $Project."}

$Base=Join-Path $env:LOCALAPPDATA "MatriceBuildHub"
$Vault=Join-Path $Base "vault"
$Sdk=Join-Path $Base "android-sdk"
$BuildTools=[string]$Registry.policy.android_build_tools
$JavaState=Join-Path $Base "state\java-home.txt"
if(Test-Path $JavaState){
  $env:JAVA_HOME=(Get-Content $JavaState -Raw).Trim()
  $javaBin=Join-Path $env:JAVA_HOME "bin"
  if(Test-Path $javaBin){ $env:Path=$javaBin+";"+$env:Path }
}
$BT=Join-Path $Sdk ("build-tools\"+$BuildTools)
$ZipAlign=Join-Path $BT "zipalign.exe"
$ApkSigner=Join-Path $BT "apksigner.bat"
$Aapt=Join-Path $BT "aapt.exe"

foreach($p in @($UnsignedApk,$ZipAlign,$ApkSigner,$Aapt)){
  if(-not(Test-Path $p)){throw "[LOCAL_SIGNING_INPUT] Required file missing: $p"}
}

$Profile=[string]$Cfg.signing.profile
$VaultFile=Join-Path $Vault ($Profile+".signing.dpapi")
if(-not(Test-Path $VaultFile)){throw "[SIGNING_VAULT_MISSING] Run migrate-signing.ps1 before building."}

function Unprotect-Bytes([byte[]]$Bytes,[string]$ProfileName){
  Add-Type -AssemblyName System.Security
  $entropy=[Text.Encoding]::UTF8.GetBytes("MatriceBuildHub|"+$ProfileName+"|v0.2")
  return [Security.Cryptography.ProtectedData]::Unprotect($Bytes,$entropy,[Security.Cryptography.DataProtectionScope]::CurrentUser)
}
function Parse-Credentials([string]$Path){
  $map=@{}
  foreach($line in Get-Content $Path){
    if($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)=(.*)$'){
      $n=$matches[1]
      $v=$matches[2].Trim()
      if(($v.StartsWith('"') -and $v.EndsWith('"')) -or ($v.StartsWith("'") -and $v.EndsWith("'"))){$v=$v.Substring(1,$v.Length-2)}
      $map[$n]=$v
    }
  }
  return $map
}

$prefix=if($Project -eq "PhoneMouse"){"PHONEMOUSE"}else{"P2PCR95"}
$keystoreName=if($Project -eq "PhoneMouse"){"PhoneMouse-signing.jks"}else{"P2PCR95-signing.jks"}
$temp=Join-Path $env:TEMP ("mbh-local-sign-"+[guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $temp|Out-Null

try{
  $zip=Join-Path $temp "signing.zip"
  $plain=Unprotect-Bytes ([IO.File]::ReadAllBytes($VaultFile)) $Profile
  [IO.File]::WriteAllBytes($zip,$plain)
  $extract=Join-Path $temp "extract"
  Expand-Archive -Path $zip -DestinationPath $extract -Force
  $jks=Get-ChildItem $extract -Recurse -File -Filter $keystoreName|Select-Object -First 1
  $cred=Get-ChildItem $extract -Recurse -File -Filter "SIGNING-CREDENTIALS.txt"|Select-Object -First 1
  if(-not $jks -or -not $cred){throw "[SIGNING_VAULT_INVALID] Keystore or credentials missing."}
  $vars=Parse-Credentials $cred.FullName

  $storeKey=$prefix+"_KEYSTORE_PASSWORD"
  $aliasKey=$prefix+"_KEY_ALIAS"
  $keyKey=$prefix+"_KEY_PASSWORD"
  foreach($n in @($storeKey,$aliasKey,$keyKey)){if(-not $vars.ContainsKey($n) -or [string]::IsNullOrEmpty([string]$vars[$n])){throw "[SIGNING_CREDENTIAL_MISSING] $n"}}

  $preBadging=Join-Path $temp "unsigned-badging.txt"
  & $Aapt dump badging $UnsignedApk|Tee-Object -FilePath $preBadging|Out-Host
  if($LASTEXITCODE -ne 0){throw "[AAPT_UNSIGNED] Cannot inspect unsigned APK."}
  $badging=Get-Content $preBadging -Raw
  $app=[string]$Cfg.signing.application_id
  if($badging -notmatch ("package: name='"+[regex]::Escape($app)+"'")){throw "[APP_ID_MISMATCH] Unsigned APK package ID is not $app."}
  if($badging -notmatch ("versionCode='"+[regex]::Escape($ExpectedVersionCode)+"'")){throw "[VERSION_CODE_MISMATCH] Unexpected versionCode."}
  if($badging -notmatch ("versionName='"+[regex]::Escape($ExpectedVersionName)+"'")){throw "[VERSION_NAME_MISMATCH] Unexpected versionName."}

  $aligned=Join-Path $temp "aligned.apk"
  & $ZipAlign -P 16 -f -v 4 $UnsignedApk $aligned|Out-Host
  if($LASTEXITCODE -ne 0){throw "[ZIPALIGN] APK alignment failed."}
  & $ZipAlign -c -P 16 -v 4 $aligned|Out-Host
  if($LASTEXITCODE -ne 0){throw "[ZIPALIGN_VERIFY] Aligned APK verification failed."}

  $env:MBH_STORE_PASS=[string]$vars[$storeKey]
  $env:MBH_KEY_PASS=[string]$vars[$keyKey]
  $outDir=Split-Path -Parent $SignedApk
  if($outDir){New-Item -ItemType Directory -Force -Path $outDir|Out-Null}
  if(Test-Path $SignedApk){Remove-Item $SignedApk -Force}

  & $ApkSigner sign --ks $jks.FullName --ks-key-alias ([string]$vars[$aliasKey]) --ks-pass env:MBH_STORE_PASS --key-pass env:MBH_KEY_PASS --out $SignedApk $aligned
  if($LASTEXITCODE -ne 0){throw "[APKSIGNER_SIGN] APK signing failed."}

  $verify=Join-Path $temp "signature.txt"
  & $ApkSigner verify --verbose --print-certs $SignedApk|Tee-Object -FilePath $verify|Out-Host
  if($LASTEXITCODE -ne 0){throw "[APKSIGNER_VERIFY] Signed APK verification failed."}
  $vt=Get-Content $verify -Raw
  $m=[regex]::Match($vt,"Signer #1 certificate SHA-256 digest:\s*([0-9A-Fa-f:]+)")
  if(-not $m.Success){throw "[CERT_PARSE] Cannot read signing certificate digest."}
  $cert=$m.Groups[1].Value.ToLowerInvariant().Replace(":","")
  $expected=[string]$Cfg.signing.certificate_sha256
  if($cert -ne $expected){throw "[CERT_MISMATCH] Signed APK certificate does not match canonical identity."}

  $postBadging=Join-Path $temp "signed-badging.txt"
  & $Aapt dump badging $SignedApk|Tee-Object -FilePath $postBadging|Out-Host
  if($LASTEXITCODE -ne 0){throw "[AAPT_SIGNED] Cannot inspect signed APK."}
  $post=Get-Content $postBadging -Raw
  if($post -notmatch ("package: name='"+[regex]::Escape($app)+"'")){throw "[POSTSIGN_APP_ID] Package ID changed after signing."}
  if($post -notmatch ("versionCode='"+[regex]::Escape($ExpectedVersionCode)+"'")){throw "[POSTSIGN_VERSION_CODE] versionCode changed after signing."}
  if($post -notmatch ("versionName='"+[regex]::Escape($ExpectedVersionName)+"'")){throw "[POSTSIGN_VERSION_NAME] versionName changed after signing."}

  if((Get-Item $SignedApk).Length -le 0){throw "[SIGNED_APK_EMPTY] Signed APK is empty."}
  $hash=(Get-FileHash -Algorithm SHA256 $SignedApk).Hash.ToLowerInvariant()
  Set-Content -Encoding ASCII -Path ($SignedApk+".sha256") -Value ($hash+"  "+(Split-Path $SignedApk -Leaf))
  Copy-Item $verify ($SignedApk+".signature.txt") -Force
  Copy-Item $postBadging ($SignedApk+".identity.txt") -Force
  Write-Host ("LOCAL_APK_SIGN_PASS: "+$SignedApk) -ForegroundColor Green
}finally{
  Remove-Item Env:MBH_STORE_PASS -ErrorAction SilentlyContinue
  Remove-Item Env:MBH_KEY_PASS -ErrorAction SilentlyContinue
  if(Test-Path $temp){Remove-Item $temp -Recurse -Force -ErrorAction SilentlyContinue}
}
