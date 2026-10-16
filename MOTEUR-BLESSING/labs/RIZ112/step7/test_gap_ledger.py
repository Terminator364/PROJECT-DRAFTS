import json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class TestGaps(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  subprocess.run([sys.executable,str(ROOT/'step7/build_stage7.py')],cwd=ROOT,capture_output=True,text=True,check=True)
  cls.rows=json.loads((ROOT/'step7/GAPS_112_V7.json').read_text(encoding='utf8'))['cases']
 def test_exact_112_unique(self):self.assertEqual({r['id'] for r in self.rows},{f'{x:03}' for x in range(1,113)})
 def test_each_case_has_documented_next_step(self):self.assertTrue(all(r['next_step'] for r in self.rows))
 def test_14_targets_not_features(self):self.assertEqual(sum(r['role_input_contract']=='POSTSTART_LABEL_NOT_PRESTART_INPUT' for r in self.rows),14)
 def test_numeric_orphans_are_not_concealed(self):
  self.assertEqual({r['id'] for r in self.rows if r['physical_numeric_path_toy_only'] and not r['reaches_final_Q112_in_declarative_graph']},{'014','037','038','043'})
 def test_never_claim_empirically_validated_Q(self):self.assertFalse(any(r['empirical_effect_on_Q_validated'] for r in self.rows))
if __name__=='__main__':unittest.main()
