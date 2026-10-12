import ast
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('setup_pc',ROOT/'setup_pc.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class SetupContract(unittest.TestCase):
    def test_syntax_and_entrypoint(self):
        ast.parse((ROOT/'setup_pc.py').read_text(encoding='utf-8'))
        self.assertTrue(callable(mod.cli_self_test))
    def test_port_matches_android(self):
        self.assertEqual(8766,mod.PORT)
    def test_bundle_requires_agent_binary(self):
        self.assertIn('bridge_agent.exe',mod.REQUIRED)
    def test_missing_binary_causes_failure(self):
        self.assertFalse(mod.validate_payload()[0])
    def test_ip_zero(self):
        self.assertIsNone(mod.pick_ip({}))
    def test_ip_one(self):
        self.assertEqual('192.168.42.19',mod.pick_ip({'usb_adapters':[{'ip':'192.168.42.19'}]}))
    def test_ip_multiple_needs_operator(self):
        self.assertIsNone(mod.pick_ip({'usb_adapters':[{'ip':'192.168.1.1'},{'ip':'192.168.2.1'}]}))
    def test_source_command_no_auto_firewall(self):
        s=(ROOT/'windows'/'Install-Rescue.ps1').read_text(encoding='utf-8')
        self.assertNotIn('New-NetFirewallRule',s)
        self.assertIn('bridge_agent.exe',s)
    def test_guardian_prefers_bundled_agent(self):
        s=(ROOT/'windows'/'Start-Bridge.ps1').read_text(encoding='utf-8')
        self.assertIn('$bundled',s)
        self.assertIn('AgentExe',s)
        self.assertIn('Start-Process',s)
    def test_key_is_not_automatically_uploaded(self):
        s=(ROOT/'setup_pc.py').read_text(encoding='utf-8')
        self.assertNotIn('requests.post',s)
        self.assertIn('secrets.token_hex(32)',s)

if __name__ == '__main__':unittest.main()