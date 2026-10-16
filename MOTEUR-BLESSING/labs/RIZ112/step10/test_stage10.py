import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step10'))
from ic_integrity_v10 import audited_simulate,digest
from case_intervention_audit import run
P=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text())
AUD=json.loads((ROOT/'step10/INTERVENTIONS_112_STAGE9.json').read_text())
GATE=json.loads((ROOT/'step10/GATE_V10.json').read_text())
class Stage10(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.v=audited_simulate(P,draws=100)
 def test_01_demo_still_available(self): self.assertEqual(self.v['status'],'DEMONSTRATION_ASSUMPTIONS_ONLY_NOT_REAL_Q')
 def test_02_real_IC_stays_null(self):self.assertIsNone(self.v['scientific_ic_percent'])
 def test_03_gated_14(self):self.assertEqual(self.v['target_integrity']['frozen_target_cases_checked'],14)
 def test_04_no_future_data(self):self.assertEqual(self.v['target_integrity']['future_labels_as_predictors'],0)
 def test_05_all_targets_veto_on_change(self):
  for key in P['target_contract']:
   cp=copy.deepcopy(P);cp['target_contract'][key]['measurement_definition']='different hypothetical target'
   v=audited_simulate(cp,draws=100)
   self.assertEqual(v['status'],'ABSTAIN_TARGET_CONTRACT_CHANGED',key)
   self.assertIsNone(v['ic_demo_percent'],key)
 def test_06_refuse_missing_target(self):
  cp=copy.deepcopy(P);cp['target_contract']['102']['status']='UNDEFINED';cp['target_contract']['102']['measurement_definition']=None
  self.assertEqual(audited_simulate(cp,draws=100)['status'],'ABSTAIN_TARGET_CONTRACT_CHANGED')
 def test_07_digest_pin(self):self.assertEqual(digest(P['target_contract']),GATE['demo_quality_target_sha256'])
 def test_08_refuse_fake_approval(self):
  c=copy.deepcopy(GATE);c['scientific_approval']=True
  with self.assertRaises(ValueError):audited_simulate(P,contract=c,draws=100)
 def test_09_audit_covers_112(self):self.assertEqual(AUD['counts']['cases'],112)
 def test_10_no_missing_intervention(self):self.assertEqual(AUD['counts']['mutations_failed'],0)
 def test_11_11_numeric_delta(self):self.assertEqual(AUD['counts']['statuses']['IC_CHANGED'],11)
 def test_12_5_existing_abstentions(self):self.assertEqual(AUD['counts']['statuses']['ABSTAIN'],5)
 def test_13_target_never_numeric_in_v9(self):
  xs=[x for x in AUD['cases'] if x['intervention_role']=='TARGET_SPEC_INTERVENTION']
  self.assertEqual(len(xs),14);self.assertTrue(all(x['status']=='IC_UNCHANGED' for x in xs))
 def test_14_action_never_numeric_in_v9(self):
  xs=[x for x in AUD['cases'] if x['intervention_role']=='PLAN_INTERVENTION']
  self.assertEqual(len(xs),37);self.assertTrue(all(x['status']=='IC_UNCHANGED' for x in xs))
 def test_15_policy_never_numeric_in_v9(self):
  xs=[x for x in AUD['cases'] if x['intervention_role']=='POLICY_INTERVENTION']
  self.assertEqual(len(xs),13);self.assertTrue(all(x['status']=='IC_UNCHANGED' for x in xs))
 def test_16_nonmutable_derivations(self):self.assertEqual(AUD['counts']['statuses']['DERIVED_COMPUTED_ONLY'],4)
 def test_17_no_real_trials(self):self.assertTrue(all(x['scientific_ic'] is None for x in AUD['cases']))
 def test_18_original_a_values(self):self.assertEqual(self.v['ic_demo_percent'],67.0) # 100-draw MC noise distinct from published 3000 draws
 def test_19_changed_target_version_abstains(self):
  cp=copy.deepcopy(P);cp['target_contract']['112']['protocol_reference']+='-v2'
  self.assertIsNone(audited_simulate(cp,draws=100)['ic_demo_percent'])
 def test_20_uncertainty_still_marked(self):self.assertFalse(self.v['target_integrity']['scientific_approval'])
if __name__=='__main__':unittest.main()
