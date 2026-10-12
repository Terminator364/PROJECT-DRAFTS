"""JVM-executed mission gate, not merely an Android Java syntax check."""
import subprocess
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class MissionPolicyTests(unittest.TestCase):
    def test_exact_jvm_mission_policy(self):
        policy=ROOT/'android/app/src/main/java/com/blessing/rescuebridge/MissionPolicy.java'
        probe=ROOT/'tests/java/MissionPolicyProbe.java'
        with tempfile.TemporaryDirectory() as work:
            build=subprocess.run(['javac','-encoding','UTF-8','-d',work,str(policy),str(probe)],capture_output=True,text=True,timeout=30)
            self.assertEqual(build.returncode,0,build.stderr)
            run=subprocess.run(['java','-cp',work,'MissionPolicyProbe'],capture_output=True,text=True,timeout=15)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertEqual(run.stdout.splitlines(),['true','false','true','false','false','true','false','false','false','true','false'])
    def test_ui_connects_policy_and_android_file_picker(self):
        ui=(ROOT/'android/app/src/main/java/com/blessing/rescuebridge/MainActivity.java').read_text()
        for required in ('Intent.ACTION_OPEN_DOCUMENT','PICK_MISSION_JSON','MissionPolicy.actionAllowed',
                         'MissionPolicy.validExpiry','MissionPolicy.safeRelativePath',
                         'MissionPolicy.validWriteContent','payload.remove("approved")',
                         'Partager dernier resultat'):
            self.assertIn(required,ui)

if __name__=='__main__':unittest.main()