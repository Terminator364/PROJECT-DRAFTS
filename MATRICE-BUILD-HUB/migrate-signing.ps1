param([ValidateSet("All","PhoneMouse","P2PCR95")][string]$Profile="All")

$ErrorActionPreference="Stop"
$DataRoot=Join-Path $env:LOCALAPPDATA "MatriceBuildHub"
$Vault=Join-Path $DataRoot "vault"
New-Item -ItemType Directory -Force -Path $Vault|Out-Null

function Fail($Code,$Message){throw "[$Code] $Message"}
function Protect-Bytes([byte[]]$Bytes,[string]$ProfileName){
  Add-Type -AssemblyName System.Security
  $entropy=[Text.Encoding]::UTF8.GetBytes("MatriceBuildHub|"+$ProfileName+"|v0.2")
  return [Security.Cryptography.ProtectedData]::Protect($Bytes,$entropy,[Security.Cryptography.DataProtectionScope]::CurrentUser)
}
function Unprotect-Bytes([byte[]]$Bytes,[string]$ProfileName){
  Add-Type -AssemblyName System.Security
  $entropy=[Text.Encoding]::UTF8.GetBytes("MatriceBuildHub|"+$ProfileName+"|v0.2")
  return [Security.Cryptography.ProtectedData]::Unprotect($Bytes,$entropy,[Security.Cryptography.DataProtectionScope]::CurrentUser)
}

if(-not(Get-Command gh -ErrorAction SilentlyContinue)){Fail "GH_MISSING" "GitHub CLI is missing."}
& gh auth status -h github.com *> $null
if($LASTEXITCODE -ne 0){Fail "GH_AUTH" "GitHub CLI is not authenticated."}

$profiles=@(
  [pscustomobject]@{Name="PhoneMouse";Repo="Terminator364/PhoneMouse";Artifact="PhoneMouse-SIGNING-IDENTITY-CANONICAL";Keystore="PhoneMouse-signing.jks"},
  [pscustomobject]@{Name="P2PCR95";Repo="Terminator364/P2PCR95";Artifact="P2PCR95-SIGNING-IDENTITY-CANONICAL";Keystore="P2PCR95-signing.jks"}
)

foreach($cfg in $profiles){
  if($Profile -ne "All" -and $Profile -ne $cfg.Name){continue}
  $vaultFile=Join-Path $Vault ($cfg.Name+".signing.dpapi")
  $metaFile=Join-Path $Vault ($cfg.Name+".signing.json")
  $temp=Join-Path $env:TEMP ("mbh-signing-"+[guid]::NewGuid().ToString("N"))
  New-Item -ItemType Directory -Force -Path $temp|Out-Null
  try{
    $zip=Join-Path $temp "signing.zip"
    $source=""

    $token=(& gh auth token).Trim()
    if(-not $token){Fail "GH_TOKEN" "Cannot read GitHub auth token."}
    $headers=@{Authorization="Bearer $token";Accept="application/vnd.github+json";"X-GitHub-Api-Version"="2022-11-28"}

    try{
      $api="https://api.github.com/repos/"+$cfg.Repo+"/actions/artifacts?name="+$cfg.Artifact+"&per_page=100"
      $listing=Invoke-RestMethod -UseBasicParsing -Headers $headers -Uri $api -Method Get
      $artifact=@($listing.artifacts|Where-Object{-not $_.expired}|Sort-Object created_at|Select-Object -Last 1)[0]
    }catch{$artifact=$null}

    if($artifact){
      Write-Host ("Downloading canonical signing identity for "+$cfg.Name+"...") -ForegroundColor Cyan
      Invoke-WebRequest -UseBasicParsing -Headers $headers -Uri $artifact.archive_download_url -OutFile $zip
      $protected=Protect-Bytes ([IO.File]::ReadAllBytes($zip)) $cfg.Name
      [IO.File]::WriteAllBytes($vaultFile,$protected)
      $source="github-actions-artifact:"+$artifact.id
    }elseif(Test-Path $vaultFile){
      Write-Host ("Canonical Actions artifact unavailable; validating local encrypted vault for "+$cfg.Name+".") -ForegroundColor Yellow
      $plain=Unprotect-Bytes ([IO.File]::ReadAllBytes($vaultFile)) $cfg.Name
      [IO.File]::WriteAllBytes($zip,$plain)
      $source="windows-dpapi-vault"
    }else{
      Fail "SIGNING_SOURCE_MISSING" ("No canonical signing artifact and no DPAPI vault exist for "+$cfg.Name+".")
    }

    $extract=Join-Path $temp "extract"
    Expand-Archive -Path $zip -DestinationPath $extract -Force
    $jks=Get-ChildItem $extract -Recurse -File -Filter $cfg.Keystore|Select-Object -First 1
    $cred=Get-ChildItem $extract -Recurse -File -Filter "SIGNING-CREDENTIALS.txt"|Select-Object -First 1
    if(-not $jks){Fail "KEYSTORE_MISSING" ($cfg.Keystore+" missing from canonical archive.")}
    if(-not $cred){Fail "CREDENTIALS_MISSING" "SIGNING-CREDENTIALS.txt missing from canonical archive."}

    $jksSha=(Get-FileHash -Algorithm SHA256 $jks.FullName).Hash.ToLowerInvariant()
    $archiveSha=(Get-FileHash -Algorithm SHA256 $zip).Hash.ToLowerInvariant()
    $meta=[pscustomobject]@{
      schema="mbh-signing-vault-v1"
      profile=$cfg.Name
      repository=$cfg.Repo
      source=$source
      archive_sha256=$archiveSha
      keystore_sha256=$jksSha
      protected_by="Windows DPAPI CurrentUser"
      migrated_at=(Get-Date).ToString("o")
      disaster_recovery_backup="REQUIRED_BEFORE_OPERATIONAL_CERTIFICATION"
    }
    $meta|ConvertTo-Json -Depth 4|Set-Content -Encoding UTF8 $metaFile
    Write-Host ("LOCAL_SIGNING_VAULT_PASS: "+$cfg.Name) -ForegroundColor Green
  }finally{
    if(Test-Path $temp){Remove-Item $temp -Recurse -Force -ErrorAction SilentlyContinue}
  }
}

$warning=Join-Path $Vault "DISASTER_RECOVERY_REQUIRED.txt"
@(
  "The active Android signing identities are protected locally with Windows DPAPI.",
  "Before BuildHub can be certified OPERATIONAL, create an encrypted disaster-recovery copy on a separate trusted medium/service.",
  "Do not delete the old canonical GitHub Actions signing artifacts while they are still available.",
  "Never generate a replacement signing key just because the original cannot be found."
)|Set-Content -Encoding UTF8 $warning
