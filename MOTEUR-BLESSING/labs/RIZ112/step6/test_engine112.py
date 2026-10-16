#!/usr/bin/env python3
"""Counter-audit: 112/112 role execution, no leakage, no fake numeric effects."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'step6'))
from engine112 import analyze112,ContractError,PRESTART,ACTIONS,POLICIES,OUTCOMES,IDS,DRIVER
from riz112 import InvalidPacket
SOURCE=ROOT/'step6/examples/A_couvercle_ajuste_112.json'
def sample():return json.loads(SOURCE.read_text(encoding='utf8'))
def run(p):return analyze112(p)
class CompleteCaseCoverage(unittest.TestCase):
 def test_exact_112(self):
  o=run(sample());self.assertEqual(o['case_execution']['processed'],112)
  self.assertEqual({n['id'] for n in o['graph']['all_112_case_trace']},IDS)
 def test_roles(self):
  o=run(sample())['case_execution']['role_counts']
  self.assertEqual(o,{'PRESTART':44,'FORECAST':3,'DERIVED':1,'PRESTART_ACTION_PLAN':37,'PRESTART_BRANCH_POLICY':13,'POSTSTART_TARGET_NOT_FEATURE':14})
 def test_count_physically_supported(self):
  o=run(sample());self.assertEqual(o['case_execution']['physical_stage4_count'],15)
  self.assertTrue(o['case_execution']['no_claim_112_numerical_effects'])
 def test_ic_abstains_even_with_contract_complete(self):
  o=run(sample());self.assertIsNone(o['validated_success_IC_percent'])
  self.assertEqual(o['real_trials_observed'],0)
 def test_no_future_label_features(self):
  o=run(sample());self.assertEqual(o['evidence']['poststart_features_consumed'],0)
 def test_all_prestart_ids_required(self):
  for key in PRESTART:
   p=sample();del p['case_inputs'][key]
   with self.subTest(key=key),self.assertRaises(ContractError):run(p)
 def test_all_action_ids_required(self):
  for key in ACTIONS:
   p=sample();del p['action_plans'][key]
   with self.subTest(key=key),self.assertRaises(ContractError):run(p)
 def test_all_policies_required(self):
  for key in POLICIES:
   p=sample();del p['correction_policies'][key]
   with self.subTest(key=key),self.assertRaises(ContractError):run(p)
 def test_all_outcomes_required(self):
  for key in OUTCOMES:
   p=sample();del p['target_contract'][key]
   with self.subTest(key=key),self.assertRaises(ContractError):run(p)
 def test_derived_inputs_not_user_supplied(self):
  p=sample();p['case_inputs']['048']={'value':0}
  with self.assertRaises(ContractError):run(p)
 def test_no_future_fact_import(self):
  p=sample();p['case_inputs']['043']={'value':0}
  with self.assertRaises(ContractError):run(p)
 def test_no_outcome_at_root(self):
  for key in ('quality_score_100','poststart','realized_actions'):
   p=sample();p[key]=95
   with self.subTest(key=key),self.assertRaises(ContractError):run(p)
 def test_no_outcome_in_prestart(self):
  p=sample();p['prestart']['quality_score_100']=99
  with self.assertRaises(ContractError):run(p)
 def test_non_numeric_driver_inconsistent(self):
  p=sample();p['case_inputs']['024']['value']='new_variety'
  with self.assertRaises(ContractError):run(p)
 def test_numeric_driver_inconsistent(self):
  p=sample();p['case_inputs']['035']['value']=234
  with self.assertRaises(ContractError):run(p)
 def test_assumptions_marked(self):
  o=run(sample());self.assertIn('014',o['case_execution']['assumptions']);self.assertFalse(o['evidence']['independent_prestart_source_attestation'])
 def test_timeline_future_prestart(self):
  p=sample();p['case_inputs']['010']['available_at_utc']=p['prestart']['start_utc']
  with self.assertRaises(ContractError):run(p)
 def test_timeline_future_action(self):
  p=sample();p['action_plans']['049']['available_at_utc']=p['prestart']['start_utc']
  with self.assertRaises(ContractError):run(p)
 def test_timeline_future_policy(self):
  p=sample();p['correction_policies']['086']['available_at_utc']=p['prestart']['start_utc']
  with self.assertRaises(ContractError):run(p)
 def test_snapshot_sha_change_when_input_becomes_known(self):
  p=sample();a=run(p);p['case_inputs']['003'].update({'state':'ASSUMPTION','value':0,'source':'SYNTHETIC_TEST'})
  b=run(p);self.assertNotEqual(a['snapshot_sha256'],b['snapshot_sha256'])
  self.assertEqual(a['graph']['physical'],b['graph']['physical']) # NOT fictitiously numerical
 def test_all_prestart_inputs_operationally_consumed(self):
  original=run(sample())
  for id in PRESTART:
   p=sample()
   if id in DRIVER: # driver change must not silently contradict explicit original driver
    p['case_inputs'][id]['source']+='-verified-copy'
   else:
    p['case_inputs'][id]['source']+='-verified-copy'
   r=run(p)
   with self.subTest(id=id):self.assertNotEqual(r['snapshot_sha256'],original['snapshot_sha256'])
 def test_all_actions_operationally_consumed(self):
  orig=run(sample())
  for id in ACTIONS:
   p=sample();p['action_plans'][id]['status']='NOT_PLANNED' if p['action_plans'][id]['status']=='PLANNED' else 'PLANNED'
   r=run(p);assert r['snapshot_sha256']!=orig['snapshot_sha256']
   node={n['id']:n for n in r['graph']['all_112_case_trace']}[id]
   with self.subTest(id=id):self.assertEqual(node['status'],p['action_plans'][id]['status'])
 def test_all_policies_operationally_consumed(self):
  for id in POLICIES:
   p=sample()
   if p['correction_policies'][id]['status']=='DEFINED':
    p['correction_policies'][id].update({'status':'UNDEFINED','trigger':None,'planned_response':None})
   else:p['correction_policies'][id].update({'status':'DEFINED','trigger':'synthetic_trigger','planned_response':'synthetic_predeclared_response'})
   o=run(p);node={n['id']:n for n in o['graph']['all_112_case_trace']}[id]
   with self.subTest(id=id):self.assertEqual(node['status'],p['correction_policies'][id]['status'])
 def test_all_targets_are_defined_no_outcome_consumed(self):
  p=sample()
  for id in OUTCOMES:
   p['target_contract'][id].update({'status':'UNDEFINED','measurement_definition':None})
  r=run(p)
  self.assertEqual(len(r['case_execution']['undefined_target_definitions']),14)
  self.assertIsNone(r['validated_success_IC_percent'])
 def test_declared_lid_absence_plan_inconsistency(self):
  p=sample();p['case_inputs']['013']['value']=False
  r=run(p)
  self.assertTrue(any(set(x['cases'])=={'013','064'} for x in r['graph']['contradictions']))
 def test_declared_scale_absence_plan_inconsistency(self):
  p=sample();p['case_inputs']['019']['value']=False
  self.assertTrue(any(x['cases']==['019','050'] for x in run(p)['graph']['contradictions']))
 def test_resource_shortage(self):
  p=sample();p['case_inputs']['002']['value']=100
  self.assertTrue(any(x['type']=='RESOURCE_SHORTAGE' for x in run(p)['graph']['contradictions']))
 def test_water_replay_changes_derived_not_prob(self):
  a=run(sample());p=sample();p['prestart']['inputs']['water_added_g']['value']=200;p['case_inputs']['035']['value']=200
  b=run(p);self.assertNotEqual(a['graph']['physical'],b['graph']['physical'])
  self.assertNotEqual(a['graph']['all_112_case_trace'][47]['output'],b['graph']['all_112_case_trace'][47]['output'])
  self.assertIsNone(b['validated_success_IC_percent'])
 def test_unmodeled_input_not_assigned_fake_effect(self):
  p=sample();a=run(p);p['case_inputs']['003'].update(state='ASSUMPTION',value=3)
  b=run(p);self.assertEqual(a['graph']['physical'],b['graph']['physical'])
 def test_no_future_outcome_masquerade(self):
  p=sample();p['target_contract']['101']['measurement_definition']={'observed_tenderness':95}
  with self.assertRaises(ContractError):run(p)
 def test_cannot_hide_stage4_driver_as_unknown(self):
  p=sample();p['case_inputs']['035'].update(state='UNKNOWN',value=None)
  with self.assertRaises(ContractError):run(p)
 def test_boolean_type_enforced(self):
  p=sample();p['case_inputs']['013']['value']='true'
  with self.assertRaises(ContractError):run(p)
 def test_context_number_type_enforced(self):
  p=sample();p['case_inputs']['002']['value']='350'
  with self.assertRaises(ContractError):run(p)
 def test_fraction_range_enforced(self):
  p=sample();p['case_inputs']['032'].update(state='ASSUMPTION',value=1.2)
  with self.assertRaises(ContractError):run(p)
 def test_negative_resource_rejected(self):
  p=sample();p['case_inputs']['002']['value']=-1
  with self.assertRaises(ContractError):run(p)
 def test_unknown_nonzero(self):
  p=sample();p['case_inputs']['003']['value']=0
  with self.assertRaises(ContractError):run(p)
 def test_missing_known_must_be_unknown(self):
  p=sample();p['case_inputs']['035']['value']=None
  with self.assertRaises(ContractError):run(p)
 def test_bad_units_rejected(self):
  p=sample();p['case_inputs']['001']['unit']='kg'
  with self.assertRaises(ContractError):run(p)
 def test_nonfinite_rejected(self):
  p=sample();p['case_inputs']['002'].update(state='ASSUMPTION',value=float('nan'))
  with self.assertRaises(ContractError):run(p)
 def test_undefined_policy_must_be_empty(self):
  p=sample();p['correction_policies']['089']['planned_response']='secret_future_action'
  with self.assertRaises(ContractError):run(p)
 def test_defined_policy_must_have_trigger(self):
  p=sample();p['correction_policies']['086']['trigger']=''
  with self.assertRaises(ContractError):run(p)
 def test_exact_numerical_influence_scope(self):
  for name in ['A_couvercle_ajuste','B_couvercle_fuyant','C_chaleur_faible']:
   packet=json.loads((ROOT/f'step6/examples/{name}_112.json').read_text(encoding='utf8'))
   r=run(packet)
   with self.subTest(name=name):
    self.assertEqual(r['case_execution']['processed'],112)
    self.assertEqual(r['case_execution']['physical_stage4_count'],15)
    self.assertIsNone(r['validated_success_IC_percent'])

if __name__=='__main__':unittest.main(verbosity=2)
