# Read-only Windows/USB diagnostic for MBMPC; does not configure networking or services.
$ErrorActionPreference = "Continue"
$report = [ordered]@{
    schema = "usb-rescue-windows-readonly-probe/1"
    utc = (Get-Date).ToUniversalTime().ToString("o")
    computer = $env:COMPUTERNAME
    powershell = $PSVersionTable.PSVersion.ToString()
    usb = @()
    adapters = @()
    desktop_commander = @()
    bcp_processes = @()
    firewall_changed = $false
    service_changed = $false
}
try {
    $report.usb = @(Get-PnpDevice -Class USB -ErrorAction Stop | Select-Object -First 35 FriendlyName, Status, Class)
} catch {
    $report.usb_error = $_.Exception.Message
}
try {
    $report.adapters = @(Get-NetAdapter -ErrorAction Stop | Select-Object -First 30 Name, InterfaceDescription, Status, LinkSpeed)
} catch {
    $report.network_error = $_.Exception.Message
}
try {
    $report.desktop_commander = @(Get-Process -ErrorAction Stop | Where-Object { $_.ProcessName -match "desktop.commander|desktopcommander" } | Select-Object ProcessName, Id)
    $report.bcp_processes = @(Get-Process -ErrorAction Stop | Where-Object { $_.ProcessName -match "bcp" } | Select-Object ProcessName, Id)
} catch {
    $report.process_error = $_.Exception.Message
}
$report | ConvertTo-Json -Depth 6
