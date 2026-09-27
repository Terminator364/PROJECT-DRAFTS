param([switch]$NoOpen)
$ErrorActionPreference="SilentlyContinue"
$data=Join-Path $env:LOCALAPPDATA "TLIB-PC"
$boot=Join-Path $data "bootstrap-node.cjs"
$node=(Get-Command node -ErrorAction SilentlyContinue).Source
if(-not $node -or -not (Test-Path $boot)){ exit 2 }
$args=@($boot)
if($NoOpen){$args+="--no-open"}
Start-Process -FilePath $node -ArgumentList $args -WindowStyle Hidden
exit 0
