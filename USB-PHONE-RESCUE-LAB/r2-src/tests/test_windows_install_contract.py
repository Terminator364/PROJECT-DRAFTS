"""Static-only protection contract; NOT execution on Windows PowerShell."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class WindowsInstallContract(unittest.TestCase):
 def test_windows_minimum_runtime_and_fail_closed_acl(self):
  ps=(ROOT/'windows/Install-Rescue.ps1').read_text()
  self.assertIn('sys.version_info >= (3,10)',ps)
  self.assertIn('SECURITY_BLOCK:',ps)
  self.assertIn("New-ScheduledTaskTrigger -AtLogOn",ps)
  self.assertNotIn('New-NetFirewallRule',ps)
 def test_guardian_retries_usb_with_log_bounds(self):
  ps=(ROOT/'windows/Start-Bridge.ps1').read_text()
  self.assertIn("$lastWaitUsbLog",ps)
  self.assertIn('2097152',ps)
  self.assertIn('sys.version_info >= (3,10)',ps)
  self.assertIn('USB_ROUTE_CHANGED',ps)
  self.assertIn('CIRCUIT_BREAKER',ps)
  self.assertNotIn('New-NetFirewallRule',ps)
if __name__=='__main__':unittest.main()