$ErrorActionPreference="Stop"
Write-Host "MATRICE BUILD HUB V0.2 - installation unique" -ForegroundColor Cyan

function Fail($Code,$Message){throw "[$Code] $Message"}
function Refresh-Path{
  $machine=[Environment]::GetEnvironmentVariable("Path","Machine")
  $user=[Environment]::GetEnvironmentVariable("Path","User")
  $env:Path=$machine+";"+$user
}

if(-not(Get-Command winget -ErrorAction SilentlyContinue)){
  Fail "WINGET_MISSING" "Windows Package Manager (winget) is required for automatic installation."
}

if(-not(Get-Command git -ErrorAction SilentlyContinue)){
  Write-Host "Installing Git..." -ForegroundColor Cyan
  & winget install --id Git.Git --exact --source winget --accept-package-agreements --accept-source-agreements
  if($LASTEXITCODE -ne 0){Fail "GIT_INSTALL" "Git installation failed."}
  Refresh-Path
}

if(-not(Get-Command gh -ErrorAction SilentlyContinue)){
  Write-Host "Installing GitHub CLI..." -ForegroundColor Cyan
  & winget install --id GitHub.cli --exact --source winget --accept-package-agreements --accept-source-agreements
  if($LASTEXITCODE -ne 0){Fail "GH_INSTALL" "GitHub CLI installation failed."}
  Refresh-Path
}

if(-not(Get-Command git -ErrorAction SilentlyContinue)){Fail "GIT_MISSING" "Git is still unavailable after installation."}
if(-not(Get-Command gh -ErrorAction SilentlyContinue)){Fail "GH_MISSING" "GitHub CLI is still unavailable after installation."}

& gh auth status -h github.com *> $null
if($LASTEXITCODE -ne 0){
  Write-Host "GitHub sign-in will open in your browser." -ForegroundColor Yellow
  & gh auth login -h github.com -p https -w -s codespace
  if($LASTEXITCODE -ne 0){Fail "GH_AUTH" "GitHub authentication failed."}
}else{
  Write-Host "Refreshing GitHub permission for Codespaces..." -ForegroundColor Cyan
  & gh auth refresh -h github.com -s codespace
  if($LASTEXITCODE -ne 0){Fail "GH_SCOPE" "Could not authorize the Codespaces scope."}
}

& gh auth setup-git -h github.com
if($LASTEXITCODE -ne 0){Fail "GIT_AUTH" "Could not configure Git to use GitHub authentication."}

$Base=Join-Path $env:LOCALAPPDATA "MatriceBuildHub"
$Source=Join-Path $Base "PROJECT-DRAFTS"
New-Item -ItemType Directory -Force -Path $Base|Out-Null

if(Test-Path (Join-Path $Source ".git")){
  Write-Host "Updating canonical BuildHub source..." -ForegroundColor Cyan
  & git -C $Source fetch origin main
  & git -C $Source reset --hard origin/main
}else{
  if(Test-Path $Source){Remove-Item $Source -Recurse -Force}
  Write-Host "Installing canonical BuildHub source..." -ForegroundColor Cyan
  & gh repo clone Terminator364/PROJECT-DRAFTS $Source
  if($LASTEXITCODE -ne 0){Fail "CLONE_FAILED" "Could not clone PROJECT-DRAFTS."}
}

$Hub=Join-Path $Source "MATRICE-BUILD-HUB"
if(-not(Test-Path (Join-Path $Hub "hub.ps1"))){Fail "HUB_MISSING" "MATRICE-BUILD-HUB was not found in the canonical clone."}

Write-Host "Checking Codespaces access..." -ForegroundColor Cyan
& gh codespace list --limit 1 *> $null
if($LASTEXITCODE -ne 0){Fail "CODESPACES_ACCESS" "GitHub Codespaces is not available to this authenticated account."}

Write-Host "Preparing lightweight local Android signing tools..." -ForegroundColor Cyan
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Hub "setup-local-signing-tools.ps1")
if($LASTEXITCODE -ne 0){Fail "LOCAL_SIGNING_TOOLS" "Could not prepare local Android signing tools."}

Write-Host "Securing Android signing identities..." -ForegroundColor Cyan
$signingOk=$true
try{
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Hub "migrate-signing.ps1") -Profile All
  if($LASTEXITCODE -ne 0){$signingOk=$false}
}catch{
  $signingOk=$false
  Write-Host ("Signing migration warning: "+$_.Exception.Message) -ForegroundColor Yellow
}

Write-Host "Preserving durable non-secret build inputs..." -ForegroundColor Cyan\r\ntry{\r\n  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Hub "migrate-durable-inputs.ps1")\r\n  if($LASTEXITCODE -ne 0){ Write-Host "Durable input migration needs attention before P2PCR95 BETA03." -ForegroundColor Yellow }\r\n}catch{\r\n  Write-Host ("Durable input migration warning: "+$_.Exception.Message) -ForegroundColor Yellow\r\n}\r\n\r\nWrite-Host "Running local doctor..." -ForegroundColor Cyan
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Hub "hub.ps1") -Mode Doctor
if($LASTEXITCODE -ne 0){Fail "DOCTOR_FAILED" "BuildHub local doctor failed."}

$Desktop=[Environment]::GetFolderPath("Desktop")
$ShortcutPath=Join-Path $Desktop "MATRICE BUILD HUB.lnk"
$Target=Join-Path $Hub "hub.cmd"
$ws=New-Object -ComObject WScript.Shell
$shortcut=$ws.CreateShortcut($ShortcutPath)
$shortcut.TargetPath=$Target
$shortcut.WorkingDirectory=$Hub
$shortcut.Description="MATRICE BUILD HUB - production centralisee"
$shortcut.Save()

Write-Host ""
Write-Host "BUILD_HUB_BOOTSTRAP_PASS" -ForegroundColor Green
Write-Host ("Shortcut: "+$ShortcutPath)
if($signingOk){
  Write-Host "Android signing migration: PASS" -ForegroundColor Green
}else{
  Write-Host "Android signing migration: NEEDS ATTENTION before a signed APK build." -ForegroundColor Yellow
}
Write-Host "Next safe step: launch MATRICE BUILD HUB and choose 4 for the cloud diagnostic before the first APK build."
Read-Host "Press Enter to close" | Out-Null
