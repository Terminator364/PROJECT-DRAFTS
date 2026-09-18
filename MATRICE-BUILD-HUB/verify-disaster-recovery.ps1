$ErrorActionPreference="Stop"
Add-Type -AssemblyName System.Windows.Forms

$Base=Join-Path $env:LOCALAPPDATA "MatriceBuildHub"
$Vault=Join-Path $Base "vault"
New-Item -ItemType Directory -Force -Path $Vault|Out-Null

if(-not(Get-Command age -ErrorAction SilentlyContinue)){throw "[AGE_MISSING] Install age or run export-disaster-recovery.ps1 first."}

$dialog=New-Object System.Windows.Forms.OpenFileDialog
$dialog.Title="Choisis la sauvegarde MatriceBuildHub-Recovery-*.zip.age"
$dialog.Filter="age encrypted backup (*.age)|*.age|All files (*.*)|*.*"
if($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK){throw "[VERIFY_CANCELLED] No backup selected."}
$Encrypted=$dialog.FileName

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
  foreach($p in @($manifest.profiles)){
    $file=Join-Path $extract ([string]$p.file)
    if(-not(Test-Path $file)){throw "[RECOVERY_FILE_MISSING] $($p.file)"}
    $sha=(Get-FileHash -Algorithm SHA256 $file).Hash.ToLowerInvariant()
    if($sha -ne [string]$p.sha256){throw "[RECOVERY_HASH_MISMATCH] $($p.name)"}
    $seen[[string]$p.name]=$true
  }
  foreach($required in @("PhoneMouse","P2PCR95")){
    if(-not $seen.ContainsKey($required)){throw "[RECOVERY_PROFILE_MISSING] $required"}
  }

  $encHash=(Get-FileHash -Algorithm SHA256 $Encrypted).Hash.ToLowerInvariant()
  $marker=Join-Path $Vault "DISASTER_RECOVERY_RESTORE_TEST_PASS.json"
  [pscustomobject]@{
    schema="mbh-disaster-recovery-restore-test-v1"
    verified_at=(Get-Date).ToString("o")
    encrypted_backup=$Encrypted
    encrypted_sha256=$encHash
    profiles=@("PhoneMouse","P2PCR95")
    result="PASS"
  }|ConvertTo-Json -Depth 5|Set-Content -Encoding UTF8 $marker

  Write-Host "DISASTER_RECOVERY_RESTORE_TEST_PASS" -ForegroundColor Green
}finally{
  if(Test-Path $temp){Remove-Item $temp -Recurse -Force -ErrorAction SilentlyContinue}
}
