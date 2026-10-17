import json, sys,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'continuity'))
import audit_trail as a
class ContextDurabilityTests(unittest.TestCase):
 def test_existing_journal_sha_chain(self):self.assertTrue(a.check()['journal_chain_valid'])
 def test_context_contiguous(self):self.assertGreaterEqual(a.check()['context_rows'],33)
 def test_sha_exact_unicode(self):self.assertEqual(a.text_sha('é'),__import__('hashlib').sha256('é'.encode('utf8')).hexdigest())
 def test_fence_does_not_leak(self):self.assertGreater(len(a._fence('````')),4)
 def test_validate_unsupported_role(self):
  with self.assertRaises(ValueError):a.capture('message','SYSTEM')
 def test_validate_empty_text(self):
  with self.assertRaises(ValueError):a.capture(' ','USER')
 def test_prohibit_mistagging_user(self):
  with self.assertRaises(ValueError):a.capture('ok','USER',kind='TESTED')
 def test_validate_date(self):
  with self.assertRaises(ValueError):a.capture('ok','USER',date='tomorrow')
if __name__=='__main__':unittest.main()
