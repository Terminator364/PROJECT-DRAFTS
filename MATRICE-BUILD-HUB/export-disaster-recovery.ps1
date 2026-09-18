$ErrorActionPreference="Stop"
Add-Type -AssemblyName System.Windows.Forms

$Base=Join-Path $env:LOCALAPPDATA "MatriceBuildHub"
$Vault=Join-Path $Base "vault"
if(-not(Test-Path $Vault)){throw "[VAULT_MISSING] Run bootstrap/signing migration first."}

function Refresh-Path{
  $machine=[Environment]::GetEnvironmentVariable("Path","Machine")
  $user=[Environment]::GetEnvironmentVariable("Path","User")
  $env:Path=$machine+";"+$user
}
function Unprotect-Bytes([byte[]]$Bytes,[string]$ProfileName){
  Add-Type -AssemblyName System.Security
  $entropy=[Text.Encoding]::UTF8.GetBytes("MatriceBuildHub|"+$ProfileName+"|v0.2")
  return [Security.Cryptography.ProtectedData]::Unprotect($Bytes,$entropy,[Security.Cryptography.DataProtectionScope]::CurrentUser)
}

if(-not(Get-Command age -ErrorAction SilentlyContinue)){
  if(-not(Get-Command winget -ErrorAction SilentlyContinue)){throw "[AGE_INSTALL] winget is unavailable."}
  Write-Host "Installing age encryption..." -ForegroundColor Cyan
  & winget install --id FiloSottile.age --exact --source winget --accept-package-agreements --accept-source-agreements
  if($LASTEXITCODE -ne 0){throw "[AGE_INSTALL] age installation failed."}
  Refresh-Path
}
if(-not(Get-Command age -ErrorAction SilentlyContinue)){throw "[AGE_MISSING] age is unavailable after installation."}

$dialog=New-Object System.Windows.Forms.FolderBrowserDialog
$dialog.Description="Choisis un dossier EXTERNE ou synchronise cloud pour la sauvegarde catastrophe BuildHub."
$dialog.ShowNewFolderButton=$true
if($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK){throw "[BACKUP_CANCELLED] No destination selected."}
$Destination=$dialog.SelectedPath

Write-Host ""
Write-Host "IMPORTANT: cette sauvegarde doit survivre a la perte de ce PC." -ForegroundColor Yellow
Write-Host ("Destination: "+$Destination)
$confirm=Read-Host "Tape OUI si ce dossier est externe ou synchronise hors de ce PC"
if($confirm -ne "OUI"){throw "[BACKUP_LOCATION_UNCONFIRMED] Disaster-recovery destination was not confirmed."}

$profiles=@("PhoneMouse","P2PCR95")
$temp=Join-Path $env:TEMP ("mbh-recovery-"+[guid]::NewGuid().ToString("N"))
$plainBundle=$null
New-Item -ItemType Directory -Force -Path $temp|Out-Null
try{
  $manifest=@{schema="mbh-disaster-recovery-v1";created_at=(Get-Date).ToString("o");profiles=@()}
  foreach($profile in $profiles){
    $vaultFile=Join-Path $Vault ($profile+".signing.dpapi")
    $metaFile=Join-Path $Vault ($profile+".signing.json")
    if(-not(Test-Path $vaultFile)){throw "[VAULT_PROFILE_MISSING] $profile"}
    $plain=Unprotect-Bytes ([IO.File]::ReadAllBytes($vaultFile)) $profile
    $out=Join-Path $temp ($profile+".canonical-signing.zip")
    [IO.File]::WriteAllBytes($out,$plain)
    $sha=(Get-FileHash -Algorithm SHA256 $out).Hash.ToLowerInvariant()
    $manifest.profiles+=@{name=$profile;file=(Split-Path $out -Leaf);sha256=$sha}
    if(Test-Path $metaFile){Copy-Item $metaFile (Join-Path $temp ($profile+".metadata.json")) -Force}
  }

  $manifestPath=Join-Path $temp "RECOVERY_MANIFEST.json"
  $manifest|ConvertTo-Json -Depth 6|Set-Content -Encoding UTF8 $manifestPath
  $instructions=Join-Path $temp "RECOVERY_INSTRUCTIONS.txt"
  @(
    "MATRICE BUILD HUB disaster-recovery bundle.",
    "Keep this encrypted .age file separate from the PC.",
    "Without the passphrase it cannot be recovered.",
    "Never publish the decrypted signing archives.",
    "These keys are required for Android updates to existing installed apps."
  )|Set-Content -Encoding UTF8 $instructions

  $plainBundle=Join-Path $env:TEMP ("MatriceBuildHub-Recovery-"+(Get-Date -Format "yyyyMMdd-HHmmss")+".zip")
  Compress-Archive -Path (Join-Path $temp "*") -DestinationPath $plainBundle -Force
  $encrypted=Join-Path $Destination ("MatriceBuildHub-Recovery-"+(Get-Date -Format "yyyyMMdd-HHmmss")+".zip.age")

  Write-Host ""
  Write-Host "age va demander une phrase secrete." -ForegroundColor Cyan
  Write-Host "Tu peux laisser vide pour que age en genere une forte; NOTE-LA et garde-la separement." -ForegroundColor Yellow
  & age -p -o $encrypted $plainBundle
  if($LASTEXITCODE -ne 0 -or -not(Test-Path $encrypted)){throw "[AGE_ENCRYPT] Recovery encryption failed."}

  $encHash=(Get-FileHash -Algorithm SHA256 $encrypted).Hash.ToLowerInvariant()
  Set-Content -Encoding ASCII -Path ($encrypted+".sha256") -Value ($encHash+"  "+(Split-Path $encrypted -Leaf))
  Remove-Item $plainBundle -Force -ErrorAction SilentlyContinue

  $marker=Join-Path $Vault "DISASTER_RECOVERY_EXPORTED.json"
  [pscustomobject]@{schema="mbh-disaster-recovery-export-v1";exported_at=(Get-Date).ToString("o");encrypted_sha256=$encHash;destination=$encrypted;verification="ENCRYPTED_FILE_CREATED_HASHED"}|ConvertTo-Json|Set-Content -Encoding UTF8 $marker
  Write-Host ""
  Write-Host "DISASTER_RECOVERY_EXPORT_PASS" -ForegroundColor Green
  Write-Host ("Backup: "+$encrypted)
  Write-Host ("SHA256: "+$encHash)
  Write-Host "Le gate de restauration complete restera a tester lors d un controle separe." -ForegroundColor Yellow
}finally{
  if($plainBundle -and (Test-Path $plainBundle)){Remove-Item $plainBundle -Force -ErrorAction SilentlyContinue}
  if(Test-Path $temp){Remove-Item $temp -Recurse -Force -ErrorAction SilentlyContinue}
}
