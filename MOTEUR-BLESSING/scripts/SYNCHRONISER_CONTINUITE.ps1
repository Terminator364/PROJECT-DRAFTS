# Moteur Blessing : synchronisation des documents, sans moteur ni API payante.
# Cache-busting obligatoire pour eviter les anciens fichiers juste apres un commit.
$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$RawRoot="https://raw.githubusercontent.com/Terminator364/PROJECT-DRAFTS/main/MOTEUR-BLESSING"
$Files=@("README.md","CONTINUITE.md","ETAT_V112.md","FEUILLE_ROUTE.md","LIVRAISONS.md","JOURNAL.md","MANIFEST.json")
$Results=@()
foreach ($name in $Files) {
 $tmp=Join-Path $Root ($name+".incoming")
 $dst=Join-Path $Root $name
 try {
   $nonce=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
   $uri=$RawRoot+"/"+$name+"?checkpoint="+$nonce
   Invoke-WebRequest -UseBasicParsing -TimeoutSec 30 -Headers @{"Cache-Control"="no-cache"} -Uri $uri -OutFile $tmp
   if ((Get-Item $tmp).Length -lt 30) { throw "Fichier anormalement court" }
   if ($name -eq "MANIFEST.json") {
      $j=Get-Content -Raw -Path $tmp | ConvertFrom-Json
      if (-not $j.checkpoints.documentation_synced_to_windows) { throw "Manifeste ancien : checkpoint absent" }
   }
   if ($name -eq "JOURNAL.md" -and -not ((Get-Content -Raw $tmp).Contains("FIN / espace officiel"))) { throw "Journal ancien" }
   Move-Item -Force -Path $tmp -Destination $dst
   $Results += [PSCustomObject]@{name=$name;status="OK";bytes=(Get-Item $dst).Length}
 } catch {
   if (Test-Path $tmp) { Remove-Item -Force $tmp }
   $Results += [PSCustomObject]@{name=$name;status="ERROR";message=$_.Exception.Message}
 }
}
$Results | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 -Path (Join-Path $Root "SYNCHRONISATION_ETAT.json")
$Results | Format-Table -AutoSize
if (@($Results | Where-Object status -ne "OK").Count -gt 0) { exit 2 }
exit 0
