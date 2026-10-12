"""Portable mission-file generator contract."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools_mission_generator import build

class MissionGeneratorTests(unittest.TestCase):
    def test_diagnostics_with_expiration(self):
        x=build('diagnostics',minutes=15,now=1700000000)
        self.assertEqual('bcp-rescue-mission/1',x['schema'])
        self.assertEqual(1700000900,x['expires_unix_seconds'])
        self.assertEqual({},x['payload'])
    def test_no_remote_mutation(self):
        with self.assertRaises(ValueError):build('write',now=1700000000)
    def test_no_traversal(self):
        with self.assertRaises(ValueError):build('read',path='../secret.txt',now=1700000000)
    def test_read_path(self):
        self.assertEqual('test.txt',build('read',path='test.txt',now=1700000000)['payload']['path'])
if __name__=='__main__':unittest.main()