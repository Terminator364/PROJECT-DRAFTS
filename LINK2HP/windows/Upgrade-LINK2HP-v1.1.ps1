# LINK2HP 1.1 guarded user-scoped hot-upgrade. Do not reset secrets, DB or TLS material.
$ErrorActionPreference = 'Stop'
$root = 'C:\Users\HP\AppData\Local\LINK2HP'
$app = Join-Path $root 'app'
$stage = Join-Path $root 'stage_v1_1_20261110'
$node = Join-Path $app 'node.exe'
$files = @('agent.cjs','network.cjs','pairing.cjs','wifi.cjs')
$backup = Join-Path $root ('rollback_v1_1_'+(Get-Date -Format 'yyyyMMdd_HHmmss'))
if (!(Test-Path (Join-Path $root 'config.json'))) { throw 'OWNER_CONFIG_MISSING' }
if (!(Test-Path $node)) { throw 'OWNER_NODE_MISSING' }
foreach ($f in $files) { if (!(Test-Path (Join-Path $stage $f))) { throw ('STAGED_FILE_MISSING_'+$f) } }
New-Item -ItemType Directory -Path $backup -Force | Out-Null
foreach ($f in $files) {
    $current = Join-Path $app $f
    if (Test-Path $current) { Copy-Item $current (Join-Path $backup $f) -Force }
}
# Config and TLS remain at their original paths; backup config with inherited owner ACL.
Copy-Item (Join-Path $root 'config.json') (Join-Path $backup 'config.backup.json') -Force
function Get-AgentProcess {
    @(Get-CimInstance Win32_Process -Filter "name='node.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like '*LINK2HP*app*agent.cjs*' })
}
function Launch-Agent {
    # PCRC has an isolated LOCALAPPDATA value. Set the REAL Windows owner path.
    $env:LOCALAPPDATA = 'C:\Users\HP\AppData\Local'
    $env:APPDATA = 'C:\Users\HP\AppData\Roaming'
    Start-Process -FilePath $node -ArgumentList ('"'+(Join-Path $app 'agent.cjs')+'"') -WindowStyle Hidden -PassThru | Out-Null
}
function Verify-Running {
    for ($i=0; $i -lt 14; $i++) {
        Start-Sleep -Milliseconds 800
        try {
            $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 -Uri 'http://127.0.0.1:17643/api/status'
            if ($r.StatusCode -eq 200) {
                $j = $r.Content | ConvertFrom-Json
                if ($j.online -eq $true) { return $true }
            }
        } catch {}
    }
    return $false
}
$old = @(Get-AgentProcess)
foreach ($p in $old) { Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop }
Start-Sleep -Milliseconds 750
try {
    foreach ($f in $files) { Copy-Item (Join-Path $stage $f) (Join-Path $app $f) -Force }
    Launch-Agent
    if (!(Verify-Running)) { throw 'NEW_SERVICE_HEALTH_FAILED' }
    $p = @(Get-AgentProcess)
    if ($p.Count -lt 1) { throw 'NEW_SERVICE_PROCESS_MISSING' }
    Write-Output ('LINK2HP_V1_1_INSTALLED_OK;BACKUP='+$backup+';PID='+$p[0].ProcessId)
} catch {
    $cause = $_.Exception.Message
    foreach ($p in @(Get-AgentProcess)) { Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue }
    foreach ($f in $files) {
        $b = Join-Path $backup $f
        $to = Join-Path $app $f
        if (Test-Path $b) { Copy-Item $b $to -Force }
        elseif (Test-Path $to) { Remove-Item $to -Force }
    }
    Launch-Agent
    $restored = Verify-Running
    throw ('LINK2HP_V1_1_ROLLBACK;REASON='+$cause+';OLD_RESTORED='+$restored)
}
