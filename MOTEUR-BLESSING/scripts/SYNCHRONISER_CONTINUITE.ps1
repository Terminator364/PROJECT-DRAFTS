# Moteur Blessing: synchronisation de documentation GitHub vers Documents/Moteur Blessing
# Sans API payante, sans telechargement du moteur.
$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$RawRoot="https://raw.githubusercontent.com/Terminator364/PROJECT-DRAFTS/main/MOTEUR-BLESSING"
$Files=@("README.md","CONTINUITE.md","ETAT_V112.md","FEUILLE_ROUTE.md","LIVRAISONS.md","JOURNAL.md","MANIFEST.json")
$Results=@()
foreach($name in $Files) {
 $tmp=Join-Path $Root ($name+".incoming")
 $dst=Join-Path $Root $name
 try {
   Invoke-WebRequest -UseBasicParsing -TimeoutSec 30 -Uri ($RawRoot+"/"+$name) -OutFile $tmp
   if ((Get-Item $tmp).Length -lt 30) { throw "Fichier anormalement court" }
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
