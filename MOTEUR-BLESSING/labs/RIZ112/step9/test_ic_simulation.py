from __future__ import annotations
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ic_simulation_v1 import simulate,SimulationError,proxy_scores, draw_factors
from riz112 import InvalidPacket

C=json.loads((ROOT/'step9'/'DEMONSTRATION_CONTRACT.json').read_text())
def packet(n):return json.loads((ROOT/'step6'/'examples'/f'{n}_112.json').read_text())

class TestDemo(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=packet('A_couvercle_ajuste');cls.b=packet('B_couvercle_fuyant');cls.c=packet('C_chaleur_faible')
  cls.ra=simulate(cls.a,C,1500,7);cls.rb=simulate(cls.b,C,1500,7);cls.rc=simulate(cls.c,C,1500,7)
 def test_computes_probability_three(self):
  for d in [self.ra,self.rb,self.rc]: self.assertIsInstance(d['ic_demo_percent'],float);self.assertTrue(0<=d['ic_demo_percent']<=100)
 def test_a_b_c_order(self):self.assertGreater(self.ra['ic_demo_percent'],self.rb['ic_demo_percent']);self.assertGreater(self.rb['ic_demo_percent'],self.rc['ic_demo_percent'])
 def test_not_validated(self):
  for d in [self.ra,self.rb,self.rc]:
   self.assertIsNone(d['scientific_ic_percent']);self.assertIsNone(d['real_Q_probability_percent']);self.assertFalse(d['evidence']['calibrated'])
 def test_all_112(self):self.assertEqual(self.ra['coverage']['cases_visited'],112)
 def test_all_62(self):self.assertEqual(self.ra['coverage']['d014_routes_visited'],62)
 def test_output_labels_never_features(self):
  self.assertEqual(self.ra['coverage']['poststart_consumed'],0)
  self.assertEqual(len(self.ra['coverage']['other_target_cases_not_quantified']),10)
 def test_repeat_deterministic(self):self.assertEqual(self.ra,simulate(self.a,C,1500,7))
 def test_seed_matters(self):self.assertNotEqual(self.ra['ic_demo_percent'],simulate(self.a,C,1500,8)['ic_demo_percent'])
 def test_prestart_aftercutoff_reject(self):
  p=copy.deepcopy(self.a);p['prestart']['inputs']['water_added_g']['available_at_utc']='2026-10-16T14:00:00Z'
  with self.assertRaises(InvalidPacket):simulate(p,C,100,7)
 def test_poststart_label_reject(self):
  p=copy.deepcopy(self.a);p['quality_score_100']=100
  with self.assertRaises(Exception):simulate(p,C,100,7)
 def test_conflict_abstain(self):
  p=copy.deepcopy(self.a);p['case_inputs']['013']['value']=False
  ans=simulate(p,C,100,7)
  self.assertEqual(ans['status'],'ABSTAIN_PRESTART_CONTRADICTION')
  self.assertIsNone(ans['ic_demo_percent'])
 def test_low_water_affects_prob(self):
  p=copy.deepcopy(self.a);p['prestart']['inputs']['water_added_g']['value']-=80;p['case_inputs']['035']['value']-=80
  r=simulate(p,C,500,7);self.assertLess(r['ic_demo_percent'],self.ra['ic_demo_percent'])
 def test_increased_lid_loss_affects_prob(self):
  p=copy.deepcopy(self.a);p['prestart']['inputs']['lid_multiplier']['value']*=2;p['case_inputs']['014']['value']*=2
  r=simulate(p,C,500,7);self.assertLess(r['ic_demo_percent'],self.ra['ic_demo_percent'])
 def test_invalid_contract_scales(self):
  contract=copy.deepcopy(C);contract['proxy_scales']['free_water_scale_g_per_g']=0
  with self.assertRaises(SimulationError):simulate(self.a,contract,100,7)
 def test_invalid_contract_approval(self):
  contract=copy.deepcopy(C);contract['approved_for_empirical_success']=True
  with self.assertRaises(SimulationError):simulate(self.a,contract,100,7)
 def test_missing_uncertainty(self):
  contract=copy.deepcopy(C);del contract['uncertainty_distribution']['transfer_efficiency']
  with self.assertRaises(SimulationError):simulate(self.a,contract,100,7)
 def test_small_n_rejected(self):
  with self.assertRaises(SimulationError):simulate(self.a,C,12,7)
 def test_no_arbitrary_112_sum(self):self.assertIn('minimum',self.ra['simulator']['aggregation'])
 def test_change_contract_changes_ic(self):
  c=copy.deepcopy(C);c['proxy_scales']['free_water_scale_g_per_g']=.8
  d=simulate(self.a,c,600,7);self.assertNotEqual(d['ic_demo_percent'],self.ra['ic_demo_percent'])
 def test_sampling_ci_in_bounds(self):
  for d in [self.ra,self.rb,self.rc]:
   lo,hi=d['mc_95_percent_interval_for_demo_ONLY'];self.assertTrue(0<=lo<=d['ic_demo_percent']<=hi<=100)
 def test_not_empty_calibration_evidence(self):
  self.assertEqual(self.ra['evidence']['real_labeled_preparations'],0)
 def test_proxy_threshold_in_contract(self):self.assertEqual(C['threshold_q_demo'],85)
 def test_starch_explicitly_unvalidated(self):self.assertIn('starch_102_UNVALIDATED',self.ra['baseline_dimensions_demo'])
 def test_known_unknown_separation(self):
  p=copy.deepcopy(self.a);p['case_inputs']['003']['state']='UNKNOWN';p['case_inputs']['003']['value']=None
  ans=simulate(p,C,100,7);self.assertIsNone(ans['scientific_ic_percent'])
 def test_no_future_label_in_calculation(self):self.assertEqual(self.ra['evidence']['user_approved_quality_rubric'],False)

if __name__=='__main__':unittest.main()
