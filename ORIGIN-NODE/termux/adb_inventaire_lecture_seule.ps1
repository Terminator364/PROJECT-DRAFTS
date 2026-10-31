# ORIGIN: read-only ADB inventory on a personally owned, authorized phone.
# It does NOT unlock the bootloader, flash images, read IMEI, or wipe data.
$ErrorActionPreference = 'Continue'
$adb = Get-Command adb -ErrorAction SilentlyContinue
if (-not $adb) { Write-Error 'ADB absent: install official Android platform-tools'; exit 1 }
$devices = & adb devices
Write-Host $devices
$online = @($devices | Select-String '^\S+\s+device$')
if ($online.Count -ne 1) { Write-Error 'Exactly one authorized phone is required'; exit 2 }
$dest = Join-Path $env:USERPROFILE ('Desktop\ORIGIN_INVENTAIRE_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.txt')
$cmds = @(
 'getprop ro.product.model', 'getprop ro.product.device',
 'getprop ro.build.version.release', 'getprop ro.build.version.sdk',
 'getprop ro.build.version.security_patch', 'getprop ro.product.cpu.abi',
 'getprop ro.boot.verifiedbootstate', 'getprop ro.boot.flash.locked',
 'cat /proc/meminfo', 'df -h /data', 'dumpsys battery', 'dumpsys power'
)
"ORIGIN READ-ONLY REPORT — $(Get-Date -Format o)" | Out-File $dest -Encoding UTF8
foreach($cmd in $cmds){
  "`n### $cmd" | Out-File $dest -Append -Encoding UTF8
  (& adb shell $cmd 2>&1 | Out-String) | Out-File $dest -Append -Encoding UTF8
}
Write-Host "Local report: $dest"
Write-Warning 'Review/redact personal data before sharing. Do not publish logs.'
