from pathlib import Path
import unittest,sys,json,copy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from build_register_112 import build
read=lambda p:json.loads((ROOT/p).read_text(encoding='utf8'))
class RegisterChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.out=build(read('step6/examples/A_couvercle_ajuste_112.json'),read('step20/ASSUMPTIONS_SYNTHETIQUES_NON_CALIBREES.json'),read('reference/step4/CATALOGUE_112_ROLES_ETAPE4.json'),read('step17/RAPPORT_112_INFLUENCES_DEMO_20261017.json'))
 def test_01_112_exactly(self):self.assertEqual(self.out['rubrics_total'],112)
 def test_02_no_duplicate_ids(self):self.assertEqual(len(set(x['rubric'] for x in self.out['rows'])),112)
 def test_03_nine_physics(self):self.assertEqual(self.out['physical_intermediate_tested'],9)
 def test_04_nine_responses(self):self.assertEqual(self.out['physical_responded'],9)
 def test_05_fourteen_outputs(self):self.assertEqual(self.out['outcome_only'],14)
 def test_06_rest_unpromoted(self):self.assertEqual(self.out['additional_rubrics_without_new_physical_proof'],89)
 def test_07_no_quality_weights(self):self.assertTrue(self.out['no_assumed_112_quality_weights'])
 def test_08_real_q_null(self):self.assertIsNone(self.out['scientific_ic_percent'])
 def test_09_all_rows_unproven_q(self):self.assertTrue(all(not x['real_quality_effect_validated'] for x in self.out['rows']))
 def test_10_all_rows_no_fake_percent(self):self.assertTrue(all(x['scientific_ic_delta_percent'] is None for x in self.out['rows']))
 def test_11_all_target_role(self):
  self.assertTrue(all(next(x for x in self.out['rows'] if x['rubric']==f'{i:03}')['step20_evidence_status']=='OUTCOME_ONLY_NO_PRET0_INTERVENTION' for i in range(99,113)))
 def test_12_prev_effect_retained(self):self.assertTrue(all('original_step17_effect_on_Q' in x for x in self.out['rows']))
if __name__=='__main__':unittest.main()
