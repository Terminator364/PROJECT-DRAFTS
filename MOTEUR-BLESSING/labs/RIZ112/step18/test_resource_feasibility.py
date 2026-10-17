import copy,json,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from resource_feasibility import evaluate_resources,perturb_resource,ResourceContractError
P=HERE.parent/'step6/examples/A_couvercle_ajuste_112.json'
def packet():return json.loads(P.read_text(encoding='utf-8'))
def a(v,u):return {'kind':'ASSUMPTION','value':v,'unit':u,'source':'SYNTHETIC_TEST_ONLY','available_at_utc':'2026-10-16T11:00:00Z'}
def assumptions():return {'water_density_g_per_ml':a(1,'g/ml'),'rice_bulk_density_g_per_ml':a(0.8,'g/ml'),'rinse_volume_planned_ml':a(120,'ml')}
class ResourceFeasibilityTests(unittest.TestCase):
 def test_no_assumptions_abstains(self):self.assertEqual(evaluate_resources(packet())['diagnostics']['cooking_water_inventory']['status'],'ABSTAIN_MISSING_OBSERVATION_OR_CONVERSION')
 def test_cooking_water_stock_margin(self):self.assertEqual(evaluate_resources(packet(),assumptions())['diagnostics']['cooking_water_inventory']['margin_ml'],50)
 def test_cooking_water_stock_perturb(self):self.assertAlmostEqual(perturb_resource(packet(),assumptions(),'002')['delta_margin_ml'],3.5)
 def test_rinse_stock_perturb(self):self.assertAlmostEqual(perturb_resource(packet(),assumptions(),'005')['delta_margin_ml'],10)
 def test_pot_capacity_perturb(self):self.assertAlmostEqual(perturb_resource(packet(),assumptions(),'008')['delta_margin_ml'],17)
 def test_initial_load_proxy(self):self.assertEqual(evaluate_resources(packet(),assumptions())['diagnostics']['pot_initial_load_proxy']['margin_ml'],1200)
 def test_unknown_not_zero(self):
  p=packet();p['case_inputs']['002'].update(state='UNKNOWN',value=None)
  self.assertIsNone(evaluate_resources(p,assumptions())['diagnostics']['cooking_water_inventory']['margin_ml'])
 def test_source_required(self):
  p=assumptions();p['water_density_g_per_ml']['source']=''
  with self.assertRaises(ResourceContractError):evaluate_resources(packet(),p)
 def test_wrong_units_rejected(self):
  p=packet();p['case_inputs']['008']['unit']='g'
  with self.assertRaises(ResourceContractError):evaluate_resources(p,assumptions())
 def test_post_freeze_rejected(self):
  p=assumptions();p['water_density_g_per_ml']['available_at_utc']='2026-10-16T12:30:00Z'
  with self.assertRaises(ResourceContractError):evaluate_resources(packet(),p)
 def test_nonfinite_density_rejected(self):
  p=assumptions();p['water_density_g_per_ml']['value']=float('inf')
  with self.assertRaises(ResourceContractError):evaluate_resources(packet(),p)
 def test_no_mutation(self):
  p=packet();copy_p=copy.deepcopy(p);perturb_resource(p,assumptions(),'002');self.assertEqual(p,copy_p)
 def test_no_Q_fabrication(self):
  q=evaluate_resources(packet(),assumptions());self.assertIsNone(q['scientific_ic_percent']);self.assertTrue(all(not x['is_quality_effect'] for x in q['diagnostics'].values()))
 def test_rinse_not_planned(self):
  p=packet();p['action_plans']['054']['status']='NOT_PLANNED';self.assertEqual(evaluate_resources(p,assumptions())['diagnostics']['rinse_water_inventory']['status'],'NOT_PLANNED_ACTION')
 def test_shortage_negative_margin(self):
  p=packet();p['case_inputs']['002']['value']=200;z=evaluate_resources(p,assumptions())['diagnostics']['cooking_water_inventory'];self.assertEqual(z['margin_ml'],-100);self.assertFalse(z['details']['feasible_by_volume'])
 def test_impossible_perturb_rubric(self):
  with self.assertRaises(ResourceContractError):perturb_resource(packet(),assumptions(),'099')
 def test_unsupported_parameter_rejected(self):
  p=assumptions();p['magic_q_bonus']=a(.01,'percent')
  with self.assertRaises(ResourceContractError):evaluate_resources(packet(),p)
if __name__=='__main__':unittest.main()
