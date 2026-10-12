# Explicit, narrowly scoped Windows Defender Firewall exception for a REAL Android USB
# tether network adapter. Never invoked by the normal installer / guardian.
# User must initiate and approve UAC. No network profile is modified.
param([switch]$Undo, [int]$Port=8766)
$ErrorActionPreference='Stop'
$Name='BCPUsbRescueUsbOnly8766'
$Display='BCP USB Rescue - Android USB tether only'
if ($Port -ne 8766) { throw 'This approved helper is restricted to BCP USB Rescue TCP 8766.' }
$id = [Security.Principal.WindowsIdentity]::GetCurrent()
$admin = New-Object Security.Principal.WindowsPrincipal($id)
if (-not $admin.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
  throw 'Administrator approval is required. Run FIX-USB-FIREWALL.cmd and accept Windows UAC.'
}
if ($Undo) {
  $existing = Get-NetFirewallRule -Name $Name -ErrorAction SilentlyContinue
  if ($existing) { $existing | Remove-NetFirewallRule -ErrorAction Stop; Write-Host 'BCP USB-only rule removed.' }
  else { Write-Host 'No BCP USB-only rule was installed.' }
  exit 0
}
# A genuine USB tether adapter must be ACTIVE and carry a private unicast IPv4.
# Filtering by both device description and interface index rules out generic Ethernet/Wi-Fi.
$candidates=@()
$adapters=@(Get-NetAdapter -ErrorAction Stop | Where-Object {
  $_.Status -eq 'Up' -and $_.InterfaceDescription -match 'RNDIS|USB.*Ethernet|Remote NDIS|USB NCM|CDC.NCM'
})
foreach ($adapter in $adapters) {
  $ips=@(Get-NetIPAddress -InterfaceIndex $adapter.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object {$_.IPAddress -match '^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)' -and $_.PrefixLength -ge 16 -and $_.PrefixLength -le 30})
  if ($ips.Count -eq 1) { $candidates+=@{Alias=$adapter.Name; IPv4=$ips[0].IPAddress} }
}
if ($candidates.Count -ne 1) {
  throw "No unique Android USB tether interface found ($($candidates.Count) found). Connect phone, enable USB tethering, and ensure there is only one matching adapter."
}
$target=$candidates[0]
$existing=Get-NetFirewallRule -Name $Name -ErrorAction SilentlyContinue
if ($existing) {
  # Do not silently assume a same-name rule is properly scoped. Replace only this exact name.
  $existing | Remove-NetFirewallRule -ErrorAction Stop
}
try {
  New-NetFirewallRule -Name $Name -DisplayName $Display -Enabled True -Action Allow -Direction Inbound `
      -Protocol TCP -LocalPort 8766 -Profile Any -InterfaceAlias $target.Alias `
      -RemoteAddress LocalSubnet -ErrorAction Stop | Out-Null
  $rule=Get-NetFirewallRule -Name $Name -ErrorAction Stop
  $portFilter=$rule | Get-NetFirewallPortFilter
  $addressFilter=$rule | Get-NetFirewallAddressFilter
  $interfaceFilter=$rule | Get-NetFirewallInterfaceFilter
  if ($portFilter.LocalPort -ne '8766' -or $addressFilter.RemoteAddress -notcontains 'LocalSubnet' -or
      $interfaceFilter.InterfaceAlias -notcontains $target.Alias) {
    throw 'Read-back of firewall rule does not match restricted USB interface'
  }
  Write-Host "USB-ONLY firewall rule installed for $($target.Alias), $($target.IPv4), TCP 8766."
  Write-Host 'No public Internet interface was opened. No Windows network profile was changed.'
} catch {
  Get-NetFirewallRule -Name $Name -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue
  throw
}