import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step13'))
from prospective_branches import evaluate_branches,HierarchyError

class TestH2(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.packet=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text())
 def go(self,**kw):
  opts={'material':'copper','diameter_cm':18,'wall_mm':2,'water_g':180,'draws':200,'seed':42}
  opts.update(kw)
  return evaluate_branches(self.packet,**opts)
 def test_runnable_nested_scenario(self):
  r=self.go();self.assertIsInstance(r['baseline_ic_demo_percent'],float)
 def test_mutable_original_not_modified(self):
  before=copy.deepcopy(self.packet);self.go(conditional_water_policy={'trigger_shortfall_g':5,'dose_g':60,'adherence_probability':1});self.assertEqual(before,self.packet)
 def test_predeclared_policy_changes_outcome(self):
  r=self.go(conditional_water_policy={'trigger_shortfall_g':5,'dose_g':65,'adherence_probability':1})
  self.assertGreater(r['conditional_plan_ic_demo_percent'],r['baseline_ic_demo_percent'])
 def test_disable_policy_returns_same_result(self):
  r=self.go(conditional_water_policy={'trigger_shortfall_g':5,'dose_g':65,'adherence_probability':0})
  self.assertEqual(r['conditional_plan_ic_demo_percent'],r['baseline_ic_demo_percent'])
 def test_without_policy_has_no_difference(self):
  r=self.go();self.assertEqual(r['conditional_plan_ic_demo_percent'],r['baseline_ic_demo_percent'])
 def test_common_random_number_alignment(self):
  base=self.go();alt=self.go(conditional_water_policy={'trigger_shortfall_g':5,'dose_g':65,'adherence_probability':1})
  self.assertEqual(base['baseline_ic_demo_percent'],alt['baseline_ic_demo_percent'])
 def test_no_stock_means_no_extra_water(self):
  p=copy.deepcopy(self.packet);p['case_inputs']['002'].update(state='UNKNOWN',value=None)
  out=evaluate_branches(p,material='copper',water_g=180,diameter_cm=18,wall_mm=2,draws=200,
    conditional_water_policy={'trigger_shortfall_g':5,'dose_g':60,'adherence_probability':1})
  self.assertEqual(out['conditional_plan_ic_demo_percent'],out['baseline_ic_demo_percent'])
 def test_low_stock_limits_effect(self):
  p=copy.deepcopy(self.packet);p['case_inputs']['002']['value']=180
  out=evaluate_branches(p,material='copper',water_g=180,diameter_cm=18,wall_mm=2,draws=200,
    conditional_water_policy={'trigger_shortfall_g':5,'dose_g':60,'adherence_probability':1})
  self.assertEqual(out['conditional_plan_ic_demo_percent'],out['baseline_ic_demo_percent'])
 def test_policy_declared_case_087_required(self):
  p=copy.deepcopy(self.packet);p['correction_policies']['087']['status']='UNDEFINED'
  with self.assertRaises(HierarchyError):
   evaluate_branches(p,material='copper',water_g=180,diameter_cm=18,wall_mm=2,draws=200,
     conditional_water_policy={'trigger_shortfall_g':5,'dose_g':60,'adherence_probability':1})
 def test_rice_profile_hydration_changes_demo(self):
  a=self.go(rice_profile={'water_capacity_g_per_g':0.8})
  b=self.go(rice_profile={'water_capacity_g_per_g':2.2})
  self.assertNotEqual(a['baseline_ic_demo_percent'],b['baseline_ic_demo_percent'])
 def test_profile_starch_has_executable_path(self):
  a=self.go(water_g=300,rice_profile={'surface_starch_index':0.1})
  b=self.go(water_g=300,rice_profile={'surface_starch_index':1.0})
  self.assertNotEqual(a['baseline_median_q_demo'],b['baseline_median_q_demo'])
 def test_rinse_subparameter_plan_required(self):
  p=copy.deepcopy(self.packet);p['action_plans']['054']['status']='NOT_PLANNED'
  with self.assertRaises(HierarchyError):
   evaluate_branches(p,material='copper',water_g=180,diameter_cm=18,wall_mm=2,draws=200,
    rice_profile={'rinse_removal_fraction':0.7})
 def test_profile_invalid_rejected(self):
  with self.assertRaises(HierarchyError):self.go(rice_profile={'water_capacity_g_per_g':-1})
 def test_policy_invalid_rejected(self):
  with self.assertRaises(HierarchyError):self.go(conditional_water_policy={'dose_g':10})
 def test_lid_absent_simulated_not_unconditional_reject(self):
  r=self.go(lid_present=False)
  self.assertIsNotNone(r['baseline_ic_demo_percent'])
  self.assertIn('ANTICIPATE_NO_LID',[x['id'] for x in r['trace']])
 def test_wood_direct_safe_gate_no_fictitious_probability(self):
  r=self.go(material='wood_unrated')
  self.assertEqual(r['status'],'UNSAFE_PATH_WITHOUT_SAFE_PROSPECTIVE_MODEL')
  self.assertIsNone(r['ic_demo_percent'])
 def test_wood_insert_scenario_computes_assumed_path(self):
  r=self.go(material='wood_unrated',heat_path='indirect_metal_insert')
  self.assertIsNotNone(r['baseline_ic_demo_percent'])
 def test_no_future_leakage(self):
  r=self.go();self.assertEqual(r['targets_used_as_predictors'],0)
  self.assertEqual(r['post_T0_measured_values_used'],0)
 def test_material_affects_heat_path(self):
  a=self.go(material='copper');b=self.go(material='ceramic_rated')
  self.assertNotEqual(a['thermal_path']['effective_eta'],b['thermal_path']['effective_eta'])
 def test_deterministic(self):
  opts={'conditional_water_policy':{'trigger_shortfall_g':5,'dose_g':65,'adherence_probability':.7}}
  self.assertEqual(self.go(**opts),self.go(**opts))
 def test_strict_no_scientific_ic(self):self.assertIsNone(self.go()['real_success_ic_percent'])

if __name__=='__main__':unittest.main()
