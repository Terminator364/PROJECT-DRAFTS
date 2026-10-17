import unittest,sys,json,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'step23'))
from evidence_gate import *
class GateTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pc=json.loads((ROOT/'step21/PRIORITY_CONFIRMED_NO_WEIGHTS.json').read_text(encoding='utf8'))
  cls.q=json.loads((ROOT/'step20/PROTOCOLE_Q_14_SORTIES_DRAFT.json').read_text(encoding='utf8'))
 def check(self):return inspect_registry([],self.pc,self.q)
 def test_01(self):self.assertEqual(self.check()['eligible_real_paired_trials'],0)
 def test_02(self):self.assertFalse(self.check()['calibration_allowed_now'])
 def test_03(self):self.assertIsNone(self.check()['scientific_ic_percent'])
 def test_04(self):self.assertIn('Q_SCORING_NOT_PREREGISTERED_OR_USER_APPROVED',self.check()['blocking_reasons'])
 def test_05(self):self.assertIn('INSUFFICIENT_VERIFIABLE_REAL_TRIALS',self.check()['blocking_reasons'])
 def test_06(self):self.assertIn('CALIBRATION_AND_OUT_OF_SAMPLE_VALIDATION_NOT_RUN',self.check()['blocking_reasons'])
 def test_07(self):
  with self.assertRaises(GateError):inspect_registry([],self.pc,self.q,min_independent_real_trials=1)
 def test_08(self):self.assertEqual(self.check()['ineligible_trials'],{})
 def test_09(self):
  pc=copy.deepcopy(self.pc);pc['numerical_weights']={'101':0.8};self.assertFalse(inspect_registry([],pc,self.q)['calibration_allowed_now'])
 def test_10(self):
  q=copy.deepcopy(self.q);q['approved_by_user']=True;q['Q_score_formula']='x';self.assertFalse(inspect_registry([],self.pc,q)['preregistered_Q_approved'])
if __name__=='__main__':unittest.main()
