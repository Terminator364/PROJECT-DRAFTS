import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'step13'),str(ROOT/'step12'),str(ROOT/'step11')]
from hierarchy import build_registry
from causal_demo import simulate13,prepare,SyntheticContractError,MATERIALS
from full_variation_v12 import build_case
from scenario_factory import _set
BASE=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text())

class HierarchicalTests(unittest.TestCase):
 def test_all_112(self):
  reg=build_registry();self.assertEqual(len(reg['cases']),112);self.assertEqual(set(reg['cases']),{f'{i:03}' for i in range(1,113)})
 def test_every_role_has_subparams(self):
  for k,r in build_registry()['cases'].items():self.assertGreaterEqual(len(r['subparameters']),2,k)
 def test_role_counts(self):
  from collections import Counter
  self.assertEqual(dict(Counter(v['role'] for v in build_registry()['cases'].values())),
     {'INPUT':44,'DERIVED':4,'PLANNED_ACTION':37,'CONDITIONAL_POLICY':13,'TARGET_DEFINITION':14})
 def test_categories_not_free_independent(self):
  reg=build_registry()['cases'];self.assertEqual(reg['112']['role'],'TARGET_DEFINITION');self.assertEqual(reg['043']['role'],'DERIVED')
 def test_all_effects_not_claimed_calibrated(self):
  self.assertFalse(any(r['calibrated_effect'] for r in build_registry()['cases'].values()))
 def test_material_properties_are_different(self):
  self.assertLess(MATERIALS['wood_unrated']['conductivity_W_mK'],MATERIALS['ceramic_rated']['conductivity_W_mK'])
  self.assertGreater(MATERIALS['copper']['conductivity_W_mK'],MATERIALS['iron']['conductivity_W_mK'])
 def test_fallback_assumptions_visible(self):
  v=simulate13(BASE,100);self.assertIn('009',v['assumed_missing_inputs']);self.assertNotEqual(v['assumed_missing_inputs']['009'],0)
 def test_metal_ic_not_null(self):
  q=copy.deepcopy(BASE);_set(q,'010','metal');r=simulate13(q,100);self.assertIsInstance(r['ic_demo_percent'],float)
 def test_wood_not_abstained(self):
  q=copy.deepcopy(BASE);_set(q,'010','wood_unrated');r=simulate13(q,100);self.assertEqual(r['ic_demo_percent'],0);self.assertIn('unsafe', ' '.join(r['anticipated_events']))
 def test_wood_indirect_heating_conditional_branch(self):
  q=copy.deepcopy(BASE);_set(q,'010','wood_unrated');_set(q,'016','indirect_water_bath')
  r=simulate13(q,100)
  self.assertEqual(r['heat_route'],'indirect_water_bath')
  self.assertFalse(any('unsafe' in x for x in r['anticipated_events']))
  self.assertIsNotNone(r['ic_demo_percent'])
 def test_explicit_112_subsubparameter_registry(self):
  d=build_registry()['cases']
  self.assertEqual(len(d),112)
  self.assertTrue(all(len(x['sub_subparameters'])>=2 for v in d.values() for x in v['subparameters']))
 def test_ceramic_and_metal_different(self):
  a=copy.deepcopy(BASE);b=copy.deepcopy(BASE);_set(a,'010','metal');_set(b,'010','ceramic_rated');
  ra=simulate13(a,400);rb=simulate13(b,400);self.assertNotEqual(ra['ic_demo_percent'],rb['ic_demo_percent'])
 def test_material_numeric_mechanism(self):
  a=copy.deepcopy(BASE);b=copy.deepcopy(BASE);_set(a,'010','metal');_set(b,'010','copper');
  self.assertNotEqual(prepare(a)['changed_drivers']['transfer_efficiency'],prepare(b)['changed_drivers']['transfer_efficiency'])
 def test_thickness_subparam(self):
  a=copy.deepcopy(BASE);b=copy.deepcopy(BASE);_set(a,'011',1.0);_set(b,'011',5.0)
  self.assertNotEqual(prepare(a)['changed_drivers']['transfer_efficiency'],prepare(b)['changed_drivers']['transfer_efficiency'])
 def test_diameter_subparam(self):
  a=copy.deepcopy(BASE);b=copy.deepcopy(BASE);_set(a,'009',15.0);_set(b,'009',30.0)
  self.assertNotEqual(prepare(a)['changed_drivers']['evap_reference_g_per_min'],prepare(b)['changed_drivers']['evap_reference_g_per_min'])
 def test_no_lid_no_veto(self):
  q=copy.deepcopy(BASE);_set(q,'013',False);r=simulate13(q,100);self.assertIsNotNone(r['ic_demo_percent']);self.assertTrue(r['adapted_plans'])
 def test_no_tools_not_veto(self):
  q=copy.deepcopy(BASE);_set(q,'019',False);_set(q,'020',False);r=simulate13(q,100);self.assertIsNotNone(r['ic_demo_percent'])
 def test_stock_water_conservation(self):
  q=copy.deepcopy(BASE);_set(q,'002',150.);x=prepare(q);self.assertLessEqual(x['prestart']['inputs']['water_added_g']['value'],150.)
 def test_capacity_anticipation(self):
  q=copy.deepcopy(BASE);_set(q,'008',250.);x=prepare(q);self.assertTrue(any('spill' in a for a in x['alerts']))
 def test_rinsing_effect(self):
  a=copy.deepcopy(BASE);b=copy.deepcopy(BASE);a['action_plans']['054']['status']='PLANNED';a['action_plans']['055']['status']='PLANNED';b['action_plans']['054']['status']='NOT_PLANNED'
  self.assertNotEqual(prepare(a)['changed_drivers']['rinse_removal_fraction'],prepare(b)['changed_drivers']['rinse_removal_fraction'])
 def test_water_hydration_no_bonus(self):
  q=copy.deepcopy(BASE);_set(q,'035',150.);self.assertIn('minimum', simulate13(q,100)['quality_qstar_definition'])
 def test_unknown_material_not_autoguessed(self):
  q=copy.deepcopy(BASE);_set(q,'010','magical_alloy');
  with self.assertRaises(SyntheticContractError):prepare(q)
 def test_target_mutation_guard(self):
  q=copy.deepcopy(BASE);q['target_contract']['112']['measurement_definition']='other target';r=simulate13(q,100)
  self.assertIsNone(r['ic_demo_percent']);self.assertEqual(r['status'],'TARGET_CHANGED_REQUIRES_NEW_MODEL')
 def test_target_not_randomized(self):
  q,_=build_case(20261017,2)
  self.assertEqual(q['target_contract'],BASE['target_contract'])
 def test_no_real_ic(self):
  q,_=build_case(20261017,2);r=simulate13(q,100)
  self.assertIsNone(r['real_ic_percent']);self.assertIsNone(r['scientific_ic_percent'])
 def test_25_percent_threshold_logic(self):
  r=simulate13(BASE,100);self.assertEqual(r['ic_threshold_decision_0_25'],r['ic_demo_percent']>=25)
 def test_repeatability(self):
  q,_=build_case(20261017,2);a=simulate13(q,100,55);b=simulate13(q,100,55);self.assertEqual(a,b)
 def test_different_seed_not_fabricated_identical(self):
  q=copy.deepcopy(BASE);a=simulate13(q,300,1);b=simulate13(q,300,2);self.assertNotEqual(a['representative_draws'],b['representative_draws'])
 def test_100_scenarios_no_abstentions(self):
  for i in range(100):
   q,_=build_case(20261017,i);r=simulate13(q,100,i)
   self.assertEqual(r['status'],'SYNTHETIC_IC_DEMO_ONLY_NOT_REAL_SUCCESS')
   self.assertTrue(0<=r['ic_demo_percent']<=100)
 def test_event_policy_13(self):
  q,_=build_case(20261017,0);r=simulate13(q,100)
  self.assertEqual(len(r['policy_risk_forecasts']),13)
 def test_only_before_start(self):
  q=copy.deepcopy(BASE);q['case_inputs']['001']['available_at_utc']='2030-01-01T00:00:00Z'
  with self.assertRaises(SyntheticContractError):prepare(q)
 def test_112_role_contract_enforced(self):
  q=copy.deepcopy(BASE);del q['action_plans']['049']
  with self.assertRaises(SyntheticContractError):prepare(q)

if __name__=='__main__':unittest.main()
