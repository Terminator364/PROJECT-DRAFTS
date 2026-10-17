import sys,unittest,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'continuity'))
import resume
class TestSingleResume(unittest.TestCase):
 def test_checkpoint_and_journal(self):
  out=resume.preflight();self.assertEqual(out['trigger'],'Moteur/continue');self.assertGreaterEqual(out['journal_events'],89)
 def test_latest_h3_not_old_zip(self):
  out=resume.preflight();self.assertEqual(out['checkpoint_stage'],14)
 def test_next_action_not_just_status(self):
  out=resume.preflight();self.assertEqual(out['next_execution'],'H4_CLOSE_22_MECHANISTIC_GAPS');self.assertIn('Ouvrir',out['first_action'])
 def test_context_verbatims_saved(self):
  content=(ROOT/'CONTEXTE_INTEGRAL/REGISTRE_MESSAGES.jsonl').read_text(encoding='utf8');self.assertIn('Papa je veux un seul code',content);self.assertIn('CONTINUELEMENT',content)
 def test_scientific_truth_kept(self):
  d=json.loads((ROOT/'CHECKPOINT.json').read_text());self.assertEqual(d['scientific']['real_rice_trials'],0);self.assertIsNone(d['scientific']['calibrated_ic'])
 def test_only_one_active_code(self):
  d=json.loads((ROOT/'continuity/NEXT_ACTION.json').read_text());self.assertEqual(d['canonical_trigger'],'Moteur/continue')
if __name__=='__main__':unittest.main()
