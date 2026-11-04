# KINMOTO — build pure PowerShell 5.1+ : ni Python, ni npm, ni Vercel.
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\build_offline.ps1
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$dist = Join-Path $root 'dist'
$assetsOut = Join-Path $dist 'assets'
[IO.Directory]::CreateDirectory($dist) | Out-Null
[IO.Directory]::CreateDirectory($assetsOut) | Out-Null
$utf8 = New-Object System.Text.UTF8Encoding($false)
function ReadText([string]$relative) {
  return [IO.File]::ReadAllText((Join-Path $root $relative), [Text.Encoding]::UTF8)
}
function WriteText([string]$name,[string]$data) {
  [IO.File]::WriteAllText((Join-Path $dist $name), $data, $utf8)
}
$modules = @('src/road_surface.js','src/math.js','src/navigation.js','src/geom.js','src/bike_physics.js','src/sim.js','src/render.js','src/main.js')
$bundle = New-Object System.Collections.Generic.List[string]
foreach($module in $modules) {
  $source = ReadText $module
  $source = [regex]::Replace($source, '(?m)^import .*?;\s*$', '')
  $source = [regex]::Replace($source, '(?m)^export ', '')
  [void]$bundle.Add('// MODULE ' + $module + "`n" + $source)
}
$css = ReadText 'style.css'
$html = ReadText 'index.html'
$cssNeedle = '<link rel="stylesheet" href="./style.css"/>'
$jsNeedle = '<script type="module" src="./src/main.js"></script>'
if (-not $html.Contains($cssNeedle) -or -not $html.Contains($jsNeedle)) { throw 'Missing expected HTML source markers; aborting build.' }
$html = $html.Replace($cssNeedle, "<style>`n" + $css + "`n</style>")
$html = $html.Replace($jsNeedle, "`n<script>`n" + [string]::Join("`n", $bundle) + "`n</script>`n")
WriteText 'index.html' $html
WriteText 'KIN_MOTO_A2_LAB_JOUER.html' $html
foreach($size in @(192,512)) {
  $dest = Join-Path $assetsOut "icon-$size.png"
  $base64 = Join-Path $root "assets/icon-$size.png.base64"
  if (Test-Path $base64) {
    $bytes = [Convert]::FromBase64String([IO.File]::ReadAllText($base64).Trim())
    [IO.File]::WriteAllBytes($dest,$bytes)
  } elseif (Test-Path (Join-Path $root "assets/icon-$size.png")) {
    Copy-Item (Join-Path $root "assets/icon-$size.png") $dest -Force
  } else { throw "Missing icon $size" }
}
Copy-Item (Join-Path $root 'assets/icon.svg') (Join-Path $assetsOut 'icon.svg') -Force
WriteText 'manifest.webmanifest' (ReadText 'manifest.webmanifest')
$hash = [Security.Cryptography.SHA256]::Create()
try {
  $hex = [BitConverter]::ToString($hash.ComputeHash([Text.Encoding]::UTF8.GetBytes($html))).Replace('-','').ToLowerInvariant().Substring(0,12)
} finally { $hash.Dispose() }
# Substituting only the cache hash ensures updates invalidate obsolete offline caches.
$template = @'
const CACHE='kin-moto-a2-lab-__HASH__';
const FILES=['./','./index.html','./manifest.webmanifest','./assets/icon.svg','./assets/icon-192.png','./assets/icon-512.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(Promise.all([caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('kin-moto-a2-lab-')&&k!==CACHE).map(k=>caches.delete(k)))),self.clients.claim()])));
self.addEventListener('fetch',e=>{
 const req=e.request,url=new URL(req.url);
 if(req.method!=='GET'||url.origin!==self.location.origin)return;
 if(req.mode==='navigate'){
  e.respondWith(fetch(req).then(r=>{if(r.ok){const copy=r.clone();caches.open(CACHE).then(c=>c.put('./index.html',copy)).catch(()=>{});}return r;})
   .catch(()=>caches.match('./index.html')));return;
 }
 e.respondWith(caches.match(req).then(hit=>hit||fetch(req).then(r=>{if(r.ok){const copy=r.clone();caches.open(CACHE).then(c=>c.put(req,copy)).catch(()=>{});}return r;})));
});
'@
WriteText 'sw.js' ($template.Replace('__HASH__',$hex))
$sizeBytes = ([Text.Encoding]::UTF8.GetByteCount($html))
Write-Output "KINMOTO BUILD OFFLINE PASS: HTML=$sizeBytes bytes; modules=$($modules.Length); cache=$hex; output=$dist"
