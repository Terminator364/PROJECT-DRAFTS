$ErrorActionPreference='Stop'
$exe=Join-Path $PSScriptRoot 'bin\MBMPC-Remote-OneClick.exe'
if(!(Test-Path $exe)){ throw "Native executable missing: $exe" }
$lab=Join-Path $env:TEMP 'MBMPC-Remote-OneClick-WinLab'
New-Item -Path $lab -ItemType Directory -Force | Out-Null
$fake=Join-Path $lab 'bin with spaces'
New-Item -Path $fake -ItemType Directory -Force|Out-Null
$receipt=Join-Path $lab 'receipt.txt'
$log=Join-Path $lab 'events.log'
Remove-Item $receipt,$log -ErrorAction SilentlyContinue -Force
@'
@echo off
echo %* >> "%MBMPC_LAB_RECEIPT%"
ping -n 10 127.0.0.1 >nul
exit /b 23
'@ | Set-Content -LiteralPath (Join-Path $fake 'npx.cmd') -Encoding ascii
$env:PATH=$fake+';'+$env:PATH
$env:MBMPC_LAB_MODE='1'
$env:MBMPC_LAB_NET='offline'
$env:MBMPC_LAB_RAM='96'
$env:MBMPC_LAB_RECEIPT=$receipt
$env:MBMPC_LAB_LOG=$log

$p=$null;$second=$null
try {
    $p=Start-Process -FilePath $exe -PassThru
    $deadline=[DateTime]::UtcNow.AddSeconds(18)
    while(!(Test-Path $receipt) -and [DateTime]::UtcNow -lt $deadline){
        Start-Sleep -Milliseconds 250
        if($p.HasExited){throw "GUI exited early with exit code $($p.ExitCode)"}
    }
    if(!(Test-Path $receipt)){ throw "Actual CreateProcess did not launch fake npx within 18 seconds" }
    $args=(Get-Content $receipt | Select-Object -First 1).Trim()
    if($args -ne '--yes @wonderwhy-er/desktop-commander@latest remote'){
        throw "Wrong launch args: $args"
    }
    Write-Host "NATIVE_ACTUAL_COMMAND_PASS: $args"
    $p.Refresh()
    $mb=[math]::Round($p.WorkingSet64/1MB,2)
    Write-Host "NATIVE_GUI_RAM_MB=$mb"
    if($mb -gt 45){throw "GUI exceeds 45 MB working-set budget: $mb"}
    if(!(Test-Path $log)){throw "Missing diagnostic log"}
    $deadline=[DateTime]::UtcNow.AddSeconds(8)
    while((Get-Content $log -Raw) -notmatch 'NETWORK_CHECK_FAILED' -and [DateTime]::UtcNow -lt $deadline){
        Start-Sleep -Milliseconds 250
    }
    $events=Get-Content $log -Raw
    if($events -notmatch 'CMD_SPAWNED'){throw 'Native CreateProcess success was not logged'}
    if($events -notmatch 'NETWORK_CHECK_FAILED'){throw 'Simulated offline message was not logged'}
    Write-Host 'OFFLINE_SIMULATION_PASS'

    # Second double click must not spawn a second Remote agent.
    $second=Start-Process -FilePath $exe -PassThru
    $second.WaitForExit(5000)|Out-Null
    if(!$second.HasExited){throw 'Second click remained resident; singleton not respected'}
    Start-Sleep -Milliseconds 500
    $count=@(Get-Content $receipt).Count
    if($count -ne 1){throw "Duplicate npx invocations detected: $count"}
    Write-Host 'DOUBLE_CLICK_SINGLETON_PASS'

    Add-Type @'
using System;
using System.Runtime.InteropServices;
public class MBMPC_UI {
  [DllImport("user32.dll",CharSet=CharSet.Unicode)]
  public static extern IntPtr FindWindow(string cls,string title);
}
'@
    $p.Refresh()
    if($p.HasExited) { throw "Native GUI crashed during lab run: $($p.ExitCode)" }
    if([MBMPC_UI]::FindWindow('MBMPC_REMOTE_ONECLICK_NATIVE',$null) -eq [IntPtr]::Zero){
        Write-Host 'HEADLESS_RUNNER_UI_VISIBILITY_UNVERIFIED: interactive visual acceptance required on desktop'
    } else {
        Write-Host 'WIN32_GUI_VISIBLE_CLASS_PASS'
    }
    Write-Host 'NATIVE_WINDOWS_LAB_PASS'
} finally {
    if($second -and !$second.HasExited){Stop-Process -Id $second.Id -Force -ErrorAction SilentlyContinue}
    if($p -and !$p.HasExited){Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue}
    # Only our fake npx session children are targeted, never a real user process.
    # The CI runner is disposable: no real Desktop Commander token ever present.
}
