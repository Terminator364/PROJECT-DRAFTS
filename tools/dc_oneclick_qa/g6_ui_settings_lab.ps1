$ErrorActionPreference='Stop'
$exe=Join-Path $PSScriptRoot 'bin\MBMPC-Remote-OneClick-G6.exe'
$work=Join-Path $env:TEMP ('G6-SettingsSmoke-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $work -Force|Out-Null
$env:LOCALAPPDATA=$work
$dir=Join-Path $work 'MBMPC-RemoteOneClick'
New-Item -ItemType Directory -Path $dir -Force|Out-Null
$legacy=Join-Path $dir 'trusted_home_wifi.v1'
$enc=New-Object Text.UnicodeEncoding($false,$true,$true)
[IO.File]::WriteAllText($legacy,('Lab Home WiFi'+[char]10+'{LAB-ADAPTER-01}'),$enc)
$env:MBMPC_LAB_MODE='1'
$env:MBMPC_LAB_WIFI='other'
$env:MBMPC_LAB_TRUST='0'
$env:MBMPC_LAB_COST='metered'
$env:MBMPC_LAB_NET='offline'
$env:MBMPC_LAB_LOG=Join-Path $work 'gui-events.log'
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class G6Api {
  [DllImport("user32.dll",CharSet=CharSet.Unicode)]
  public static extern IntPtr FindWindow(string cls,string name);
  [DllImport("user32.dll")]public static extern IntPtr GetDlgItem(IntPtr w,int id);
  [DllImport("user32.dll")]public static extern bool PostMessage(IntPtr w,uint m,int a,IntPtr b);
  [DllImport("user32.dll")]public static extern IntPtr SendMessage(IntPtr w,uint m,IntPtr a,IntPtr b);
}
'@
$p=$null
try{
    $p=Start-Process -FilePath $exe -PassThru
    $deadline=[DateTime]::UtcNow.AddSeconds(12)
    $ui=[IntPtr]::Zero
    while([DateTime]::UtcNow -lt $deadline){
       $ui=[G6Api]::FindWindow('MBMPC_REMOTE_ONECLICK_NATIVE_G6',$null)
       if($ui -ne [IntPtr]::Zero){break}
       Start-Sleep -Milliseconds 150
    }
    if($ui -eq [IntPtr]::Zero){
        # Hosted Windows services may run in a noninteractive session.
        # Validate launch and fail-closed evidence without claiming visual proof.
        $events=if(Test-Path $env:MBMPC_LAB_LOG){Get-Content $env:MBMPC_LAB_LOG -Raw}else{''}
        if(!$events.Contains('UI_FIRST_PAINT') -or !$events.Contains('G5_FAIL_CLOSED_NO_NEW_AGENT')){
            throw 'G6_HEADLESS_GUARD_OR_PAINT_FAILED'
        }
        Write-Host 'G6_HEADLESS_SERVICE_DESKTOP: VISUAL_AND_CLICK_ACCEPTANCE_DEFERRED_TO_REAL_USER_DESKTOP'
        return
    }
    [G6Api]::PostMessage($ui,0x111,103,[IntPtr]::Zero)|Out-Null
    $manager=[IntPtr]::Zero
    $deadline=[DateTime]::UtcNow.AddSeconds(12)
    while([DateTime]::UtcNow -lt $deadline){
       $manager=[G6Api]::FindWindow('MBMPC_G6_APPROVED_NETS',$null)
       if($manager -ne [IntPtr]::Zero){break}
       Start-Sleep -Milliseconds 150
    }
    if($manager -eq [IntPtr]::Zero){throw 'G6_SETTINGS_WINDOW_NOT_FOUND'}
    $list=[G6Api]::GetDlgItem($manager,220)
    if($list -eq [IntPtr]::Zero){throw 'G6_SETTINGS_LIST_NOT_FOUND'}
    $count=[G6Api]::SendMessage($list,0x18B,[IntPtr]::Zero,[IntPtr]::Zero).ToInt64()
    if($count -ne 1){throw "G6_OLD_HOME_MIGRATION_LIST_COUNT=$count"}
    foreach($id in @(221,222,223,224)){
       if([G6Api]::GetDlgItem($manager,$id) -eq [IntPtr]::Zero){throw "G6_SETTINGS_ACTION_MISSING=$id"}
    }
    # Repeated button click returns to existing manager window.
    for($k=0;$k -lt 20;$k++){[G6Api]::PostMessage($ui,0x111,103,[IntPtr]::Zero)|Out-Null}
    Start-Sleep -Milliseconds 400
    if([G6Api]::FindWindow('MBMPC_G6_APPROVED_NETS',$null) -ne $manager){throw 'G6_DUPLICATE_MANAGER'}
    [G6Api]::PostMessage($manager,0x10,0,[IntPtr]::Zero)|Out-Null
    [G6Api]::PostMessage($ui,0x10,0,[IntPtr]::Zero)|Out-Null
    [void]$p.WaitForExit(5500)
    if(!$p.HasExited){throw 'G6_GUI_PERSISTED_AFTER_CLOSE'}
    Write-Host 'G6_GUI_MANAGER_LEGACY_PROFILE_RETAINED_PASS'
    Write-Host 'G6_GUI_MANAGER_ADD_REVOKE_WINDOWS_BUTTONS_PASS'
    Write-Host 'G6_GUI_MANAGER_REPEATED_OPEN_SINGLETON_PASS'
    Write-Host 'G6_GUI_CLOSE_NO_RESIDENT_PROCESS_PASS'
}finally{
    if($p -and !$p.HasExited){Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue}
}
