$ErrorActionPreference='Stop'
$dir=Join-Path $env:LOCALAPPDATA 'LINK2HP'
$startup=Join-Path ([Environment]::GetFolderPath('Startup')) 'LINK2HP.lnk'
$desktop=Join-Path ([Environment]::GetFolderPath('Desktop')) 'LINK2HP.lnk'
Remove-Item $startup,$desktop -Force -ErrorAction SilentlyContinue
Get-CimInstance Win32_Process -Filter "name='node.exe'" -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like '*LINK2HP*agent.cjs*'} | ForEach-Object {Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue}
Write-Host 'Agent arrêté et raccourcis supprimés. Les téléchargements, fichiers locaux et certificats restent conservés.'
Write-Host ('Pour supprimer également les données après sauvegarde : '+$dir)
