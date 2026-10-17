import unittest,json,copy,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from route_integrity import (validate_035_water_source,coherent_water_counterfactual,
    audit_planned_route,run_step19,RouteIntegrityError,ACTION_IDS,REMAINING)
LAB=HERE.parent
class TestRouteIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=json.loads((LAB/'step6/examples/A_couvercle_ajuste_112.json').read_text(encoding='utf8'))
    def test_count_30(self):self.assertEqual(len(REMAINING),30)
    def test_all_23_action_coverage(self):self.assertEqual(len(ACTION_IDS),23)
    def test_water_equal(self):self.assertTrue(validate_035_water_source(self.p)['verified_equal'])
    def test_water_mismatch_failclosed(self):
        p=copy.deepcopy(self.p);p['case_inputs']['035']['value']+=10
        with self.assertRaisesRegex(RouteIntegrityError,'CONFLICT_035'):validate_035_water_source(p)
    def test_water_non_number_failclosed(self):
        p=copy.deepcopy(self.p);p['case_inputs']['035']['value']=True
        with self.assertRaises(RouteIntegrityError):validate_035_water_source(p)
    def test_water_which_is_unknown_cannot_guess(self):
        p=copy.deepcopy(self.p);p['case_inputs']['035']['state']='UNKNOWN';p['case_inputs']['035']['value']=None
        with self.assertRaises(ValueError):validate_035_water_source(p)
    def test_coherent_035_edit_updates_both(self):
        p=coherent_water_counterfactual(self.p,180)
        self.assertEqual(p['prestart']['inputs']['water_added_g']['value'],180)
        self.assertEqual(p['case_inputs']['035']['value'],180)
        self.assertEqual(self.p['case_inputs']['035']['value'],300)
    def test_coherent_zero_does_not_invent_negative(self):
        self.assertEqual(coherent_water_counterfactual(self.p,0)['case_inputs']['035']['value'],0)
        with self.assertRaises(RouteIntegrityError):coherent_water_counterfactual(self.p,-1)
    def test_all_30_routes_present(self):
        x=audit_planned_route(self.p);self.assertEqual(set(x['audited_remaining_rubrics']),set(REMAINING));self.assertTrue(x['coverage_complete']);self.assertIsNone(x['scientific_ic_percent'])
    def test_022_false_blocks_077(self):
        p=copy.deepcopy(self.p);p['case_inputs']['022']['value']=False
        z=audit_planned_route(p)
        self.assertEqual(z['action_routes']['077']['status'],'PLAN_BLOCKED_BY_PRESTART_RESOURCE')
        self.assertEqual(z['material_readiness']['022']['status'],'UNAVAILABLE')
    def test_023_false_blocks_081_and_082_and_083(self):
        p=copy.deepcopy(self.p);p['case_inputs']['023']['value']=False
        z=audit_planned_route(p)['action_routes']
        self.assertEqual(z['081']['status'],'PLAN_BLOCKED_BY_PRESTART_RESOURCE')
        self.assertEqual(z['082']['status'],'PLAN_BLOCKED_BY_PRESTART_PREDECESSOR')
        self.assertEqual(z['083']['status'],'PLAN_BLOCKED_BY_PRESTART_PREDECESSOR')
    def test_unknown_023_not_zero(self):
        p=copy.deepcopy(self.p);p['case_inputs']['023'].update(state='UNKNOWN',value=None)
        self.assertEqual(audit_planned_route(p)['action_routes']['081']['status'],'ABSTAIN_UNRESOLVED_PRESTART_DEPENDENCY')
    def test_action_064_not_planned_blocks_068(self):
        p=copy.deepcopy(self.p);p['action_plans']['064']['status']='NOT_PLANNED'
        z=audit_planned_route(p)['action_routes']
        self.assertEqual(z['064']['status'],'NOT_IN_PRESTART_PLAN')
        self.assertEqual(z['068']['status'],'PLAN_BLOCKED_BY_PRESTART_PREDECESSOR')
    def test_action_080_not_planned_blocks_service(self):
        p=copy.deepcopy(self.p);p['action_plans']['080']['status']='NOT_PLANNED'
        self.assertEqual(audit_planned_route(p)['action_routes']['081']['status'],'PLAN_BLOCKED_BY_PRESTART_PREDECESSOR')
    def test_action_unknown_abstains(self):
        p=copy.deepcopy(self.p);p['action_plans']['075']['status']='UNKNOWN'
        self.assertEqual(audit_planned_route(p)['action_routes']['076']['status'],'ABSTAIN_UNRESOLVED_PRESTART_DEPENDENCY')
    def test_policy_not_fired(self):
        z=audit_planned_route(self.p)['conditional_policies']
        self.assertEqual(len(z),4)
        self.assertTrue(all(not v['trigger_observed'] for v in z.values()))
    def test_policy_undefined(self):
        p=copy.deepcopy(self.p);p['correction_policies']['098']['status']='UNDEFINED'
        self.assertEqual(audit_planned_route(p)['conditional_policies']['098']['status'],'ABSTAIN_UNDEFINED_PRESTART_POLICY')
    def test_policy_incomplete_rejected(self):
        p=copy.deepcopy(self.p);p['correction_policies']['090']['trigger']=None
        with self.assertRaises(RouteIntegrityError):audit_planned_route(p)
    def test_invalid_bool_rejected(self):
        p=copy.deepcopy(self.p);p['case_inputs']['022']['value']='yes'
        with self.assertRaises(RouteIntegrityError):audit_planned_route(p)
    def test_after_freeze_rejected(self):
        p=copy.deepcopy(self.p);p['action_plans']['081']['available_at_utc']=p['prestart']['start_utc']
        with self.assertRaises(ValueError):audit_planned_route(p)
    def test_never_promote_quality_effect(self):
        z=audit_planned_route(self.p)
        self.assertFalse(any(r['is_quality_effect'] for r in z['action_routes'].values()))
    def test_h3_coherent_intervention(self):
        z=run_step19(self.p,LAB,planned_water_override_g=180,draws=100)
        self.assertIsNone(z['scientific_ic_percent'])
        self.assertNotEqual(z['035_coherent_counterfactual']['baseline_ic_demo_percent'],z['035_coherent_counterfactual']['after_ic_demo_percent'])
    def test_h3_mismatched_input_rejected(self):
        p=copy.deepcopy(self.p);p['prestart']['inputs']['water_added_g']['value']=200
        with self.assertRaises(RouteIntegrityError):run_step19(p,LAB,draws=100)
if __name__=='__main__':unittest.main()
