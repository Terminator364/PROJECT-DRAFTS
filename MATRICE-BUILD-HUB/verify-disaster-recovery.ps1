$ErrorActionPreference="Stop"
Add-Type -AssemblyName System.Windows.Forms

$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$Registry=Get-Content (Join-Path $Root "projects.json") -Raw|ConvertFrom-Json
$Base=Join-Path $env:LOCALAPPDATA "MatriceBuildHub"
$Vault=Join-Path $Base "vault"
New-Item -ItemType Directory -Force -Path $Vault|Out-Null

function Parse-Credentials([string]$Path){
  $map=@{}
  foreach($line in Get-Content $Path){
    if($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)=(.*)$'){
      $name=$matches[1]
      $value=$matches[2].Trim()
      if(
        ($value.StartsWith('"') -and $value.EndsWith('"')) -or
        ($value.StartsWith("'") -and $value.EndsWith("'"))
      ){
        $value=$value.Substring(1,$value.Length-2)
      }
      $map[$name]=$value
    }
  }
  return $map
}

function Find-Keytool {
  $cmd=Get-Command keytool -ErrorAction SilentlyContinue
  if($cmd){ return $cmd.Source }

  $state=Join-Path $Base "state\java-home.txt"
  if(Test-Path $state){
    $javaHome=(Get-Content $state -Raw).Trim()
    $candidate=Join-Path $javaHome "bin\keytool.exe"
    if(Test-Path $candidate){ return $candidate }
  }

  foreach($rootPath in @("C:\Program Files\Eclipse Adoptium","C:\Program Files\Java")){
    foreach($dir in @(Get-ChildItem $rootPath -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending)){
      $candidate=Join-Path $dir.FullName "bin\keytool.exe"
      if(Test-Path $candidate){ return $candidate }
    }
  }
  return $null
}

if(-not(Get-Command age -ErrorAction SilentlyContinue)){throw "[AGE_MISSING] Install age or run export-disaster-recovery.ps1 first."}
$keytool=Find-Keytool
if(-not $keytool){throw "[KEYTOOL_MISSING] JDK keytool is required for a functional restore test."}

$dialog=New-Object System.Windows.Forms.OpenFileDialog
$dialog.Title="Choisis la sauvegarde MatriceBuildHub-Recovery-*.zip.age"
$dialog.Filter="age encrypted backup (*.age)|*.age|All files (*.*)|*.*"
if($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK){throw "[VERIFY_CANCELLED] No backup selected."}
$Encrypted=$dialog.FileName

$profileSpec=@{
  "PhoneMouse"=[pscustomobject]@{
    Keystore="PhoneMouse-signing.jks"
    Prefix="PHONEMOUSE"
    ExpectedCert=[string]$Registry.projects.PhoneMouse.signing.certificate_sha256
  }
  "P2PCR95"=[pscustomobject]@{
    Keystore="P2PCR95-signing.jks"
    Prefix="P2PCR95"
    ExpectedCert=[string]$Registry.projects.P2PCR95.signing.certificate_sha256
  }
}

$temp=Join-Path $env:TEMP ("mbh-recovery-verify-"+[guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $temp|Out-Null
try{
  $bundle=Join-Path $temp "recovery.zip"
  Write-Host "Entre la phrase secrete de la sauvegarde." -ForegroundColor Cyan
  & age -d -o $bundle $Encrypted
  if($LASTEXITCODE -ne 0 -or -not(Test-Path $bundle)){throw "[RECOVERY_DECRYPT] Backup decryption failed."}

  $extract=Join-Path $temp "extract"
  Expand-Archive -Path $bundle -DestinationPath $extract -Force
  $manifestPath=Join-Path $extract "RECOVERY_MANIFEST.json"
  if(-not(Test-Path $manifestPath)){throw "[RECOVERY_MANIFEST] Manifest missing."}
  $manifest=Get-Content $manifestPath -Raw|ConvertFrom-Json
  if($manifest.schema -ne "mbh-disaster-recovery-v1"){throw "[RECOVERY_SCHEMA] Unexpected recovery manifest schema."}

  $seen=@{}
  $certEvidence=@()
  foreach($p in @($manifest.profiles)){
    $profile=[string]$p.name
    if(-not $profileSpec.ContainsKey($profile)){throw "[RECOVERY_PROFILE_UNKNOWN] $profile"}
    $leaf=[string]$p.file
    if([string]::IsNullOrWhiteSpace($leaf) -or (Split-Path $leaf -Leaf) -ne $leaf){throw "[RECOVERY_PATH_UNSAFE] $leaf"}

    $file=Join-Path $extract $leaf
    if(-not(Test-Path $file -PathType Leaf)){throw "[RECOVERY_FILE_MISSING] $leaf"}
    $sha=(Get-FileHash -Algorithm SHA256 $file).Hash.ToLowerInvariant()
    if($sha -ne ([string]$p.sha256).ToLowerInvariant()){throw "[RECOVERY_HASH_MISMATCH] $profile"}

    $spec=$profileSpec[$profile]
    if($spec.ExpectedCert -notmatch '^[0-9a-f]{64}$'){throw "[RECOVERY_EXPECTED_CERT_INVALID] $profile"}

    $profileDir=Join-Path $temp ("profile-"+$profile)
    New-Item -ItemType Directory -Force -Path $profileDir|Out-Null
    Expand-Archive -Path $file -DestinationPath $profileDir -Force

    $jks=Get-ChildItem $profileDir -Recurse -File -Filter $spec.Keystore|Select-Object -First 1
    $cred=Get-ChildItem $profileDir -Recurse -File -Filter "SIGNING-CREDENTIALS.txt"|Select-Object -First 1
    if(-not $jks){throw "[RECOVERY_KEYSTORE_MISSING] $profile"}
    if(-not $cred){throw "[RECOVERY_CREDENTIALS_MISSING] $profile"}

    $vars=Parse-Credentials $cred.FullName
    $storeKey=$spec.Prefix+"_KEYSTORE_PASSWORD"
    $aliasKey=$spec.Prefix+"_KEY_ALIAS"
    foreach($required in @($storeKey,$aliasKey)){
      if(-not $vars.ContainsKey($required) -or [string]::IsNullOrEmpty([string]$vars[$required])){
        throw "[RECOVERY_CREDENTIAL_MISSING] $profile/$required"
      }
    }

    $env:MBH_RECOVERY_STOREPASS=[string]$vars[$storeKey]
    try{
      $keytoolOutput=& $keytool -J-Duser.language=en -J-Duser.country=US -list -v -keystore $jks.FullName -storepass:env MBH_RECOVERY_STOREPASS -alias ([string]$vars[$aliasKey]) 2>&1|Out-String
      if($LASTEXITCODE -ne 0){throw "[RECOVERY_KEYSTORE_OPEN_FAILED] $profile"}
    }finally{
      Remove-Item Env:MBH_RECOVERY_STOREPASS -ErrorAction SilentlyContinue
    }

    $m=[regex]::Match($keytoolOutput,'SHA256:\s*([0-9A-Fa-f:]+)')
    if(-not $m.Success){throw "[RECOVERY_CERT_PARSE] $profile"}
    $actualCert=$m.Groups[1].Value.ToLowerInvariant().Replace(":","")
    if($actualCert -ne $spec.ExpectedCert){throw "[RECOVERY_CERT_MISMATCH] $profile"}

    $seen[$profile]=$true
    $certEvidence+=[pscustomobject]@{
      profile=$profile
      archive_sha256=$sha
      certificate_sha256=$actualCert
      keystore_opened=$true
    }
  }

  foreach($required in @("PhoneMouse","P2PCR95")){
    if(-not $seen.ContainsKey($required)){throw "[RECOVERY_PROFILE_MISSING] $required"}
  }

  $encHash=(Get-FileHash -Algorithm SHA256 $Encrypted).Hash.ToLowerInvariant()
  $sidecar=$Encrypted+".sha256"
  if(Test-Path $sidecar){
    $declared=((Get-Content $sidecar -Raw).Trim() -split '\s+')[0].ToLowerInvariant()
    if($declared -notmatch '^[0-9a-f]{64}$' -or $declared -ne $encHash){throw "[RECOVERY_ENCRYPTED_HASH_MISMATCH] Sidecar SHA-256 does not match selected backup."}
  }

  $marker=Join-Path $Vault "DISASTER_RECOVERY_RESTORE_TEST_PASS.json"
  [pscustomobject]@{
    schema="mbh-disaster-recovery-restore-test-v2"
    verified_at=(Get-Date).ToString("o")
    encrypted_backup=$Encrypted
    encrypted_sha256=$encHash
    profiles=@("PhoneMouse","P2PCR95")
    certificate_evidence=$certEvidence
    functional_restore_validation="DECRYPT_HASH_OPEN_KEYSTORE_VERIFY_CERTIFICATE"
    result="PASS"
  }|ConvertTo-Json -Depth 8|Set-Content -Encoding UTF8 $marker

  Write-Host "DISASTER_RECOVERY_RESTORE_TEST_PASS" -ForegroundColor Green
  Write-Host "Backup decrypted, payload hashes matched, keystores opened, and canonical certificates matched." -ForegroundColor Green
}finally{
  Remove-Item Env:MBH_RECOVERY_STOREPASS -ErrorAction SilentlyContinue
  if(Test-Path $temp){Remove-Item $temp -Recurse -Force -ErrorAction SilentlyContinue}
}
