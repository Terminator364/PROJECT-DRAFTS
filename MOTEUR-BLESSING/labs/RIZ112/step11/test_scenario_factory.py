import copy, json, unittest
from pathlib import Path
from scenario_factory import _make, _set, evaluate, run, SOURCE

class TestScenarioFactory(unittest.TestCase):
    def test_repeatability_and_variety(self):
        a=run(103,12,100);b=run(103,12,100)
        self.assertEqual(a,b)
        self.assertGreater(len({str(x['scenario']) for x in a['scenarios']}),8)
    def test_complete_112_role_contract(self):
        p,s=_make(42,2)
        self.assertEqual((len(p['case_inputs']),len(p['action_plans']),len(p['correction_policies']),len(p['target_contract'])),(44,37,13,14))
        self.assertEqual(len(p['prestart']['inputs']),16)
    def test_core_driver_alignment(self):
        p,s=_make(42,2)
        from engine112 import DRIVER
        for case,k in DRIVER.items():self.assertEqual(p['case_inputs'][case]['value'],p['prestart']['inputs'][k]['value'])
    def test_barren_wood_abstains(self):
        p,s=_make(1,0,{'vessel':'wood_unrated'})
        q=evaluate(p,s,100)
        self.assertEqual(q['status'],'ABSTAIN_UNSUPPORTED_VESSEL');self.assertIsNone(q['ic_demo_percent'])
    def test_wood_does_not_receive_fabricated_bonus(self):
        a,sa=_make(1,0,{'vessel':'wood_unrated'});b,sb=_make(1,0,{'vessel':'metal'})
        self.assertEqual(a['prestart']['inputs'],b['prestart']['inputs'])
        self.assertIsNone(evaluate(a,sa,100)['scientific_ic_percent'])
    def test_no_lid_no_lid_action(self):
        p,s=_make(2,0,{'lid':False})
        self.assertFalse(p['case_inputs']['013']['value'])
        for k in ('064','070','080'):self.assertEqual(p['action_plans'][k]['status'],'NOT_PLANNED')
    def test_different_water_reaches_ic(self):
        p=json.loads(SOURCE.read_text())
        s={'material':'metal'}
        baseline=evaluate(p,s,300,20261016)
        p2=copy.deepcopy(p);_set(p2,'035',240.0)
        reduced=evaluate(p2,s,300,20261016)
        self.assertEqual(baseline['status'],'DEMONSTRATION_ASSUMPTIONS_ONLY_NOT_REAL_Q')
        self.assertNotEqual(baseline['ic_demo_percent'],reduced['ic_demo_percent'])
        self.assertIsNone(reduced['scientific_ic_percent'])
    def test_compatible_material_is_no_fabricated_effect(self):
        p=json.loads(SOURCE.read_text())
        a=evaluate(p,{'material':'metal'},100,2)
        b=evaluate(p,{'material':'ceramic_rated'},100,2)
        self.assertEqual(a['ic_demo_percent'],b['ic_demo_percent'])
    def test_target_frozen(self):
        p,s=_make(42,2)
        for k,v in p['target_contract'].items():self.assertEqual(v['status'],'DRAFT')
        self.assertEqual(run(42,1,100)['poststart_input_used'],0)
    def test_invalid_unsafe_no_numbers(self):
        with self.assertRaises(ValueError):_make(1,0,{'water_g':-1})
        with self.assertRaises(ValueError):_make(1,0,{'power_w':0})
    def test_malformed_override_rejected(self):
        with self.assertRaises(ValueError):_make(1,0,{'ic_bonus':100})
    def test_unknown_real_model(self):
        p,s=_make(21,3,{'vessel':'metal'})
        result=evaluate(p,s,100)
        self.assertIsNone(result['scientific_ic_percent'])
    def test_nonrandom_target(self):
        a,_=_make(21,0);b,_=_make(22,15)
        self.assertEqual(a['target_contract'],b['target_contract'])

if __name__=='__main__':unittest.main()
