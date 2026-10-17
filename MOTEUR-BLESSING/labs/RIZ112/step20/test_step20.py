from __future__ import annotations
import copy,json,unittest,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from physical_influence_envelope import calculate,validate_semantic_twins,coherent_perturbation,audit_perturbations,PhysicalEvidenceError,FIELDS
from quality_outcome_protocol import propose,validate_observation,OutcomeProtocolError,TARGETS
P=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text(encoding='utf-8'))
A=json.loads((HERE/'ASSUMPTIONS_SYNTHETIQUES_NON_CALIBREES.json').read_text(encoding='utf-8'))
CAT=json.loads((ROOT/'reference/step4/CATALOGUE_112_ROLES_ETAPE4.json').read_text(encoding='utf-8'))
class Step20Tests(unittest.TestCase):
 def setUp(self):self.p=copy.deepcopy(P);self.a=copy.deepcopy(A)
 def test_01_nine_twin_fields(self):self.assertEqual(len(validate_semantic_twins(self.p)),9)
 def test_02_thermal_reference(self):
  x=calculate(self.p,self.a);self.assertAlmostEqual(x['physical_account']['energy_margin_for_target_J'],315211.68)
 def test_03_moisture_reference(self):
  x=calculate(self.p,self.a)['physical_account'];self.assertEqual(x['water_for_absorption_target_g'],216)
 def test_04_protect_q(self):self.assertIsNone(calculate(self.p,self.a)['scientific_ic_percent'])
 def test_05_9_responses(self):self.assertEqual(sum(bool(x['physical_intermediate_responded']) for x in audit_perturbations(self.p,self.a)['rows']),9)
 def test_06_independent_provenance_hash(self):
  x=calculate(self.p,self.a);self.assertEqual(len(x['provenance']['packet_sha256']),64)
 def test_07_fail_twin_water(self):
  self.p['case_inputs']['035']['value']+=1
  with self.assertRaisesRegex(PhysicalEvidenceError,'SEMANTIC_TWIN_CONFLICT'):calculate(self.p,self.a)
 def test_08_fail_twin_energy(self):
  self.p['case_inputs']['041']['value']+=1
  with self.assertRaisesRegex(PhysicalEvidenceError,'SEMANTIC_TWIN_CONFLICT'):calculate(self.p,self.a)
 def test_09_fail_twin_all_cases(self):
  for i in FIELDS:
   p=copy.deepcopy(self.p);p['case_inputs'][i]['value']+=1
   with self.subTest(i=i),self.assertRaises(PhysicalEvidenceError):calculate(p,self.a)
 def test_10_unknown_not_zero(self):
  self.p['case_inputs']['036'].update(value=None,state='UNKNOWN')
  with self.assertRaises(PhysicalEvidenceError):calculate(self.p,self.a)
 def test_11_missing_assumption_abstains(self):
  del self.a['water_specific_heat_J_per_gK']
  with self.assertRaises(PhysicalEvidenceError):calculate(self.p,self.a)
 def test_12_unknown_assumption_abstains(self):
  self.a['water_specific_heat_J_per_gK']['kind']='UNKNOWN'
  with self.assertRaises(PhysicalEvidenceError):calculate(self.p,self.a)
 def test_13_future_assumption_reject(self):
  self.a['ambient_heat_loss_W']['available_at_utc']='2026-10-16T12:30:00Z'
  with self.assertRaisesRegex(PhysicalEvidenceError,'POST_FREEZE'):calculate(self.p,self.a)
 def test_14_future_input_reject(self):
  self.p['case_inputs']['035']['available_at_utc']='2026-10-16T12:30:00Z'
  with self.assertRaises(Exception):calculate(self.p,self.a)
 def test_15_nan_reject(self):
  self.a['water_specific_heat_J_per_gK']['value']=float('nan')
  with self.assertRaises(PhysicalEvidenceError):calculate(self.p,self.a)
 def test_16_bool_reject(self):
  self.a['target_water_temperature_C']['value']=True
  with self.assertRaises(PhysicalEvidenceError):calculate(self.p,self.a)
 def test_17_no_overshoot(self):
  self.a['target_water_temperature_C']['value']=15.
  with self.assertRaises(PhysicalEvidenceError):calculate(self.p,self.a)
 def test_18_negative_power_reject(self):
  self.p['case_inputs']['041']['value']=-1;self.p['prestart']['inputs']['power_W']['value']=-1
  with self.assertRaises(PhysicalEvidenceError):calculate(self.p,self.a)
 def test_19_power_zero_does_not_raise_Q(self):
  p=coherent_perturbation(self.p,'041',0);q=calculate(p,self.a)
  self.assertLess(q['physical_account']['energy_margin_for_target_J'],0)
  self.assertIsNone(q['scientific_ic_percent'])
 def test_20_moisture_decreases_when_water_removed(self):
  a=calculate(self.p,self.a)['physical_account'];b=calculate(coherent_perturbation(self.p,'035',0),self.a)['physical_account']
  self.assertLess(b['max_water_before_unmodeled_loss_g'],a['max_water_before_unmodeled_loss_g'])
 def test_21_mass_perturb_rises_energy_demand(self):
  a=calculate(self.p,self.a)['physical_account'];b=calculate(coherent_perturbation(self.p,'001',200),self.a)['physical_account']
  self.assertLess(b['energy_margin_for_target_J'],a['energy_margin_for_target_J'])
 def test_22_source_uptime_reduces_energy(self):
  a=calculate(self.p,self.a)['physical_account'];self.a['source_uptime_fraction']['value']=0.5
  b=calculate(self.p,self.a)['physical_account'];self.assertLess(b['nonnegative_available_energy_J'],a['nonnegative_available_energy_J'])
 def test_23_ambient_loss_not_double_count_as_Q(self):
  self.a['ambient_heat_loss_W']['value']=30
  b=calculate(self.p,self.a);self.assertIsNone(b['scientific_ic_percent']);self.assertGreater(b['physical_account']['assumed_heat_loss_J'],0)
 def test_24_water_evap_ceiling_bounded(self):
  x=calculate(self.p,self.a)['physical_account'];self.assertLessEqual(x['thermal_ceiling_on_evaporation_g'],x['planned_total_water_g'])
 def test_25_finite_difference_negative_rice_effect_on_energy(self):
  rows=audit_perturbations(self.p,self.a)['rows'];self.assertLess(next(x for x in rows if x['id']=='001')['physical_metric_deltas']['energy_margin_for_target_J'],0)
 def test_26_draft_14_targets(self):
  p=propose(CAT);self.assertEqual(len(p['target_rubrics']),14);self.assertEqual(p['target_ids'],TARGETS)
 def test_27_draft_no_Q_formula(self):self.assertIsNone(propose(CAT)['Q_score_formula'])
 def test_28_draft_no_experimental_IC(self):self.assertIsNone(propose(CAT)['quality_IC_percent'])
 def test_29_draft_reject_label_for_prediction(self):
  with self.assertRaises(OutcomeProtocolError):validate_observation(self.p,propose(CAT),{'observations':{}})
 def test_30_reject_unapproved_even_fake_labels(self):
  p=propose(CAT);p['Q_score_formula']='unapproved';
  with self.assertRaises(OutcomeProtocolError):validate_observation(self.p,p,{'observations':{}})
 def test_31_reject_post_started_no_evidence(self):
  p=propose(CAT);p.update(approved_by_user=True,Q_score_formula='needs-authorized-method')
  for row in p['target_rubrics'].values():row['measurement_method_finalized']=True
  with self.assertRaises(OutcomeProtocolError):validate_observation(self.p,p,{'observations':{}})
 def test_32_output_datetime_guard(self):
  p=propose(CAT);p.update(approved_by_user=True,Q_score_formula='needs-authorized-method')
  for row in p['target_rubrics'].values():row['measurement_method_finalized']=True
  obs={i:{'observed_at_utc':'2026-10-16T12:00:00Z','source':'synthetic'} for i in TARGETS}
  with self.assertRaises(OutcomeProtocolError):validate_observation(self.p,p,{'observations':obs})
 def test_33_outcome_kept_separate(self):
  p=propose(CAT);p.update(approved_by_user=True,Q_score_formula='specified-external')
  for row in p['target_rubrics'].values():row['measurement_method_finalized']=True
  obs={i:{'observed_at_utc':'2026-10-16T14:00:00Z','source':'synthetic_test'} for i in TARGETS}
  q=validate_observation(self.p,p,{'observations':obs});self.assertFalse(q['data_used_in_predictions']);self.assertIsNone(q['scientific_ic_percent'])

if __name__=='__main__': unittest.main()
