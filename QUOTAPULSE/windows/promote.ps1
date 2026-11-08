$ErrorActionPreference='Stop'
$dir='%LOCALAPPDATA%\QuotaPulse'
$live=Join-Path $dir 'QuotaPulse.exe'
$stage=Join-Path $dir 'QuotaPulse.staged.exe'
$backup=Join-Path $dir 'QuotaPulse.rollback.exe'
if(!(Test-Path $stage)){throw 'STAGED_NOT_FOUND'}
if(!(Test-Path (Join-Path $dir 'probe-result.json'))){throw 'PROBE_RESULT_MISSING'}
$expected=(Get-FileHash $stage -Algorithm SHA256).Hash
$running=Get-Process -Name QuotaPulse -ErrorAction SilentlyContinue
foreach($p in @($running)){
 try{
  if($p.Path -ne $live){continue}
  $p.CloseMainWindow()|Out-Null
  if(-not $p.WaitForExit(5000)){Stop-Process -Id $p.Id -Force -ErrorAction Stop}
 }catch{throw ('OLD_WINDOW_STOP_FAILED: '+$_.Exception.Message)}
}
Start-Sleep -Milliseconds 250
if(Test-Path $backup){Remove-Item $backup -Force}
if(Test-Path $live){Move-Item $live $backup -Force}
try{
 Move-Item $stage $live -Force
 $got=(Get-FileHash $live -Algorithm SHA256).Hash
 if($got -ne $expected){throw 'SHA_MISMATCH'}
 $desktop='%USERPROFILE%\Desktop'
 if(!(Test-Path $desktop)){throw 'DESKTOP_UNAVAILABLE'}
 $shortcut=(New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $desktop 'QuotaPulse.lnk'))
 $shortcut.TargetPath=$live
 $shortcut.WorkingDirectory=$dir
 $shortcut.IconLocation=$live+',0'
 $shortcut.Description='QuotaPulse — compteur des appels Desktop Commander'
 $shortcut.Save()
 $p=Start-Process -FilePath $live -WorkingDirectory $dir -PassThru
 Write-Output ("PROMOTED_SHA256="+$got)
 Write-Output ("EXE="+$live)
 Write-Output ("DESKTOP_SHORTCUT="+(Join-Path $desktop 'QuotaPulse.lnk'))
 Write-Output ("RUNNING_PID="+$p.Id)
 Write-Output ("ROLLBACK="+$backup)
}catch{
 if(!(Test-Path $live) -and (Test-Path $backup)){Move-Item $backup $live -Force}
 throw
}
