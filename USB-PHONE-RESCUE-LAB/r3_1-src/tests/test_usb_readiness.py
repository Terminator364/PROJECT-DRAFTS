"""Contracts of the Windows USB adapter/firewall helper. STATIC only, never field validation."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
WIN=ROOT/'windows'
JAVA=ROOT/'android/app/src/main/java/com/blessing/rescuebridge'

class UsbReadinessContracts(unittest.TestCase):
    def test_read_only_diagnostic_does_not_change_windows(self):
        script=(WIN/'Usb-Readiness.ps1').read_text()
        for token in ('Get-NetAdapter','Get-NetTCPConnection','Get-NetFirewallRule','Get-ScheduledTask','USB_READINESS_READ_ONLY'):
            self.assertIn(token,script)
        for banned in ('New-NetFirewallRule','Set-NetConnectionProfile','Disable-NetFirewallRule','Remove-NetFirewallRule','Start-Process'):
            self.assertNotIn(banned,script)

    def test_narrow_only_with_genuine_usb_adapter(self):
        script=(WIN/'Fix-UsbFirewall.ps1').read_text()
        self.assertIn('RNDIS|USB.*Ethernet|Remote NDIS|USB NCM|CDC.NCM',script)
        self.assertIn('if ($candidates.Count -ne 1)',script)
        self.assertIn('-InterfaceAlias $target.Alias',script)
        self.assertIn('-RemoteAddress LocalSubnet',script)
        self.assertIn('-LocalPort 8766',script)
        self.assertIn('if ($Port -ne 8766)',script)
        self.assertNotIn('Set-NetConnectionProfile',script)
        self.assertNotIn('-RemoteAddress Any',script)
        self.assertIn('Get-NetFirewallInterfaceFilter',script)
        self.assertIn('if ($Undo)',script)
        self.assertIn('Remove-NetFirewallRule',script)
        self.assertIn('WindowsBuiltInRole]::Administrator',script)

    def test_uac_only_user_initiated(self):
        launch=(WIN/'Request-UsbFirewall.ps1').read_text()
        self.assertIn('-Verb RunAs',launch)
        self.assertIn('Fix-UsbFirewall.ps1',launch)
        self.assertIn('FIX-USB-FIREWALL.cmd',(WIN/'Install-Rescue.ps1').read_text())
        for source in ('Install-Rescue.ps1','Start-Bridge.ps1'):
            code=(WIN/source).read_text()
            self.assertNotIn('New-NetFirewallRule',code)
            self.assertNotIn('Fix-UsbFirewall.ps1 -',code)

    def test_installer_copies_both_firewall_and_diagnostics(self):
        inst=(WIN/'Install-Rescue.ps1').read_text()
        required=['Fix-UsbFirewall.ps1','Request-UsbFirewall.ps1','FIX-USB-FIREWALL.cmd',
                  'REMOVE-USB-FIREWALL.cmd','Usb-Readiness.ps1','USB-READINESS.cmd']
        for x in required: self.assertIn(x,inst)
        self.assertIn('Usb-Readiness.ps1',(WIN/'DIAGNOSTIC.cmd').read_text())

    def test_human_diagnostic_compiles_and_understands_firewall(self):
        src=(JAVA/'RescueAdvisor.java').read_text()
        self.assertIn('USB_FIREWALL_POSSIBLE',src)
        self.assertIn('ConnectException',src)
        self.assertIn('USB-READINESS.cmd',src)
        with tempfile.TemporaryDirectory() as folder:
            harness=Path(folder)/'Probe.java'
            harness.write_text('import com.blessing.rescuebridge.RescueAdvisor; public class Probe {'
             'public static void main(String[] x) { '
             'if (!RescueAdvisor.codeForException("ConnectException").equals("USB_FIREWALL_POSSIBLE")) throw new RuntimeException();'
             'if (!RescueAdvisor.problem("USB_FIREWALL_POSSIBLE").contains("Windows")) throw new RuntimeException();'
             'System.out.println("FIREWALL GUIDE PASS");}}',encoding='utf-8')
            r=subprocess.run(['javac','-encoding','UTF-8','-d',folder,str(JAVA/'RescueAdvisor.java'),str(harness)],capture_output=True,text=True,timeout=25)
            self.assertEqual(0,r.returncode,r.stderr)
            r=subprocess.run(['java','-cp',folder,'Probe'],capture_output=True,text=True,timeout=15)
            self.assertEqual(0,r.returncode,r.stderr)
            self.assertIn('FIREWALL GUIDE PASS',r.stdout)

    def test_update_identity_bumps_monotonically(self):
        gradle=(ROOT/'android/app/build.gradle').read_text()
        self.assertIn("applicationId 'com.blessing.rescuebridge'",gradle)
        self.assertIn('versionCode 3',gradle)

if __name__=='__main__': unittest.main()