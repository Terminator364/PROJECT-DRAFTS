import unittest,sys,json,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step21'))
from quality_priority import *
class T(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.source=json.loads((ROOT/'step20/PROTOCOLE_Q_14_SORTIES_DRAFT.json').read_text(encoding='utf8'))
 def test_01(self):self.assertTrue(validate(contract_from_step20(self.source)))
 def test_02(self):self.assertEqual(contract_from_step20(self.source)['priority_tier_1_ids'],['101','102'])
 def test_03(self):self.assertIsNone(contract_from_step20(self.source)['numerical_weights'])
 def test_04(self):self.assertIsNone(contract_from_step20(self.source)['Q_score_formula'])
 def test_05(self):self.assertFalse(contract_from_step20(self.source)['calibration_training_allowed'])
 def test_06(self):self.assertEqual(len(TARGETS),14)
 def test_07(self):
  x=contract_from_step20(self.source);x['numerical_weights']={'101':0.55}
  with self.assertRaises(QualityContractError):validate(x)
 def test_08(self):
  x=contract_from_step20(self.source);x['priority_tier_1_ids']=['108','102']
  with self.assertRaises(QualityContractError):validate(x)
 def test_09(self):
  x=copy.deepcopy(self.source);x['Q_score_formula']='sum(weights)'
  with self.assertRaises(QualityContractError):contract_from_step20(x)
 def test_10(self):self.assertEqual(contract_from_step20(self.source)['Q_threshold_from_user'],85)
if __name__=='__main__':unittest.main()
