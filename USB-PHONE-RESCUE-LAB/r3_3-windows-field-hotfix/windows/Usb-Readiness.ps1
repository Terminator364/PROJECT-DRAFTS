# READ-ONLY readiness inventory, no administrator rights required.
$ErrorActionPreference='Continue'
$task=Get-ScheduledTask -TaskName 'BCP USB Rescue Guardian' -ErrorAction SilentlyContinue
$adapters=@(Get-NetAdapter -ErrorAction SilentlyContinue | Where-Object {
  $_.Status -eq 'Up' -and $_.InterfaceDescription -match 'RNDIS|USB.*Ethernet|Remote NDIS|USB NCM|CDC.NCM'
})
$candidates=@(foreach($a in $adapters) {
  $ip=Get-NetIPAddress -InterfaceIndex $a.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object {$_.IPAddress -match '^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)'}
  foreach($addr in $ip) { [pscustomobject]@{name=$a.Name; ip=$addr.IPAddress; type=$a.InterfaceDescription} }
})
$rule=Get-NetFirewallRule -Name 'BCPUsbRescueUsbOnly8876' -ErrorAction SilentlyContinue
$listeners=@(Get-NetTCPConnection -LocalPort 8876 -State Listen -ErrorAction SilentlyContinue)
$agentListener=@(foreach ($entry in $listeners) {
  $owner=Get-CimInstance Win32_Process -Filter ("ProcessId="+$entry.OwningProcess) -ErrorAction SilentlyContinue
  if ($owner -and $owner.CommandLine -match 'bridge_agent[.]py|bcp_usb_rescue_agent[.]exe' -and
      $owner.CommandLine -match 'BCP-USB-Rescue') { $entry }
})
$summary=[ordered]@{
  schema='BCP_USB_READINESS_READ_ONLY_1'
  utc=(Get-Date).ToUniversalTime().ToString('o')
  pc=$env:COMPUTERNAME
  usb_adapter_count=$candidates.Count
  usb_adapters=$candidates
  guardian_task_installed=[bool]$task
  agent_listener_found=[bool]$agentListener
  firewall_usb_rule_present=[bool]$rule
  firewall_usb_rule_matches_adapter=$false
  open_public_firewall_rule_created=$false
  corrective_action=''
}
if ($rule) {
  $iface=$rule | Get-NetFirewallInterfaceFilter -ErrorAction SilentlyContinue
  $summary.firewall_usb_rule_matches_adapter=(@($candidates | Where-Object { $_.name -in $iface.InterfaceAlias }).Count -ge 1)
}
if ($candidates.Count -eq 0) { $summary.corrective_action='Brancher un cable USB de donnees et activer Partage USB dans Android.' }
elseif ($candidates.Count -gt 1) { $summary.corrective_action='Plusieurs interfaces USB candidates. Desactiver les autres ou demander une verification manuelle.' }
elseif (-not $agentListener) { $summary.corrective_action='Lancer START-NOW.cmd ou verifier la tache BCP USB Rescue Guardian.' }
elseif (-not $summary.firewall_usb_rule_matches_adapter) { $summary.corrective_action='Si le telephone ne se connecte pas, executer FIX-USB-FIREWALL.cmd avec accord Windows.' }
else { $summary.corrective_action='Reseau USB et agent detectes localement : lancer le diagnostic depuis le telephone pour prouver le bout en bout.' }
$summary | ConvertTo-Json -Depth 8