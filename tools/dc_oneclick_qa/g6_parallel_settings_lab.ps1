$ErrorActionPreference='Stop'
$exe=Join-Path $PSScriptRoot 'bin\G6-Profile-Stress.exe'
if(!(Test-Path $exe)){throw 'NO_TEST_BINARY'}
$root=Join-Path $env:TEMP ('G6-ParallelSettings-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $root -Force|Out-Null
$env:LOCALAPPDATA=$root
$sub=Join-Path $root 'MBMPC-RemoteOneClick'
New-Item -ItemType Directory -Path $sub -Force|Out-Null
$procs=@()
try {
    for($i=0;$i -lt 12;$i++){
        $ssid=('Race-{0:00}' -f $i)
        $guid=('{LOCAL-' + ('{0:00}' -f $i) + '}')
        $procs+=Start-Process -FilePath $exe -ArgumentList @('--grant',$ssid,$guid) -PassThru
    }
    $success=0
    foreach($p in $procs){
        [void]$p.WaitForExit(15000)
        if(!$p.HasExited){throw "WRITE_STUCK_PID=$($p.Id)"}
        if($p.ExitCode -ne 0){throw "CONCURRENT_WRITE_FAILED_PID=$($p.Id),EXIT=$($p.ExitCode)"}
        ++$success
    }
    & $exe --count 12
    if($LASTEXITCODE){throw 'PARALLEL_WRITE_LOST_OR_CORRUPT_SETTINGS'}
    Write-Host "G6_CONCURRENT_NETWORK_GRANTS_PASS=$success"
} finally {
    foreach($p in $procs){if(!$p.HasExited){Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue}}
}
