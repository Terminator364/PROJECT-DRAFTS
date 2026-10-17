import copy,unittest
from full_variation_v12 import build_case,simulate_population,paired_material_probe,CHOICES
from probe_influences_v12 import audit
from engine112 import PRESTART,ACTIONS,POLICIES,OUTCOMES,DRIVER,analyze112

class TestStage12(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pop=simulate_population(103,100,100)
  cls.audit=audit(100,103)
 def test_all_prestart_variation_specs(self):self.assertEqual(set(CHOICES),set(PRESTART))
 def test_all_44_varied(self):self.assertTrue(self.pop['all_44_prestart_have_varied'])
 def test_includes_100_unique_packets(self):self.assertEqual(len(set(x['packet_sha256'] for x in self.pop['profiles'])),100)
 def test_112_roles_each_packet(self):
  for i in range(100):
   p,_=build_case(103,i)
   self.assertEqual((len(p['case_inputs']),len(p['action_plans']),len(p['correction_policies']),len(p['target_contract'])),(44,37,13,14))
 def test_14_quality_definitions_never_randomized(self):
  a,_=build_case(103,0);b,_=build_case(103,89)
  self.assertEqual(a['target_contract'],b['target_contract'])
 def test_37_plans_varied(self):
  self.assertTrue(all(x>1 for x in self.pop['per_case_action_states'].values()))
 def test_13_policies_varied(self):
  self.assertTrue(all(x>1 for x in self.pop['per_case_policy_states'].values()))
 def test_all_synthetic_ic_not_scientific(self):
  self.assertTrue(all(p['scientific_ic_percent'] is None for p in self.pop['profiles']))
 def test_no_future_observations(self):self.assertEqual(self.pop['poststart_observations_consumed'],0)
 def test_determinism(self):self.assertEqual(simulate_population(103,4,100),simulate_population(103,4,100))
 def test_driver_alignment(self):
  for i in range(20):
   p,_=build_case(103,i)
   for c,f in DRIVER.items():self.assertEqual(p['case_inputs'][c]['value'],p['prestart']['inputs'][f]['value'])
 def test_nominal_material_invariant_without_law(self):
  p=paired_material_probe(103,100)
  self.assertTrue(p['same_core_physical_inputs'])
  self.assertTrue(p['same_demo_ic'])
 def test_wood_can_abstain(self):
  self.assertGreater(self.pop['counts'].get('ABSTAIN_UNSUPPORTED_VESSEL',0),0)
 def test_valid_some_cases_calculate(self):
  self.assertGreater(self.pop['counts'].get('DEMONSTRATION_ASSUMPTIONS_ONLY_NOT_REAL_Q',0),0)
 def test_influence_audit_all_112(self):self.assertEqual(len(self.audit['cases']),112)
 def test_influence_14_outcomes_as_target(self):
  self.assertEqual(sum(v['category']=='TARGET_DEFINITION_LOCKED_NOT_INPUT' for v in self.audit['cases']),14)
 def test_influence_four_derived_not_mutable(self):
  self.assertEqual(sum(v['category']=='DERIVED_OUTPUT_NOT_INDEPENDENT_RANDOM_INPUT' for v in self.audit['cases']),4)
 def test_2_baselines_for_all(self):
  self.assertTrue(all(len(v['trials'])==2 for v in self.audit['cases']))
 def test_no_proven_effects(self):
  self.assertFalse(any(v['effect_on_real_quality_proven'] for v in self.audit['cases']))
 def test_invalid_mode(self):
  with self.assertRaises(ValueError):build_case(1,1,'trick')
 def test_invalid_amount(self):
  with self.assertRaises(ValueError):simulate_population(1,0,100)
 def test_lock_14_targets(self):
  p,_=build_case(103,2);p2=copy.deepcopy(p);p2['target_contract']['099']['status']='UNDEFINED'
  from ic_integrity_v10 import audited_simulate
  self.assertEqual(audited_simulate(p2,draws=100)['status'],'ABSTAIN_TARGET_CONTRACT_CHANGED')
 def test_100_scenario_count(self):self.assertEqual(sum(self.pop['counts'].values()),100)

if __name__=='__main__':unittest.main()
