import unittest,json,sys,copy,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step25'))
from q_measurement_contract import propose,validate_proposal,ContractError,TARGETS,PRIORITY
from trial_prep import build_empty_template,check_template,dry_run_gate,check_synthetic_rejected,PrepError

class Step25Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.draft=json.loads((ROOT/'step20/PROTOCOLE_Q_14_SORTIES_DRAFT.json').read_text(encoding='utf8'))
  cls.priority=json.loads((ROOT/'step21/PRIORITY_CONFIRMED_NO_WEIGHTS.json').read_text(encoding='utf8'))
  cls.packet=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text(encoding='utf8'))
  cls.q=propose(cls.draft,cls.priority)
 def test_01(self):self.assertTrue(validate_proposal(self.q))
 def test_02(self):self.assertEqual(self.q['user_confirmed_only']['priority_tier'],PRIORITY)
 def test_03(self):self.assertEqual(set(self.q['rubrics']),set(TARGETS))
 def test_04(self):self.assertEqual(len(self.q['rubrics']),14)
 def test_05(self):self.assertIsNone(self.q['Q_score_formula'])
 def test_06(self):self.assertIsNone(self.q['Q_numerical_weights'])
 def test_07(self):self.assertFalse(self.q['approved_by_user'])
 def test_08(self):self.assertIsNone(self.q['scientific_ic_percent'])
 def test_09(self):self.assertEqual(self.q['real_trials_count'],0)
 def test_10(self):self.assertEqual(self.q['rubrics']['099']['category'],'food_safety_separate')
 def test_11(self):self.assertEqual(self.q['rubrics']['112']['category'],'label_only')
 def test_12(self):self.assertEqual(self.q['rubrics']['101']['category'],'priority_ordinal')
 def test_13(self):self.assertEqual(self.q['rubrics']['102']['category'],'priority_fraction')
 def test_14(self):self.assertEqual(len(self.q['candidate_decision_structures']),2)
 def test_15(self):
  x=copy.deepcopy(self.q);x['Q_score_formula']='sum(coefficients)'
  with self.assertRaises(ContractError):validate_proposal(x)
 def test_16(self):
  x=copy.deepcopy(self.q);x['approved_by_user']=True
  with self.assertRaises(ContractError):validate_proposal(x)
 def test_17(self):
  x=copy.deepcopy(self.q);x['rubrics']['101']['field_value']=4
  with self.assertRaises(ContractError):validate_proposal(x)
 def test_18(self):
  x=copy.deepcopy(self.q);x['rubrics'].pop('099')
  with self.assertRaises(ContractError):validate_proposal(x)
 def test_19(self):
  x=copy.deepcopy(self.draft);x['approved_by_user']=True
  with self.assertRaises(ContractError):propose(x,self.priority)
 def test_20(self):
  x=copy.deepcopy(self.priority);x['numerical_weights']={'101':0.5}
  with self.assertRaises(ContractError):propose(self.draft,x)
 def test_21(self):
  t=build_empty_template(self.q);self.assertTrue(check_template(t))
 def test_22(self):
  t=build_empty_template(self.q);self.assertEqual(len(t['poststart']['measurements']),14)
 def test_23(self):
  t=build_empty_template(self.q);self.assertIsNone(t['prestart']['freeze_utc'])
 def test_24(self):
  t=build_empty_template(self.q);self.assertIsNone(t['poststart']['measurements']['102']['observation'])
 def test_25(self):
  t=build_empty_template(self.q);t['poststart']['measurements']['101']['observation']=4
  with self.assertRaises(PrepError):check_template(t)
 def test_26(self):
  t=build_empty_template(self.q);t['source_class']='REAL_OBSERVATION'
  with self.assertRaises(PrepError):check_template(t)
 def test_27(self):
  t=build_empty_template(self.q);t['scientific_ic_percent']=67.5
  with self.assertRaises(PrepError):check_template(t)
 def test_28(self):self.assertTrue(check_synthetic_rejected(self.packet)['synthetic_pretending_real_rejected'])
 def test_29(self):self.assertEqual(dry_run_gate(self.priority,self.draft)['eligible_real_paired_trials'],0)
 def test_30(self):self.assertFalse(dry_run_gate(self.priority,self.draft)['calibration_allowed_now'])
 def test_31(self):self.assertIsNone(dry_run_gate(self.priority,self.draft)['scientific_ic_percent'])
 def test_32(self):self.assertIn('Q_SCORING_NOT_PREREGISTERED_OR_USER_APPROVED',dry_run_gate(self.priority,self.draft)['blocking_reasons'])
 def test_33(self):
  x=copy.deepcopy(self.q);x['candidate_decision_structures'][0]['numeric_Q_formula']='0.5*x'
  with self.assertRaises(ContractError):validate_proposal(x)
 def test_34(self):
  x=copy.deepcopy(self.q);x['rubrics']['099']['category']='secondary_sensory'
  with self.assertRaises(ContractError):validate_proposal(x)
 def test_35(self):
  x=copy.deepcopy(self.q);x['user_confirmed_only']['priority_tier']=['108','101']
  with self.assertRaises(ContractError):validate_proposal(x)
 def test_36(self):
  t=build_empty_template(self.q);t['poststart']['measurements'].pop('112')
  with self.assertRaises(PrepError):check_template(t)
if __name__=='__main__':unittest.main()
