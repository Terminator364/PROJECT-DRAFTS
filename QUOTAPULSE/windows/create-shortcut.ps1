$ErrorActionPreference='Stop'
$target='%LOCALAPPDATA%\QuotaPulse\QuotaPulse.exe'
$desktop='%USERPROFILE%\Desktop'
if(!(Test-Path $target)){throw 'EXE_MISSING'}
if(!(Test-Path $desktop)){throw 'DESKTOP_MISSING'}
$link=Join-Path $desktop 'QuotaPulse.lnk'
$w=New-Object -ComObject WScript.Shell
$s=$w.CreateShortcut($link)
$s.TargetPath=$target
$s.WorkingDirectory=Split-Path $target
$s.IconLocation=$target+',0'
$s.Description='QuotaPulse - compteur local de quota Desktop Commander'
$s.Save()
Write-Output ('SHORTCUT_OK='+$link+';BYTES='+((Get-Item $link).Length))
