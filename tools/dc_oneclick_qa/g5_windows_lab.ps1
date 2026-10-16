$ErrorActionPreference='Stop'
$root=$PSScriptRoot
$exe=Join-Path $root 'bin\MBMPC-Remote-OneClick-G5.exe'
if(!(Test-Path $exe)){throw 'G5_EXE_MISSING'}
$work=Join-Path $env:TEMP 'MBMPC-G5-Windows-Safety-Lab'
New-Item -ItemType Directory -Force $work|Out-Null
$fake=Join-Path $work 'npx-stub'
New-Item -ItemType Directory -Force $fake|Out-Null
@'
@echo off
echo %* >> "%MBMPC_LAB_RECEIPT%"
exit 0
'@ | Set-Content (Join-Path $fake 'npx.cmd') -Encoding ascii
$env:PATH="$fake;$env:PATH"
$env:MBMPC_LAB_MODE='1'
$env:MBMPC_LAB_NET='offline'
$env:MBMPC_LAB_RAM='97'
function Verify-Case([string]$name,[string]$wifi,[string]$cost,[string]$trust,[string]$secure,[bool]$wantStart){
    $receipt=Join-Path $work "$name-receipt.txt"
    $log=Join-Path $work "$name-log.txt"
    Remove-Item $receipt,$log -Force -ErrorAction SilentlyContinue
    $env:MBMPC_LAB_RECEIPT=$receipt
    $env:MBMPC_LAB_LOG=$log
    $env:MBMPC_LAB_WIFI=$wifi
    $env:MBMPC_LAB_COST=$cost
    $env:MBMPC_LAB_TRUST=$trust
    $env:MBMPC_LAB_OPEN=if($secure -eq 'open'){'1'}else{'0'}
    $proc=$null
    try{
        $proc=Start-Process -FilePath $exe -PassThru
        $limit=[DateTime]::UtcNow.AddSeconds(10)
        while([DateTime]::UtcNow -lt $limit){
            Start-Sleep -Milliseconds 140
            if($proc.HasExited){throw "$name GUI CRASHED"}
            if(Test-Path $log){
                $data=Get-Content $log -Raw
                if($data.Contains('G5_FAIL_CLOSED_NO_NEW_AGENT') -or $data.Contains('G5_HOME_UNMETERED_ALLOWED')){break}
            }
        }
        if(!(Test-Path $log)){throw "$name NO_LOG"}
        $data=Get-Content $log -Raw
        if(!$data.Contains('UI_FIRST_PAINT')){throw "$name NO_RENDER"}
        if($wantStart){
            if(!$data.Contains('G5_HOME_UNMETERED_ALLOWED')){throw "$name EXPECTED_SAFE_ALLOW"}
            $waitUntil=[DateTime]::UtcNow.AddSeconds(6)
            while(!(Test-Path $receipt) -and [DateTime]::UtcNow -lt $waitUntil){Start-Sleep -Milliseconds 120}
            if(!(Test-Path $receipt)){throw "$name EXPECTED_NPX"}
            $args=(Get-Content $receipt | Select-Object -First 1).Trim()
            if($args -ne '--yes @wonderwhy-er/desktop-commander@latest remote'){throw "$name BAD_NPX_ARGS:$args"}
            Write-Host "G5_ALLOWED=$name"
            # The fake npx uses 'exit' (not 'exit /b') so its mock CMD session
            # cannot survive to impersonate a real connected agent in the next case.
            Start-Sleep -Milliseconds 650
        } else {
            if(!$data.Contains('G5_FAIL_CLOSED_NO_NEW_AGENT')){throw "$name EXPECTED_FAIL_CLOSED"}
            if(Test-Path $receipt){throw "$name UNAUTHORIZED_NETWORK_USED"}
            if($name -eq 'no-wifi' -or $name -eq 'home-cost-unknown'){
                $retryUntil=[DateTime]::UtcNow.AddSeconds(6)
                while([DateTime]::UtcNow -lt $retryUntil){
                    Start-Sleep -Milliseconds 180
                    $data=Get-Content $log -Raw
                    if($data.Contains('G5_SAFE_RETRY_WIFI_NO_AGENT_KILL')){break}
                }
                if(!$data.Contains('G5_SAFE_RETRY_WIFI_NO_AGENT_KILL')){throw "$name NO_SAFE_RETRY_AFTER_BOOT"}
                if(Test-Path $receipt){throw "$name RETRY_USED_DATA_WITHOUT_TRUST"}
                Write-Host "G5_SAFE_RETRY_PASS=$name"
            }
            Write-Host "G5_BLOCKED=$name"
        }
        $proc.Refresh()
        $ram=[math]::Round($proc.WorkingSet64/1MB,2)
        if($ram -gt 45){throw "$name RAM_TOO_HIGH:$ram"}
    } finally {
        if($proc -and !$proc.HasExited){
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            [void]$proc.WaitForExit(5000)
        }
    }
}
Verify-Case 'home-approved-free' 'home' 'free' '1' 'secure' $true
Verify-Case 'campus-wifi' 'other' 'free' '0' 'secure' $false
Verify-Case 'home-metered' 'home' 'metered' '1' 'secure' $false
Verify-Case 'home-cost-unknown' 'home' 'unknown' '1' 'secure' $false
Verify-Case 'home-not-yet-approved' 'home' 'free' '0' 'secure' $false
Verify-Case 'no-wifi' 'none' 'unknown' '0' 'secure' $false
Verify-Case 'location-permission-denied' 'denied' 'unknown' '0' 'secure' $false
Verify-Case 'home-unsecured' 'home' 'free' '1' 'open' $false
Write-Host 'G5_WIN32_REAL_EXE_8_SCENARIOS_PASS'
