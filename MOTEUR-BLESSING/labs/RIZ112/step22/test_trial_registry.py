import unittest,json,sys,tempfile,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'step22'))
from trial_registry import *
class TrialTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.packet=json.loads((R/'step6/examples/A_couvercle_ajuste_112.json').read_text(encoding='utf8'))
 def pref(self,**kw):return preflight(self.packet,experiment_id='sim001',source_class='SYNTHETIC_REHEARSAL',registered_at_utc='2026-10-16T11:59:00Z',source_identifier='test_protocol',**kw)
 def test_01(self):self.assertEqual(self.pref()['real_quality_label'],None)
 def test_02(self):self.assertTrue(self.pref()['no_post_T0_leakage'])
 def test_03(self):
  with self.assertRaises(TrialError):preflight(self.packet,experiment_id='x',source_class='REAL_OBSERVATION',registered_at_utc='2026-10-16T11:00:00Z',source_identifier='test')
 def test_04(self):
  with self.assertRaises(TrialError):preflight(self.packet,experiment_id='x',source_class='SYNTHETIC_REHEARSAL',registered_at_utc='2026-10-16T12:30:00Z',source_identifier='test')
 def test_05(self):
  with self.assertRaises(TrialError):preflight(self.packet,experiment_id='bad/xx',source_class='SYNTHETIC_REHEARSAL',registered_at_utc='2026-10-16T11:30:00Z',source_identifier='test')
 def test_06(self):
  x=outcome_draft(self.pref(),observed_at_utc='2026-10-16T14:00:00Z',observations={},observer_id='raterA',source_identifier='paper');self.assertEqual(len(x['missing_target_ids']),14)
 def test_07(self):
  with self.assertRaises(TrialError):outcome_draft(self.pref(),observed_at_utc='2026-10-16T12:59:00Z',observations={},observer_id='a',source_identifier='paper')
 def test_08(self):
  with self.assertRaises(TrialError):outcome_draft(self.pref(),observed_at_utc='2026-10-16T14:00:00Z',observations={'001':{}},observer_id='a',source_identifier='paper')
 def test_09(self):
  q={'101':{'status':'NOT_MEASURED','observation':0,'unit':None,'observed_at_utc':'2026-10-16T14:00:00Z','source':None}}
  with self.assertRaises(TrialError):outcome_draft(self.pref(),observed_at_utc='2026-10-16T14:00:00Z',observations=q,observer_id='a',source_identifier='paper')
 def test_10(self):
  q={'101':{'status':'MEASURED','observation':False,'unit':'scale','observed_at_utc':'2026-10-16T14:00:00Z','source':'a'}}
  with self.assertRaises(TrialError):outcome_draft(self.pref(),observed_at_utc='2026-10-16T14:00:00Z',observations=q,observer_id='a',source_identifier='paper')
 def test_11(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'registry.jsonl';a=append_envelope(path,self.pref());self.assertEqual(a['sequence'],1);self.assertEqual(verify_chain([json.loads(path.read_text().splitlines()[0])]),a['envelope_sha256'])
 def test_12(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'registry.jsonl';append_envelope(path,self.pref());
   with self.assertRaises(TrialError):append_envelope(path,self.pref())
 def test_13(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'registry.jsonl';append_envelope(path,self.pref());s=json.loads(path.read_text().splitlines()[0]);s['payload']['source_class']='REAL_OBSERVATION'
   with self.assertRaises(TrialError):verify_chain([s])
 def test_14(self):self.assertEqual(self.pref()['source_class'],'SYNTHETIC_REHEARSAL')
if __name__=='__main__':unittest.main()
