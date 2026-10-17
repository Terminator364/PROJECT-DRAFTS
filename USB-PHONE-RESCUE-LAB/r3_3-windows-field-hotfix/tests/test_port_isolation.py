"""Regression: USB Rescue may not reuse BCP TLS proxy ports or claim someone else's listener."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def source(rel): return (ROOT/rel).read_text(encoding="utf-8")
class PortIsolation(unittest.TestCase):
    def test_android_and_windows_private_ports_agree(self):
        protocol=source("android/app/src/main/java/com/blessing/rescuebridge/UsbDiscoveryProtocol.java")
        reverse=source("android/app/src/main/java/com/blessing/rescuebridge/UsbReverseLink.java")
        windows=source("windows/bridge_agent.py")
        guardian=source("windows/Start-Bridge.ps1")
        self.assertIn("AGENT_PORT=8876",protocol)
        self.assertIn("PORT=8767",protocol)
        self.assertIn("PORT=8768",reverse)
        self.assertIn("DISCOVERY_PORT = 8767",windows)
        self.assertIn("REVERSE_PORT = 8768",windows)
        self.assertIn("[int]$Port = 8876",guardian)
        self.assertNotIn("8766",protocol)
        self.assertNotIn("8766",guardian)
    def test_readiness_uses_ownership_not_just_any_listener(self):
        code=source("windows/Usb-Readiness.ps1")
        self.assertIn("Get-NetTCPConnection -LocalPort 8876",code)
        self.assertIn("Get-CimInstance Win32_Process",code)
        self.assertIn("owner.CommandLine",code)
        self.assertIn("agent_listener_found=[bool]$agentListener",code)
        self.assertNotIn("agent_listener_found=[bool]$listener",code)
    def test_firewall_never_opens_general_wifi(self):
        code=source("windows/Fix-UsbFirewall.ps1")
        self.assertIn("-LocalPort 8876",code)
        self.assertIn("-RemoteAddress LocalSubnet",code)
        self.assertNotIn("-RemoteAddress Any",code)
        self.assertNotIn("Set-NetConnectionProfile",code)
if __name__=="__main__": unittest.main()