#!/usr/bin/env python3
"""Step7 tests: temporal graph, invariant safety, resource contracts and honesty."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step7'))
from graph_governor import analyze7,edges_audit,topological_sort,DependencyError,feasibility,DECLARED
from engine112 import ContractError
P=ROOT/'step6/examples/A_couvercle_ajuste_112.json'
def packet():return json.loads(P.read_text(encoding='utf8'))
def checks(p):return {tuple(x['cases']):x for x in analyze7(p)['feasibility']['checks']}
class GraphGovernance(unittest.TestCase):
 def test_traces_exact_112(self):self.assertEqual(analyze7(packet())['case_count'],112)
 def test_original_cycles_explicit_rejected(self):
  a,r=edges_audit();self.assertEqual(len(a),150);self.assertEqual(len(r),19)
  self.assertEqual(sum(e['why']=='POSTSTART_TARGET_CANNOT_BE_PRESTART_INPUT' for e in r),17)
 def test_no_outcome_points_at_plan(self):
  a,_=edges_audit();self.assertTrue(all(int(e['upstream'])<99 or int(e['downstream'])>=99 for e in a))
 def test_dag_topological(self):self.assertEqual(set(topological_sort(edges_audit()[0])),{f'{i:03}' for i in range(1,113)})
 def test_cycle_detect(self):
  a,_=edges_audit();a.append({'upstream':'112','downstream':'001'})
  with self.assertRaises(DependencyError):topological_sort(a)
 def test_some_cases_not_reachable_to_quality_112(self):
  x=analyze7(packet())['graph_governance'];self.assertEqual(len(x['structural_hypothesis_paths_to_Q112']),50)
  self.assertEqual(len(x['unlinked_to_Q112']),62)
 def test_reachable_does_not_mean_effect(self):self.assertEqual(analyze7(packet())['validated_case_effects'],0)
 def test_no_quality_score(self):self.assertIsNone(analyze7(packet())['ic_percent'])
 def test_no_real_trials(self):self.assertEqual(analyze7(packet())['observed_real_trials'],0)
 def test_no_approved_rubric(self):self.assertFalse(analyze7(packet())['quality_protocol_approved'])
 def test_water_stock_consistent(self):self.assertEqual(checks(packet())[('002','035')]['status'],'CONSISTENT')
 def test_water_stock_shortage(self):
  p=packet();p['case_inputs']['002'].update(state='ASSUMPTION',value=150.0)
  self.assertEqual(checks(p)[('002','035')]['status'],'INCONSISTENT')
 def test_water_stock_unknown_is_not_zero(self):
  p=packet();p['case_inputs']['002'].update(state='UNKNOWN',value=None)
  self.assertEqual(checks(p)[('002','035')]['status'],'UNRESOLVED')
 def test_vessel_capacity_necessary_only(self):self.assertEqual(checks(packet())[('008','035')]['status'],'CONSISTENT_NECESSARY_ONLY')
 def test_vessel_capacity_conflict(self):
  p=packet();p['case_inputs']['008'].update(state='ASSUMPTION',value=100)
  self.assertEqual(checks(p)[('008','035')]['status'],'INCONSISTENT')
 def test_vessel_capacity_unknown(self):
  p=packet();p['case_inputs']['008'].update(state='UNKNOWN',value=None)
  self.assertEqual(checks(p)[('008','035')]['status'],'UNRESOLVED')
 def test_lid_plan_conflict(self):
  p=packet();p['case_inputs']['013'].update(state='ASSUMPTION',value=False)
  self.assertEqual(checks(p)[('013','064')]['status'],'INCONSISTENT')
 def test_scale_conflict(self):
  p=packet();p['case_inputs']['019'].update(state='ASSUMPTION',value=False)
  self.assertEqual(checks(p)[('019','050')]['status'],'INCONSISTENT')
 def test_measurement_tool_conflict(self):
  p=packet();p['case_inputs']['020'].update(state='ASSUMPTION',value=False)
  self.assertEqual(checks(p)[('020','053')]['status'],'INCONSISTENT')
 def test_strainer_conflict(self):
  p=packet();p['case_inputs']['021'].update(state='ASSUMPTION',value=False)
  self.assertEqual(checks(p)[('021','057')]['status'],'INCONSISTENT')
 def test_utensil_conflict(self):
  p=packet();p['case_inputs']['022'].update(state='ASSUMPTION',value=False)
  self.assertEqual(checks(p)[('022','077')]['status'],'INCONSISTENT')
 def test_serving_conflict(self):
  p=packet();p['case_inputs']['023'].update(state='ASSUMPTION',value=False)
  self.assertEqual(checks(p)[('023','081')]['status'],'INCONSISTENT')
 def test_power_adjustment_conflict(self):
  p=packet();p['case_inputs']['017'].update(state='ASSUMPTION',value=False)
  self.assertEqual(checks(p)[('017','068')]['status'],'INCONSISTENT')
 def test_energy_not_invented(self):self.assertEqual(checks(packet())[('006','065')]['status'],'UNRESOLVED')
 def test_energy_declared_absent_conflicts(self):
  p=packet();p['case_inputs']['006'].update(state='ASSUMPTION',value='none')
  self.assertEqual(checks(p)[('006','065')]['status'],'INCONSISTENT')
 def test_no_unjustified_quantified_impact(self):
  self.assertTrue(all(e['scientific_impact']=='NOT_QUANTIFIED' for e in analyze7(packet())['feasibility']['checks']))
 def test_no_future_target_prestart(self):
  p=packet();p['prestart']['final_score']=99
  with self.assertRaises(ContractError):analyze7(p)
 def test_frozen_time_protection(self):
  p=packet();p['action_plans']['049']['available_at_utc']=p['prestart']['start_utc']
  with self.assertRaises(ContractError):analyze7(p)
 def test_full_original_112_preserved(self):
  a=analyze7(packet());self.assertEqual(a['v6_case_processing']['processed'],112)
 def test_lid_alters_physical_graph_no_ic(self):
  b=json.loads((ROOT/'step6/examples/B_couvercle_fuyant_112.json').read_text(encoding='utf8'))
  self.assertNotEqual(analyze7(packet())['packet_sha256'],analyze7(b)['packet_sha256'])
  self.assertIsNone(analyze7(b)['ic_percent'])
 def test_no_doublecount_numerical_effect(self):
  x=analyze7(packet());self.assertEqual(len(x['quantified_physical_case_paths']),17)
  self.assertEqual(x['validated_case_effects'],0)
if __name__=='__main__':unittest.main(verbosity=2)
