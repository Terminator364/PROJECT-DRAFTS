import unittest,sys,json,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'step24'))
from interaction_matrix import *
class InteractionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=json.loads((R/'step6/examples/A_couvercle_ajuste_112.json').read_text(encoding='utf8'))
  cls.a=json.loads((R/'step20/ASSUMPTIONS_SYNTHETIQUES_NON_CALIBREES.json').read_text(encoding='utf8'))
  cls.x=interaction_audit(cls.p,cls.a)
 def test_01(self):self.assertEqual(self.x['pair_count'],36)
 def test_02(self):self.assertEqual(len(self.x['active_physical_primitives']),9)
 def test_03(self):self.assertEqual(len(set(tuple(x['pair']) for x in self.x['tested_interactions'])),36)
 def test_04(self):self.assertTrue(self.x['nonadditive_physics_pairs']>=1)
 def test_05(self):self.assertEqual(self.x['real_Q_effects_proven'],0)
 def test_06(self):self.assertIsNone(self.x['scientific_IC_percent'])
 def test_07(self):self.assertTrue(all(x['Q_effect_verified']==False for x in self.x['tested_interactions']))
 def test_08(self):
  with self.assertRaises(PhysicalEvidenceError):interaction_audit(self.p,self.a,fraction=0.5)
 def test_09(self):
  with self.assertRaises(PhysicalEvidenceError):interaction_audit(self.p,self.a,fraction=float('nan'))
 def test_10(self):
  with self.assertRaises(PhysicalEvidenceError):interaction_audit(self.p,self.a,fraction=True)
 def test_11(self):
  p=copy.deepcopy(self.p);p['case_inputs']['035']['value']=500
  with self.assertRaises(PhysicalEvidenceError):interaction_audit(p,self.a)
 def test_12(self):
  self.assertTrue(all('scientific_IC_delta_percent' not in r or r['scientific_IC_delta_percent'] is None for r in self.x['tested_interactions']))
 def test_13(self):
  self.assertEqual(self.x['nonadditive_physics_pairs']+self.x['no_nonadditivity_at_test_point'],36)
if __name__=='__main__':unittest.main()
