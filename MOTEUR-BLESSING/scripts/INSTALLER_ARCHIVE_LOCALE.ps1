# Installe V1.1.2 uniquement depuis une archive locale dont l'empreinte correspond au recu.
param([Parameter(Mandatory=$true)][string]$Archive)
$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$Expected="5ef731d6ee4b5edb8a741c59a565d4f7363be84eb9225e814345cb0a04fe89e0"
if (-not (Test-Path -LiteralPath $Archive -PathType Leaf)) { throw "Archive absente" }
$Actual=(Get-FileHash -LiteralPath $Archive -Algorithm SHA256).Hash.ToLowerInvariant()
if ($Actual -ne $Expected) { throw "SHA256 incompatible ; refus" }
$Versions=Join-Path $Root "versions"
$Target=Join-Path $Versions "V1.1.2"
if (Test-Path $Target) { throw "Version deja presente : $Target" }
New-Item -ItemType Directory -Force -Path $Versions | Out-Null
$Temp=Join-Path $Versions ("staging_"+[Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $Temp | Out-Null
try {
 Expand-Archive -LiteralPath $Archive -DestinationPath $Temp -ErrorAction Stop
 if (-not (Test-Path (Join-Path $Temp "00_LIRE_EN_PREMIER.md"))) { throw "Structure ZIP incorrecte" }
 Move-Item -LiteralPath $Temp -Destination $Target
 Write-Output "INSTALLED: $Target"
} catch {
 if (Test-Path $Temp) { Remove-Item -Recurse -Force -LiteralPath $Temp }
 throw
}
