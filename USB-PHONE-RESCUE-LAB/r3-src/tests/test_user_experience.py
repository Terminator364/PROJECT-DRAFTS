"""UX-oriented source contracts + real JVM diagnostic checks; no Android Emulator claim."""
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JAVA=ROOT/'android/app/src/main/java/com/blessing/rescuebridge'

class UserExperienceContracts(unittest.TestCase):
    def test_jvm_diagnostic_guide(self):
        with tempfile.TemporaryDirectory() as work:
            srcs=[JAVA/'RescueAdvisor.java',ROOT/'tests/java/RescueAdvisorProbe.java']
            result=subprocess.run(['javac','-encoding','UTF-8','-d',work,*map(str,srcs)],capture_output=True,text=True,timeout=25)
            self.assertEqual(0,result.returncode,result.stderr)
            result=subprocess.run(['java','-cp',work,'RescueAdvisorProbe'],capture_output=True,text=True,timeout=10)
            self.assertEqual(0,result.returncode,result.stderr)
            self.assertIn('9 ADVISOR CHECKS PASS',result.stdout)
    def test_jvm_local_interface_inspector_build(self):
        with tempfile.TemporaryDirectory() as work:
            result=subprocess.run(['javac','-encoding','UTF-8','-d',work,str(JAVA/'LocalLinkInspector.java')],capture_output=True,text=True,timeout=25)
            self.assertEqual(0,result.returncode,result.stderr)
    def test_four_human_facing_tabs(self):
        t=(JAVA/'MainActivity.java').read_text()
        for label in ('"Accueil"','"Missions"','"Fichiers"','"Réglages"'):
            self.assertIn(label,t)
        self.assertIn('new LinearLayout.LayoutParams(0,-2,1)',t)
        self.assertIn('ScrollView scroll=new ScrollView(this)',t)
    def test_one_diagnostic_primary_action(self):
        t=(JAVA/'MainActivity.java').read_text()
        self.assertIn('"Diagnostiquer maintenant"',t)
        self.assertIn('"Configurer mon PC"',t)
        self.assertIn('showScreen("SETTINGS")',t)
    def test_foreground_only_heartbeat(self):
        t=(JAVA/'MainActivity.java').read_text()
        self.assertIn('if(!visible)return;',t)
        self.assertIn('mainHandler.removeCallbacks(foregroundCheck)',t)
        self.assertIn('mainHandler.postDelayed(this,60000)',t)
    def test_no_fabricated_usb_success(self):
        t=(JAVA/'MainActivity.java').read_text()
        self.assertIn('LocalLinkInspector.summary()',t)
        self.assertIn('BridgeClient client',t)
        self.assertIn('JSONObject result=client.perform(path,payload)',t)
        self.assertIn('"PC joignable"',t)
    def test_android_identity_is_update_compatible(self):
        gradle=(ROOT/'android/app/build.gradle').read_text()
        manifest=(ROOT/'android/app/src/main/AndroidManifest.xml').read_text()
        self.assertIn("applicationId 'com.blessing.rescuebridge'",gradle)
        self.assertRegex(gradle,r'versionCode\s+2\b')
        self.assertIn('android:allowBackup="false"',manifest)
        self.assertIn('android:usesCleartextTraffic="true"',manifest)
    def test_no_arbitrary_shell(self):
        t=(JAVA/'MainActivity.java').read_text()
        self.assertIn('MissionPolicy.actionAllowed(action)',t)
        self.assertIn('payload.remove("approved")',t)
        self.assertNotIn('Runtime.getRuntime().exec(',t)
        self.assertNotIn('ProcessBuilder(',t)
    def test_windows_agent_remains_bounded(self):
        source=(ROOT/'windows/bridge_agent.py').read_text()
        self.assertIn('approved',source)
        self.assertNotIn('shell=True',source)
        self.assertNotIn('subprocess.Popen',source)
    def test_screen_does_not_ask_user_for_every_debug_detail_at_home(self):
        t=(JAVA/'MainActivity.java').read_text()
        home=t.split('private View buildHome()')[1].split('private View buildMissions()')[0]
        self.assertNotIn('SecurePairingStore',home)
        self.assertNotIn('EditText',home)
        self.assertIn('"Mon ordinateur"',home)

if __name__ == '__main__': unittest.main()