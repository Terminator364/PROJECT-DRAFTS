# KIN MOTO A2 — HTTP development server using built-in .NET.
# No Python/Node/install, no Vercel/hosting. Default: localhost ONLY.
# powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\serve_local.ps1
[CmdletBinding()]
param(
 [string]$Root = '',
 [ValidateRange(1024,65535)][int]$Port = 8789,
 [switch]$Lan
)
$ErrorActionPreference='Stop'
if (-not $Root) { $Root = Join-Path $PSScriptRoot '..\dist' }
$Root=[IO.Path]::GetFullPath($Root)
if (-not (Test-Path (Join-Path $Root 'index.html') -PathType Leaf)) { throw "No index.html in $Root. Run tools/build_offline.ps1 first." }
$rootWithSlash=$Root.TrimEnd('\','/')+[IO.Path]::DirectorySeparatorChar
$address=if($Lan){[Net.IPAddress]::Any}else{[Net.IPAddress]::Loopback}
$server=New-Object Net.Sockets.TcpListener($address,$Port)
$types=@{'.html'='text/html; charset=utf-8';'.js'='application/javascript; charset=utf-8';'.css'='text/css; charset=utf-8';'.webmanifest'='application/manifest+json';'.json'='application/json';'.svg'='image/svg+xml';'.png'='image/png';'.ico'='image/x-icon'}
$server.Start()
Write-Output "KINMOTO LOCAL SERVER: http://localhost:$Port/ (Ctrl+C to stop)"
Write-Output 'No Vercel calls, no upload, no third-party telemetry.'
if($Lan){Write-Warning 'LAN mode: HTTP accessible on local Wi-Fi only; no PWA/service worker on insecure mobile HTTP. Stop with Ctrl+C.'}
try {
 while($true) {
  $client=$server.AcceptTcpClient()
  try {
   $client.ReceiveTimeout=3000
   $stream=$client.GetStream()
   $reader=New-Object IO.StreamReader($stream,[Text.Encoding]::ASCII,$false,1024,$true)
   $requestLine=$reader.ReadLine()
   if(-not $requestLine){continue}
   while($true){$header=$reader.ReadLine();if([string]::IsNullOrEmpty($header)){break}}
   $parts=$requestLine.Split(' ')
   $method=$parts[0]
   $code=200;$reason='OK';$contentType='text/plain';$data=[byte[]]@()
   if($parts.Length -lt 2 -or $method -notin @('GET','HEAD')){$code=405;$reason='Method Not Allowed'}
   else {
    $path=$parts[1].Split('?')[0]
    try {$path=[uri]::UnescapeDataString($path)} catch {$path='/' }
    $path=$path.Replace('/',[IO.Path]::DirectorySeparatorChar)
    $relative=$path.TrimStart('\','/')
    if(-not $relative){$relative='index.html'}
    $full=[IO.Path]::GetFullPath((Join-Path $Root $relative))
    if(-not $full.StartsWith($rootWithSlash,[StringComparison]::OrdinalIgnoreCase)){$code=403;$reason='Forbidden'}
    elseif(-not [IO.File]::Exists($full)){$code=404;$reason='Not Found'}
    else {$data=[IO.File]::ReadAllBytes($full);$ext=[IO.Path]::GetExtension($full).ToLowerInvariant();if($types.ContainsKey($ext)){$contentType=$types[$ext]}}
   }
   if($code -ne 200){$data=[Text.Encoding]::UTF8.GetBytes($reason)}
   $header="HTTP/1.1 $code $reason`r`nContent-Type: $contentType`r`nContent-Length: $($data.Length)`r`nCache-Control: no-store, max-age=0`r`nX-Content-Type-Options: nosniff`r`nConnection: close`r`n`r`n"
   $b=[Text.Encoding]::ASCII.GetBytes($header);$stream.Write($b,0,$b.Length)
   if($method -ne 'HEAD'){$stream.Write($data,0,$data.Length)}
   $stream.Flush()
  } catch { Write-Warning $_.Exception.Message }
  finally {$client.Dispose()}
 }
} finally {$server.Stop()}
