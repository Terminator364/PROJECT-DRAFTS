$taskName = "TLIB-PC-Agent"
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
$desktop = [Environment]::GetFolderPath("Desktop")
Remove-Item (Join-Path $desktop "TLIB Cockpit.url") -Force -ErrorAction SilentlyContinue
Write-Host "TLIB-PC startup task and desktop shortcut removed. Local database was preserved."
