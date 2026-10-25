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

# Desktop shortcut: direct Edge app launch. No VBS/PowerShell/health-check on user click.
$shortcut=Join-Path $desktop "TLIB.lnk"
$edgeCandidates=@(
  "$env:ProgramFiles (x86)\Microsoft\Edge\Application\msedge.exe",
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
  "$env:LOCALAPPDATA\Microsoft\Edge\Application\msedge.exe"
)
$edge=$edgeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if(-not $edge){ throw "Microsoft Edge executable not found" }
$ws=New-Object -ComObject WScript.Shell
$lnk=$ws.CreateShortcut($shortcut)
$lnk.TargetPath=$edge
$lnk.Arguments="--app=http://127.0.0.1:8787 --start-maximized --no-first-run"
$lnk.WorkingDirectory=(Split-Path $edge -Parent)
$icon=Join-Path $dataDir "TLIB.ico"
if(Test-Path $icon){$lnk.IconLocation=$icon+",0"}else{$lnk.IconLocation=$edge+",0"}
$lnk.Description="TLIB - Bibliotheque intelligente"
$lnk.Save()
Remove-Item (Join-Path $desktop "TLIB.vbs") -Force -ErrorAction SilentlyContinue

# Remove old URL shortcut if present.
Remove-Item (Join-Path $desktop "TLIB Cockpit.url") -Force -ErrorAction SilentlyContinue

# Silent smoke start; no modal UI.
Start-Process -FilePath $node -ArgumentList @((Join-Path $dataDir "bootstrap-node.cjs"),"--no-open") -WindowStyle Hidden
Write-Host "TLIB hidden launcher installed."
