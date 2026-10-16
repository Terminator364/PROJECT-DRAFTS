import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "dc_oneclick_qa"))
from reconnect_contract import Proc, propose, remote_roots

OLD = [
    Proc(11952, 7860, "cmd.exe", 'cmd.exe /k npx.cmd --yes @wonderwhy-er/desktop-commander@latest remote'),
    Proc(3024, 11952, "node.exe", 'node.exe npx-cli.js --yes @wonderwhy-er/desktop-commander remote'),
    Proc(13276, 3024, "node.exe", r'node.exe C:\npm-cache\@wonderwhy-er\desktop-commander\dist\index.js remote'),
    Proc(8436, 13276, "node.exe", r'node.exe C:\npm-cache\@wonderwhy-er\desktop-commander\dist\index.js'),
]
OTHER = [
    Proc(9984, 1, "node.exe", r'node.exe C:\TLIB\tlib.mjs agent'),
    Proc(13002, 1, "node.exe", r'node.exe C:\Excellentia\server.mjs'),
    Proc(6068, 1, "node.exe", r'node.exe C:\BCP\server.mjs'),
    Proc(12345, 1, "cmd.exe", "cmd.exe /k unrelated remote monitoring"),
]

class OneClickContractTests(unittest.TestCase):
    def test_original_emergency_chain_is_one_root(self):
        self.assertEqual(remote_roots(OLD), [11952])
    def test_other_applications_never_selected(self):
        self.assertEqual(remote_roots(OTHER), [])
        self.assertEqual(remote_roots(OLD + OTHER), [11952])
    def test_verified_connected_does_not_destroy_session(self):
        p = propose(OLD + OTHER, cloud_status="ONLINE", user_clicked=True)
        self.assertEqual(p.operation, "REVEAL_EXISTING")
        self.assertTrue(p.cloud_online_verified)
    def test_unknown_state_fails_safe(self):
        p = propose(OLD, cloud_status="UNKNOWN", user_clicked=True)
        self.assertEqual(p.operation, "PRESERVE_AND_DIAGNOSE")
        self.assertFalse(p.cloud_online_verified)
    def test_explicit_offline_requires_prepare_before_stop(self):
        self.assertEqual(propose(OLD, cloud_status="OFFLINE", user_clicked=True).operation, "RESTART_AFTER_PREPARE")
    def test_after_reboot_no_process_is_boot_case(self):
        self.assertEqual(propose([], cloud_status="UNKNOWN", user_clicked=True).operation, "START_EMERGENCY_CMD")
    def test_no_automatic_kill(self):
        self.assertEqual(propose(OLD, cloud_status="OFFLINE", user_clicked=False).operation, "NOOP")
    def test_no_internet_status_guess(self):
        with self.assertRaises(ValueError):
            propose(OLD, cloud_status="ASSUMED_ONLINE", user_clicked=True)

    @unittest.skipUnless(sys.platform == "win32", "Real Windows host only")
    def test_windows_cmd_invocation_and_quoting(self):
        # Mock the COMMAND INTERPRETER contract; never contacts a live MCP channel.
        with tempfile.TemporaryDirectory(prefix="Remote CMD Space ") as folder:
            base = pathlib.Path(folder)
            bat = base / "mock-agent.cmd"
            receipt = base / "receipt.txt"
            bat.write_text(f'@echo off\r\necho CONNECTION_ATTEMPTED>\"{receipt}\"\r\nexit /b 0\r\n', encoding="utf-8")
            # The old OneClick construction used manually nested quotes:
            # cmd.exe /d /k "call \\"C:\\Program Files\\...\\session.cmd\\""
            # The first Windows QA run reproduced ERRORLEVEL 1 in that mode.
            # Pass the script path as an argument; let subprocess.list2cmdline quote it.
            out = subprocess.run(["cmd.exe", "/d", "/c", str(bat)],
                                 capture_output=True, text=True, timeout=15)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            self.assertEqual(receipt.read_text().strip(), "CONNECTION_ATTEMPTED")

if __name__ == "__main__":
    unittest.main(verbosity=2)
