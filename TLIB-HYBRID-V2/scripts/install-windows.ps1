param([string]$RepoDir = (Resolve-Path (Join-Path $PSScriptRoot "..")))
$ErrorActionPreference="Stop"
$node=(Get-Command node -ErrorAction Stop).Source
$dataDir=Join-Path $env:LOCALAPPDATA "TLIB-PC"
$desktop=[Environment]::GetFolderPath("Desktop")
$startup=[Environment]::GetFolderPath("Startup")
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null

Copy-Item (Join-Path $RepoDir "scripts\bootstrap-node.cjs") (Join-Path $dataDir "bootstrap-node.cjs") -Force
Copy-Item (Join-Path $RepoDir "scripts\launch-hidden.vbs") (Join-Path $dataDir "launch-hidden.vbs") -Force

# Startup: hidden VBS -> Node bootstrap, no PowerShell window.
$vbs=Join-Path $startup "TLIB-PC-Agent.vbs"
@(
'Set sh = CreateObject("WScript.Shell")',
'Set fso = CreateObject("Scripting.FileSystemObject")',
'nodePath = sh.ExpandEnvironmentStrings("%ProgramFiles%\nodejs\node.exe")',
'If Not fso.FileExists(nodePath) Then nodePath = "node.exe"',
'boot = sh.ExpandEnvironmentStrings("%LOCALAPPDATA%\TLIB-PC\bootstrap-node.cjs")',
'args = Chr(34) & nodePath & Chr(34) & " " & Chr(34) & boot & Chr(34) & " --no-open"',
'sh.Run args, 0, False'
) | Set-Content -Encoding ASCII $vbs

# Desktop shortcut: wscript -> launch-hidden.vbs.
$shortcut=Join-Path $desktop "TLIB.lnk"
$ws=New-Object -ComObject WScript.Shell
$lnk=$ws.CreateShortcut($shortcut)
$lnk.TargetPath="$env:SystemRoot\System32\wscript.exe"
$lnk.Arguments='"'+(Join-Path $dataDir "launch-hidden.vbs")+'"'
$lnk.WorkingDirectory=$dataDir
$icon=Join-Path $dataDir "TLIB.ico"
if(Test-Path $icon){$lnk.IconLocation=$icon+",0"}else{$lnk.IconLocation="$env:SystemRoot\System32\SHELL32.dll,220"}
$lnk.Description="TLIB - Bibliotheque intelligente"
$lnk.Save()

# Remove old URL shortcut if present.
Remove-Item (Join-Path $desktop "TLIB Cockpit.url") -Force -ErrorAction SilentlyContinue

# Silent smoke start; no modal UI.
Start-Process -FilePath $node -ArgumentList @((Join-Path $dataDir "bootstrap-node.cjs"),"--no-open") -WindowStyle Hidden
Write-Host "TLIB hidden launcher installed."
