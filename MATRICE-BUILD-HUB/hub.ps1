param([string]$Project,[string]$Branch,[switch]$KeepCodespace,[switch]$NoPublish)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Registry = Get-Content (Join-Path $Root "projects.json") -Raw | ConvertFrom-Json
if (-not $Project) {
  Write-Host "MATRICE BUILD HUB" -ForegroundColor Cyan
  Write-Host "1. PhoneMouse"
  Write-Host "2. P2PCR95"
  Write-Host "3. ChatGPT-PC"
  $c = Read-Host "Projet"
  if ($c -eq "1") { $Project="PhoneMouse" } elseif ($c -eq "2") { $Project="P2PCR95" } elseif ($c -eq "3") { $Project="ChatGPT-PC" } else { throw "Choix invalide" }
}
$Cfg = $Registry.projects.$Project
if (-not $Cfg) { throw "Projet inconnu: $Project" }
$Repo = [string]$Cfg.repo
$RepoName = ($Repo -split "/")[-1]
if (-not $Branch) { $Branch = [string]$Cfg.default_branch }
$Adapter = Join-Path $Root ([string]$Cfg.adapter)
if (-not (Test-Path $Adapter)) { throw "Adaptateur absent: $Adapter" }
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw "GitHub CLI absent. Execute bootstrap-pc.ps1 une seule fois." }
& gh auth status -h github.com *> $null
if ($LASTEXITCODE -ne 0) { throw "GitHub CLI non authentifie. Execute gh auth login -h github.com -p https -w" }
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Display = "mbh-" + $Project.ToLower().Replace("-","") + "-" + $Stamp
$OutBase = Join-Path $Root "output"
$Dest = Join-Path $OutBase ($Project + "-" + $Stamp)
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
Write-Host "Projet: $Project" -ForegroundColor Green
Write-Host "Depot: $Repo"
Write-Host "Branche: $Branch"
$Machines = (& gh api ("repos/" + $Repo + "/codespaces/machines") | ConvertFrom-Json).machines
$Machine = ($Machines | Sort-Object cpus | Select-Object -First 1).name
if (-not $Machine) { throw "Aucune machine Codespaces disponible." }
Write-Host "Machine: $Machine"
$Codespace = $null
try {
  & gh codespace create -R $Repo -b $Branch -d $Display -m $Machine --idle-timeout 10m --retention-period 1h --default-permissions | Out-Host
  if ($LASTEXITCODE -ne 0) { throw "Creation Codespace echouee." }
  for ($i=0; $i -lt 40 -and -not $Codespace; $i++) {
    Start-Sleep -Seconds 2
    $List = & gh codespace list -R $Repo --json name,displayName,state,createdAt | ConvertFrom-Json
    $Codespace = ($List | Where-Object { $_.displayName -eq $Display } | Sort-Object createdAt -Descending | Select-Object -First 1).name
  }
  if (-not $Codespace) { throw "Codespace introuvable apres creation." }
  Write-Host "Builder: $Codespace"
  $state = ""
  for ($i=0; $i -lt 100; $i++) {
    $View = & gh codespace view -c $Codespace --json state | ConvertFrom-Json
    $state = $View.state
    if ($state -eq "Available") { break }
    Start-Sleep -Seconds 3
  }
  if ($state -ne "Available") { throw "Codespace non disponible: $state" }
  & gh codespace cp -c $Codespace $Adapter "remote:/tmp/matrix-build-adapter.sh" | Out-Host
  if ($LASTEXITCODE -ne 0) { throw "Copie adaptateur echouee." }
  $Remote = "cd /workspaces/$RepoName && git fetch origin $Branch && git checkout $Branch && git reset --hard origin/$Branch && rm -rf .matrix-build-output && chmod +x /tmp/matrix-build-adapter.sh && MATRIX_REPO=$Repo MATRIX_BRANCH=$Branch bash /tmp/matrix-build-adapter.sh"
  Write-Host "Compilation cloud en cours..." -ForegroundColor Cyan
  & gh codespace ssh -c $Codespace $Remote
  if ($LASTEXITCODE -ne 0) { throw "Build distant echoue." }
  & gh codespace cp -r -c $Codespace ("remote:/workspaces/" + $RepoName + "/.matrix-build-output") $Dest | Out-Host
  if ($LASTEXITCODE -ne 0) { throw "Recuperation des artefacts echouee." }
  $ResultDir = Join-Path $Dest ".matrix-build-output"
  $ResultFile = Join-Path $ResultDir "result.json"
  if (-not (Test-Path $ResultFile)) { throw "Build sans result.json." }
  $Result = Get-Content $ResultFile -Raw | ConvertFrom-Json
  Write-Host "BUILD REUSSI" -ForegroundColor Green
  Write-Host ("Fichiers: " + $ResultDir)
  if (-not $NoPublish -and $Result.publish -eq $true) {
    $Tag = [string]$Result.tag
    $Title = [string]$Result.title
    $Assets = @(Get-ChildItem $ResultDir -File | Where-Object { $_.Name -ne "result.json" } | ForEach-Object { $_.FullName })
    if ($Assets.Count -eq 0) { throw "Aucun artefact a publier." }
    & gh release view $Tag -R $Repo *> $null
    if ($LASTEXITCODE -eq 0) {
      & gh release upload $Tag @Assets -R $Repo --clobber | Out-Host
    } else {
      & gh release create $Tag @Assets -R $Repo --prerelease --title $Title --notes "Produit par MATRICE BUILD HUB sans GitHub Actions." | Out-Host
    }
    if ($LASTEXITCODE -ne 0) { throw "Publication GitHub Release echouee." }
    $Release = & gh release view $Tag -R $Repo --json url | ConvertFrom-Json
    $Url = $Release.url
    Write-Host ("LIEN: " + $Url) -ForegroundColor Cyan
    [IO.File]::WriteAllLines((Join-Path $Root "LAST_BUILD.txt"), @($Project,$Branch,$Url,$ResultDir))
  }
} finally {
  if ($Codespace) {
    if ($KeepCodespace) { & gh codespace stop -c $Codespace | Out-Host } else { & gh codespace delete -c $Codespace --force | Out-Host }
  }
}
