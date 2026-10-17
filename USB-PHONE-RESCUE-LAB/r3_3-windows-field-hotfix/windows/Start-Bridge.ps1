param(
  [string]$UsbIp = "",
  [int]$Port = 8876,
  [switch]$DiagnoseOnly
)
# Independent current-user guardian. Never changes networking, firewall, or Windows policy.
$ErrorActionPreference = "Stop"
$Root = Join-Path $env:LOCALAPPDATA "BCP-USB-Rescue"
$Agent = Join-Path $Root "windows\bridge_agent.py"
$State = Join-Path $Root "private-state"
$Workspace = Join-Path $Root "workspace"
$LogDir = Join-Path $Root "logs"
New-Item -Force -ItemType Directory -Path $State,$Workspace,$LogDir | Out-Null
$Log = Join-Path $LogDir "guardian.jsonl"
function Event([string]$Code,[string]$Detail) {
  $obj = [ordered]@{ utc=(Get-Date).ToUniversalTime().ToString('o'); code=$Code; detail=$Detail }
  try {
    if ((Test-Path -LiteralPath $Log) -and ((Get-Item -LiteralPath $Log).Length -gt 2097152)) {
      Move-Item -LiteralPath $Log -Destination ($Log + '.old') -Force
    }
  } catch { Write-Warning 'Could not rotate rescue guardian log' }
  Add-Content -LiteralPath $Log -Value ($obj | ConvertTo-Json -Compress) -Encoding UTF8
  Write-Host "[$Code] $Detail"
}
function PythonCommand {
  foreach ($command in @('py','python')) {
    $found=Get-Command $command -ErrorAction SilentlyContinue
    if (-not $found) { continue }
    try {
      $opts=if($command -eq 'py'){@('-3','-c','import sys;assert sys.version_info >= (3,10);print(sys.executable)')}else{@('-c','import sys;assert sys.version_info >= (3,10);print(sys.executable)')}
      $result=@(& $found.Source @opts 2>$null)
      if($LASTEXITCODE -eq 0 -and $result.Count -ge 1 -and (Test-Path -LiteralPath $result[-1])) {
        return @{ executable=[string]$result[-1] }
      }
    } catch { }
  }
  return $null
}
function Candidates {
  # Filter strictly for recognizable Android USB tether adapters, never all active Ethernet.
  $out=@()
  try {
    $adapters=@(Get-NetAdapter -ErrorAction Stop | Where-Object {
      $_.Status -eq 'Up' -and $_.InterfaceDescription -match 'RNDIS|USB.*Ethernet|Remote NDIS|USB NCM|CDC.NCM'
    })
    foreach ($a in $adapters) {
      $ips=@(Get-NetIPAddress -InterfaceIndex $a.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object {$_.IPAddress -match '^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)'})
      $config=Get-NetIPConfiguration -InterfaceIndex $a.ifIndex -ErrorAction SilentlyContinue
      $gateway=if($config -and $config.IPv4DefaultGateway){[string]$config.IPv4DefaultGateway.NextHop}else{''}
      foreach($ip in $ips) { $out+=@{interface=$a.Name; ip=$ip.IPAddress; gateway=$gateway} }
    }
  } catch { Event 'USB_PROBE_ERROR' $_.Exception.Message }
  return $out
}
function SelectUsbIp {
  if ($UsbIp) {
    $actual=@(Candidates | Where-Object { $_.ip -eq $UsbIp })
    if ($actual.Count -eq 1) { return $UsbIp }
    return $null
  }
  $candidates=@(Candidates)
  if ($candidates.Count -eq 1) { return $candidates[0].ip }
  return $null
}
if (-not (Test-Path -LiteralPath $Agent)) {throw "Missing agent: $Agent"}
if ($UsbIp -and $UsbIp -notmatch '^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)') {throw 'Only private USB adapter IP is permitted'}
if ($Port -lt 1024 -or $Port -gt 65535) {throw 'Port must be 1024..65535'}
$python=PythonCommand
if (-not $python){throw 'Python 3 is missing: install Python 3.10+ for Windows.'}
if ($DiagnoseOnly) {
  Event 'PROBE' ('Candidates: '+((@(Candidates)) | ConvertTo-Json -Compress))
  Write-Host "Python: $($python.executable), Selected IP: $(SelectUsbIp)"
  exit 0
}
$mutex=New-Object System.Threading.Mutex($false,'Local\BCP_USB_RESCUE_GUARDIAN_R1')
try { $newInstance=$mutex.WaitOne(0,$false) } catch [System.Threading.AbandonedMutexException] { $newInstance=$true }
if(-not $newInstance){ Write-Host 'BCP USB Rescue Guardian is already running in this Windows session.'; exit 0 }
Event 'GUARDIAN_ONLINE' 'Waiting for Android USB tether and supervising the independent Windows agent.'
$failures=0
$lastWaitUsbLog=(Get-Date).AddMinutes(-2)
while ($true) {
  $ip=SelectUsbIp
  if (-not $ip) {
    if(((Get-Date)-$lastWaitUsbLog).TotalSeconds -ge 60) {
      Event 'WAIT_USB' 'USB tether adapter unavailable / no unique candidate. Connect phone, enable USB tethering.'
      $lastWaitUsbLog=Get-Date
    }
    Start-Sleep -Seconds 10
    continue
  }
  # Keep agent log free of pairing material. Only the local user reads the state/key file.
  $arguments=@(('"'+$Agent+'"'),'--bind',$ip,'--port',"$Port",'--state',('"'+$State+'"'),'--workspace',('"'+$Workspace+'"'))
  $gateway=@(Candidates | Where-Object {$_.ip -eq $ip} | Select-Object -First 1)
  if($gateway.Count -eq 1 -and $gateway[0].gateway -match '^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)'){
    $arguments+=@('--reverse-peer',$gateway[0].gateway)
    Event 'REVERSE_OUTBOUND_READY' "phone_gateway=$($gateway[0].gateway) port=8768"
  }
  try {
    $process=Start-Process -FilePath $python.executable -ArgumentList $arguments -PassThru -WindowStyle Hidden
    Event 'AGENT_START' "pid=$($process.Id) private_usb_ip=$ip port=$Port"
    $lifetimeStart=Get-Date
    while (-not $process.HasExited) {
      Start-Sleep -Seconds 5
      $process.Refresh()
      if ((SelectUsbIp) -ne $ip) {
        Event 'USB_ROUTE_CHANGED' "Old IP=$ip is absent. Restarting only BCP agent."
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        $process.WaitForExit(3000) | Out-Null
        break
      }
    }
    Event 'AGENT_EXIT' "pid=$($process.Id) code=$($process.ExitCode)"
    if (((Get-Date)-$lifetimeStart).TotalSeconds -ge 60) { $failures=0 } else { $failures++ }
  } catch {
    $failures++
    Event 'AGENT_START_ERROR' $_.Exception.Message
  }
  if ($failures -ge 5) {
    Event 'CIRCUIT_BREAKER' '5 rapid failures. Pausing for 120 seconds before attempting recovery.'
    Start-Sleep -Seconds 120
    $failures=0
  } else {
    Start-Sleep -Seconds ([Math]::Min(30,[Math]::Pow(2,[Math]::Max(1,$failures))))
  }
}