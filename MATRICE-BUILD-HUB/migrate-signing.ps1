param(
  [ValidateSet("All","PhoneMouse","P2PCR95")][string]$Profile="All"
)

$ErrorActionPreference="Stop"
$DataRoot=Join-Path $env:LOCALAPPDATA "MatriceBuildHub"
$Vault=Join-Path $DataRoot "vault"
New-Item -ItemType Directory -Force -Path $Vault|Out-Null

function Fail($Code,$Message){throw "[$Code] $Message"}

function Set-CodespacesSecret([string]$Repo,[string]$Name,[string]$Value){
  $gh=(Get-Command gh -ErrorAction Stop).Source
  $psi=New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName=$gh
  $psi.Arguments="secret set $Name --app codespaces -R $Repo"
  $psi.UseShellExecute=$false
  $psi.RedirectStandardInput=$true
  $psi.RedirectStandardOutput=$true
  $psi.RedirectStandardError=$true
  $psi.CreateNoWindow=$true
  $p=New-Object System.Diagnostics.Process
  $p.StartInfo=$psi
  [void]$p.Start()
  $p.StandardInput.Write($Value)
  $p.StandardInput.Close()
  $stdout=$p.StandardOutput.ReadToEnd()
  $stderr=$p.StandardError.ReadToEnd()
  $p.WaitForExit()
  if($p.ExitCode -ne 0){
    Fail "SECRET_SET_FAILED" "$Repo / $Name : $stderr $stdout"
  }
}

function Parse-Credentials([string]$Path){
  $map=@{}
  foreach($line in Get-Content $Path){
    if($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)=(.*)$'){
      $name=$matches[1]
      $value=$matches[2].Trim()
      if(($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))){
        $value=$value.Substring(1,$value.Length-2)
      }
      $map[$name]=$value
    }
  }
  return $map
}

function Protect-Backup([byte[]]$Bytes,[string]$Path,[string]$ProfileName){
  Add-Type -AssemblyName System.Security
  $entropy=[Text.Encoding]::UTF8.GetBytes("MatriceBuildHub|$ProfileName|v0.2")
  $protected=[Security.Cryptography.ProtectedData]::Protect(
    $Bytes,$entropy,[Security.Cryptography.DataProtectionScope]::CurrentUser
  )
  [IO.File]::WriteAllBytes($Path,$protected)
}

function Unprotect-Backup([string]$Path,[string]$ProfileName){
  Add-Type -AssemblyName System.Security
  $entropy=[Text.Encoding]::UTF8.GetBytes("MatriceBuildHub|$ProfileName|v0.2")
  $protected=[IO.File]::ReadAllBytes($Path)
  return [Security.Cryptography.ProtectedData]::Unprotect(
    $protected,$entropy,[Security.Cryptography.DataProtectionScope]::CurrentUser
  )
}

function Migrate-One($Cfg){
  $Repo=$Cfg.Repo
  $Name=$Cfg.Name
  $ArtifactName=$Cfg.Artifact
  $KeystoreName=$Cfg.Keystore
  $KeystoreSecret=$Cfg.KeystoreSecret
  $VaultFile=Join-Path $Vault ($Name+".artifact.dpapi")
  $MetaFile=Join-Path $Vault ($Name+".metadata.json")
  $temp=Join-Path $env:TEMP ("mbh-signing-"+[guid]::NewGuid().ToString("N"))
  New-Item -ItemType Directory -Force -Path $temp|Out-Null

  try{
    $zip=Join-Path $temp "signing.zip"
    $source=""

    $token=(& gh auth token).Trim()
    if(-not $token){Fail "GH_TOKEN" "Cannot read GitHub authentication token."}
    $headers=@{
      Authorization="Bearer $token"
      Accept="application/vnd.github+json"
      "X-GitHub-Api-Version"="2022-11-28"
    }

    try{
      $api="https://api.github.com/repos/$Repo/actions/artifacts?name=$ArtifactName&per_page=100"
      $listing=Invoke-RestMethod -UseBasicParsing -Headers $headers -Uri $api -Method Get
      $artifact=@($listing.artifacts|Where-Object{-not $_.expired}|Sort-Object created_at|Select-Object -Last 1)[0]
    }catch{
      $artifact=$null
    }

    if($artifact){
      Write-Host "Downloading canonical signing artifact for $Name..." -ForegroundColor Cyan
      Invoke-WebRequest -UseBasicParsing -Headers $headers -Uri $artifact.archive_download_url -OutFile $zip
      if(-not(Test-Path $zip)){Fail "ARTIFACT_DOWNLOAD" "Signing artifact download failed for $Name."}
      Protect-Backup ([IO.File]::ReadAllBytes($zip)) $VaultFile $Name
      $source="github-artifact:"+$artifact.id
    }elseif(Test-Path $VaultFile){
      Write-Host "GitHub artifact unavailable; restoring encrypted local recovery copy for $Name." -ForegroundColor Yellow
      [IO.File]::WriteAllBytes($zip,(Unprotect-Backup $VaultFile $Name))
      $source="windows-dpapi-vault"
    }else{
      Fail "SIGNING_SOURCE_MISSING" "No active $ArtifactName artifact and no local encrypted recovery backup exist."
    }

    $extract=Join-Path $temp "extract"
    Expand-Archive -Path $zip -DestinationPath $extract -Force

    $jks=Get-ChildItem $extract -Recurse -File -Filter $KeystoreName|Select-Object -First 1
    if(-not $jks){Fail "KEYSTORE_MISSING" "$KeystoreName not found in signing archive."}

    $cred=Get-ChildItem $extract -Recurse -File -Filter "SIGNING-CREDENTIALS.txt"|Select-Object -First 1
    if(-not $cred){Fail "CREDENTIALS_MISSING" "SIGNING-CREDENTIALS.txt not found."}
    $vars=Parse-Credentials $cred.FullName

    foreach($required in $Cfg.Required){
      if(-not $vars.ContainsKey($required) -or [string]::IsNullOrEmpty([string]$vars[$required])){
        Fail "CREDENTIAL_MISSING" "$required is missing for $Name."
      }
    }

    $b64=[Convert]::ToBase64String([IO.File]::ReadAllBytes($jks.FullName))
    if([Text.Encoding]::UTF8.GetByteCount($b64) -gt 48000){
      Fail "KEYSTORE_TOO_LARGE" "Base64 keystore exceeds GitHub Codespaces secret size limit."
    }

    Write-Host "Installing repository-scoped Codespaces secrets for $Name..." -ForegroundColor Cyan
    Set-CodespacesSecret $Repo $KeystoreSecret $b64
    foreach($required in $Cfg.Required){
      Set-CodespacesSecret $Repo $required ([string]$vars[$required])
    }

    $listed=& gh secret list --app codespaces -R $Repo --json name|ConvertFrom-Json
    $names=@($listed|ForEach-Object{$_.name})
    foreach($requiredName in @($KeystoreSecret)+@($Cfg.Required)){
      if($names -notcontains $requiredName){
        Fail "SECRET_VERIFY_FAILED" "$requiredName is not listed after migration."
      }
    }

    $sha=(Get-FileHash -Algorithm SHA256 $jks.FullName).Hash.ToLowerInvariant()
    $meta=[pscustomobject]@{
      profile=$Name
      repository=$Repo
      source=$source
      keystore_file=$KeystoreName
      keystore_sha256=$sha
      migrated_at=(Get-Date).ToString("o")
      secret_names=@($KeystoreSecret)+@($Cfg.Required)
    }
    $meta|ConvertTo-Json -Depth 5|Set-Content -Encoding UTF8 $MetaFile
    Write-Host "SIGNING_MIGRATION_PASS: $Name" -ForegroundColor Green
  }
  finally{
    if(Test-Path $temp){Remove-Item $temp -Recurse -Force -ErrorAction SilentlyContinue}
  }
}

if(-not(Get-Command gh -ErrorAction SilentlyContinue)){Fail "GH_MISSING" "GitHub CLI is missing."}
& gh auth status -h github.com *> $null
if($LASTEXITCODE -ne 0){Fail "GH_AUTH" "GitHub CLI is not authenticated."}

$profiles=@(
  [pscustomobject]@{
    Name="PhoneMouse"
    Repo="Terminator364/PhoneMouse"
    Artifact="PhoneMouse-SIGNING-IDENTITY-CANONICAL"
    Keystore="PhoneMouse-signing.jks"
    KeystoreSecret="PHONEMOUSE_KEYSTORE_B64"
    Required=@("PHONEMOUSE_KEYSTORE_PASSWORD","PHONEMOUSE_KEY_ALIAS","PHONEMOUSE_KEY_PASSWORD")
  },
  [pscustomobject]@{
    Name="P2PCR95"
    Repo="Terminator364/P2PCR95"
    Artifact="P2PCR95-SIGNING-IDENTITY-CANONICAL"
    Keystore="P2PCR95-signing.jks"
    KeystoreSecret="P2PCR95_KEYSTORE_B64"
    Required=@("P2PCR95_KEYSTORE_PASSWORD","P2PCR95_KEY_ALIAS","P2PCR95_KEY_PASSWORD")
  }
)

foreach($p in $profiles){
  if($Profile -eq "All" -or $Profile -eq $p.Name){Migrate-One $p}
}
