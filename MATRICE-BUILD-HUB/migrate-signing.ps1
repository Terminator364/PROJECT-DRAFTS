param([ValidateSet("All","PhoneMouse","P2PCR95")][string]$Profile="All")

$ErrorActionPreference="Stop"
$DataRoot=Join-Path $env:LOCALAPPDATA "MatriceBuildHub"
$Vault=Join-Path $DataRoot "vault"
$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$Registry=Get-Content (Join-Path $Root "projects.json") -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Force -Path $Vault | Out-Null

function Fail($Code,$Message){ throw "[$Code] $Message" }

function Protect-Bytes([byte[]]$Bytes,[string]$ProfileName){
  Add-Type -AssemblyName System.Security
  $entropy=[Text.Encoding]::UTF8.GetBytes("MatriceBuildHub|"+$ProfileName+"|v0.2")
  return [Security.Cryptography.ProtectedData]::Protect(
    $Bytes,$entropy,[Security.Cryptography.DataProtectionScope]::CurrentUser
  )
}

function Unprotect-Bytes([byte[]]$Bytes,[string]$ProfileName){
  Add-Type -AssemblyName System.Security
  $entropy=[Text.Encoding]::UTF8.GetBytes("MatriceBuildHub|"+$ProfileName+"|v0.2")
  return [Security.Cryptography.ProtectedData]::Unprotect(
    $Bytes,$entropy,[Security.Cryptography.DataProtectionScope]::CurrentUser
  )
}

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

  $state=Join-Path $DataRoot "state\java-home.txt"
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

function Invoke-RestWithRetry([string]$Uri,[hashtable]$Headers){
  $last=$null
  for($attempt=1;$attempt -le 3;$attempt++){
    try{
      return Invoke-RestMethod -UseBasicParsing -Headers $Headers -Uri $Uri -Method Get -TimeoutSec 45
    }catch{
      $last=$_
      if($attempt -lt 3){ Start-Sleep -Seconds (2*$attempt) }
    }
  }
  throw $last
}

function Download-WithRetry([string]$Uri,[hashtable]$Headers,[string]$OutFile){
  $last=$null
  for($attempt=1;$attempt -le 3;$attempt++){
    try{
      Remove-Item $OutFile -Force -ErrorAction SilentlyContinue
      Invoke-WebRequest -UseBasicParsing -Headers $Headers -Uri $Uri -OutFile $OutFile -TimeoutSec 90
      if((Test-Path $OutFile) -and (Get-Item $OutFile).Length -gt 0){ return }
      throw "Downloaded file is empty."
    }catch{
      $last=$_
      if($attempt -lt 3){ Start-Sleep -Seconds (2*$attempt) }
    }
  }
  throw $last
}

if(-not(Get-Command gh -ErrorAction SilentlyContinue)){ Fail "GH_MISSING" "GitHub CLI is missing." }
& gh auth status -h github.com *> $null
if($LASTEXITCODE -ne 0){ Fail "GH_AUTH" "GitHub CLI is not authenticated." }

$keytool=Find-Keytool
if(-not $keytool){ Fail "KEYTOOL_MISSING" "JDK keytool could not be located." }

$profiles=@(
  [pscustomobject]@{
    Name="PhoneMouse"
    Repo="Terminator364/PhoneMouse"
    Artifact="PhoneMouse-SIGNING-IDENTITY-CANONICAL"
    Keystore="PhoneMouse-signing.jks"
    Prefix="PHONEMOUSE"
  },
  [pscustomobject]@{
    Name="P2PCR95"
    Repo="Terminator364/P2PCR95"
    Artifact="P2PCR95-SIGNING-IDENTITY-CANONICAL"
    Keystore="P2PCR95-signing.jks"
    Prefix="P2PCR95"
  }
)

foreach($cfg in $profiles){
  if($Profile -ne "All" -and $Profile -ne $cfg.Name){ continue }

  $vaultFile=Join-Path $Vault ($cfg.Name+".signing.dpapi")
  $metaFile=Join-Path $Vault ($cfg.Name+".signing.json")
  $temp=Join-Path $env:TEMP ("mbh-signing-"+[guid]::NewGuid().ToString("N"))
  New-Item -ItemType Directory -Force -Path $temp | Out-Null

  try{
    $zip=Join-Path $temp "signing.zip"
    $source=""

    $token=(& gh auth token).Trim()
    if(-not $token){ Fail "GH_TOKEN" "Cannot read GitHub auth token." }

    $headers=@{
      Authorization="Bearer $token"
      Accept="application/vnd.github+json"
      "X-GitHub-Api-Version"="2022-11-28"
    }

    $artifact=$null
    try{
      $api="https://api.github.com/repos/"+$cfg.Repo+"/actions/artifacts?name="+$cfg.Artifact+"&per_page=100"
      $listing=Invoke-RestWithRetry $api $headers
      $artifact=@(
        $listing.artifacts |
        Where-Object { -not $_.expired } |
        Sort-Object created_at |
        Select-Object -Last 1
      )[0]
    }catch{
      Write-Host ("Artifact lookup failed for "+$cfg.Name+"; checking local vault.") -ForegroundColor Yellow
    }

    if($artifact){
      Write-Host ("Downloading canonical signing identity for "+$cfg.Name+"...") -ForegroundColor Cyan
      Download-WithRetry ([string]$artifact.archive_download_url) $headers $zip
      $source="github-actions-artifact:"+$artifact.id
    }elseif(Test-Path $vaultFile){
      Write-Host ("Using existing DPAPI vault for "+$cfg.Name+".") -ForegroundColor Yellow
      $plain=Unprotect-Bytes ([IO.File]::ReadAllBytes($vaultFile)) $cfg.Name
      [IO.File]::WriteAllBytes($zip,$plain)
      $source="windows-dpapi-vault"
    }else{
      Fail "SIGNING_SOURCE_MISSING" ("No active canonical artifact and no DPAPI vault exist for "+$cfg.Name+".")
    }

    $extract=Join-Path $temp "extract"
    Expand-Archive -Path $zip -DestinationPath $extract -Force

    $jks=Get-ChildItem $extract -Recurse -File -Filter $cfg.Keystore | Select-Object -First 1
    $cred=Get-ChildItem $extract -Recurse -File -Filter "SIGNING-CREDENTIALS.txt" | Select-Object -First 1
    if(-not $jks){ Fail "KEYSTORE_MISSING" ($cfg.Keystore+" missing from canonical archive.") }
    if(-not $cred){ Fail "CREDENTIALS_MISSING" "SIGNING-CREDENTIALS.txt missing from canonical archive." }

    $vars=Parse-Credentials $cred.FullName
    $storeKey=$cfg.Prefix+"_KEYSTORE_PASSWORD"
    $aliasKey=$cfg.Prefix+"_KEY_ALIAS"

    foreach($required in @($storeKey,$aliasKey)){
      if(-not $vars.ContainsKey($required) -or [string]::IsNullOrEmpty([string]$vars[$required])){
        Fail "CREDENTIAL_MISSING" ($required+" missing.")
      }
    }

    $projectCfg=$Registry.projects.($cfg.Name)
    if(-not $projectCfg -or -not $projectCfg.signing){
      Fail "SIGNING_REGISTRY_MISSING" ("Registry signing config missing for "+$cfg.Name)
    }

    $expectedCert=[string]$projectCfg.signing.certificate_sha256
    if($expectedCert -notmatch '^[0-9a-f]{64}$'){
      Fail "CERT_EXPECTED_INVALID" ("Invalid expected certificate SHA-256 for "+$cfg.Name)
    }

    $env:MBH_MIGRATE_STOREPASS=[string]$vars[$storeKey]
    try{
      $keytoolOutput=& $keytool -list -v -keystore $jks.FullName -storepass:env MBH_MIGRATE_STOREPASS -alias ([string]$vars[$aliasKey]) 2>&1 | Out-String
      if($LASTEXITCODE -ne 0){ Fail "KEYSTORE_VALIDATE" ("keytool failed for "+$cfg.Name) }
    }finally{
      Remove-Item Env:MBH_MIGRATE_STOREPASS -ErrorAction SilentlyContinue
    }

    $match=[regex]::Match($keytoolOutput,'SHA256:\s*([0-9A-Fa-f:]+)')
    if(-not $match.Success){ Fail "CERT_PARSE" ("Cannot parse certificate SHA-256 for "+$cfg.Name) }
    $actualCert=$match.Groups[1].Value.ToLowerInvariant().Replace(":","")
    if($actualCert -ne $expectedCert){
      Fail "CERT_MISMATCH" ("Canonical artifact certificate mismatch for "+$cfg.Name)
    }

    $archiveBytes=[IO.File]::ReadAllBytes($zip)
    $protected=Protect-Bytes $archiveBytes $cfg.Name

    $tmpVault=$vaultFile+".new"
    [IO.File]::WriteAllBytes($tmpVault,$protected)

    # Verify round-trip before replacing the active vault.
    $roundTrip=Unprotect-Bytes ([IO.File]::ReadAllBytes($tmpVault)) $cfg.Name
    $originalHash=[BitConverter]::ToString(
      [Security.Cryptography.SHA256]::Create().ComputeHash($archiveBytes)
    ).Replace("-","").ToLowerInvariant()
    $roundHash=[BitConverter]::ToString(
      [Security.Cryptography.SHA256]::Create().ComputeHash($roundTrip)
    ).Replace("-","").ToLowerInvariant()
    if($roundHash -ne $originalHash){
      Remove-Item $tmpVault -Force -ErrorAction SilentlyContinue
      Fail "DPAPI_ROUNDTRIP" ("DPAPI verification failed for "+$cfg.Name)
    }

    Move-Item $tmpVault $vaultFile -Force

    $jksSha=(Get-FileHash -Algorithm SHA256 $jks.FullName).Hash.ToLowerInvariant()
    $meta=[pscustomobject]@{
      schema="mbh-signing-vault-v1"
      profile=$cfg.Name
      repository=$cfg.Repo
      source=$source
      archive_sha256=$originalHash
      keystore_sha256=$jksSha
      certificate_sha256=$actualCert
      protected_by="Windows DPAPI CurrentUser"
      migrated_at=(Get-Date).ToString("o")
      disaster_recovery_backup="REQUIRED_BEFORE_OPERATIONAL_CERTIFICATION"
    }
    $meta | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 $metaFile

    Write-Host ("LOCAL_SIGNING_VAULT_PASS: "+$cfg.Name) -ForegroundColor Green
  }finally{
    if(Test-Path $temp){ Remove-Item $temp -Recurse -Force -ErrorAction SilentlyContinue }
  }
}

$warning=Join-Path $Vault "DISASTER_RECOVERY_REQUIRED.txt"
@(
  "The active Android signing identities are protected locally with Windows DPAPI.",
  "Before BuildHub can be certified OPERATIONAL, create and RESTORE-TEST an encrypted disaster-recovery copy on a separate trusted medium/service.",
  "Do not delete the old canonical GitHub Actions signing artifacts while they are still available.",
  "Never generate a replacement signing key just because the original cannot be found."
) | Set-Content -Encoding UTF8 $warning

Write-Host "SIGNING_MIGRATION_COMPLETE" -ForegroundColor Green
