$ErrorActionPreference='Stop'
$here=Split-Path -Parent $MyInvocation.MyCommand.Path
$source=Join-Path $here 'BookHarvesterApp'
$sourceExe=Join-Path $source 'BlessingBookHarvester.exe'
if (!(Test-Path -LiteralPath $sourceExe)) { throw 'Archive incomplete: BookHarvesterApp exe missing.' }
$root=Join-Path $env:LOCALAPPDATA 'BlessingBookHarvester'
$target=Join-Path $root 'app-v1.1.1'
New-Item -ItemType Directory -Path $target -Force | Out-Null
Copy-Item -Path (Join-Path $source '*') -Destination $target -Recurse -Force
$exe=Join-Path $target 'BlessingBookHarvester.exe'
$probe=Join-Path $root 'self-test-onedir.json'
if (Test-Path -LiteralPath $probe) { Remove-Item -LiteralPath $probe -Force }
$p=Start-Process -FilePath $exe -ArgumentList @('--self-test','--self-test-report',('"' + $probe + '"')) -PassThru
if (-not $p.WaitForExit(45000)) { try { $p.Kill() } catch {} ; throw 'Executable stuck beyond 45s.' }
if ($p.ExitCode -ne 0 -or !(Test-Path $probe)) { throw 'Executable self-test failed.' }
$json=Get-Content -Raw -LiteralPath $probe | ConvertFrom-Json
if ($json.ok -ne $true) { throw 'Executable dependency self-test failed.' }
$desktop=[Environment]::GetFolderPath('Desktop')
$lnk=Join-Path $desktop 'Blessing BookHarvester.lnk'
$shortcut=(New-Object -ComObject WScript.Shell).CreateShortcut($lnk)
$shortcut.TargetPath=$exe
$shortcut.WorkingDirectory=$target
$shortcut.Description='Blessing BookHarvester'
$shortcut.Save()
if (!(Test-Path $lnk)) { throw 'Shortcut not created.' }
Write-Output ('INSTALLED '+$exe)
