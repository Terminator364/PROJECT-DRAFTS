$ErrorActionPreference = "Stop"
Write-Host "MATRICE BUILD HUB - installation unique" -ForegroundColor Cyan
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
  if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw "winget absent. Installe GitHub CLI depuis cli.github.com puis relance ce fichier." }
  Write-Host "Installation de GitHub CLI..."
  & winget install --id GitHub.cli --exact --source winget --accept-package-agreements --accept-source-agreements
  if ($LASTEXITCODE -ne 0) { throw "Installation GitHub CLI echouee." }
  $env:Path = $env:Path + ";C:\Program Files\GitHub CLI"
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw "GitHub CLI installe mais pas encore visible. Ferme et rouvre PowerShell puis relance bootstrap-pc.ps1." }
& gh auth status -h github.com *> $null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Connexion GitHub dans le navigateur..."
  & gh auth login -h github.com -p https -w
  if ($LASTEXITCODE -ne 0) { throw "Authentification GitHub echouee." }
}
& gh codespace list --limit 1 *> $null
if ($LASTEXITCODE -ne 0) { throw "Acces GitHub Codespaces non disponible pour ce compte ou cette installation." }
Write-Host ""
Write-Host "BUILD HUB PRET." -ForegroundColor Green
Write-Host "A partir de maintenant, utilise hub.cmd pour lancer une production."
Read-Host "Appuie sur Entree pour fermer" | Out-Null
