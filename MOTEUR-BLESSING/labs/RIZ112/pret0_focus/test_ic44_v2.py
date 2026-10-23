#!/usr/bin/env python3
"""Reproducible 44 out of 44 input-to-ICE synthetic counterfactuals."""
import copy,unittest
from bridge44 import PRESTART,BridgeError
from test_bridge44 import packet
from ic44_v2 import simulate,perturb,audit_44,IC44Error

ALT={
 '001':190.,'002':250.,'003':.6,'004':0.,'005':90.,
 '006':'charcoal','007':.79,'008':400.,'009':15.,'010':'steel',
 '011':5.,'012':'worn','013':False,'014':1.15,'015':'unvented',
 '016':'charcoal_stove','017':False,'018':.55,'019':False,'020':False,
 '021':False,'022':False,'023':False,'024':'medium_white_hypothesis',
 '025':5.2,'026':'parboiled','027':'lot_B_synthetic','028':500.,
 '029':.17,'030':.85,'031':.10,'032':.19,'033':1.65,'034':16.,
 '035':250.,'036':50.,'037':40.,'038':40.,'039':40.,'040':1200.,
 '041':850.,'042':.80,'045':7.,'047':28.,
}
assert set(ALT)==set(PRESTART)

class Test44IC(unittest.TestCase):
    def test_each_input_changes_ice(self):
        r=audit_44(packet(),ALT)
        self.assertEqual(r['routed'],44)
        self.assertEqual(r['IC_demo_changed_count'],44)
        for row in r['cases']:
            with self.subTest(rid=row['id']):
                self.assertTrue(row['changed'],row)
    def test_demo_is_not_scientific(self):
        x=simulate(packet())
        self.assertEqual(x['routes'],44)
        self.assertIsNone(x['IC_SCIENTIFIQUE_PCT'])
        self.assertTrue(x['assumptions']['not_real_probability'])
        self.assertTrue(0<x['IC_DEMO_PCT']<100)
    def test_preparation_time_boundary(self):
        p=packet()
        p['case_inputs']['032']['available_at_utc']='2026-10-23T11:01:00Z'
        with self.assertRaises(BridgeError):simulate(p)
    def test_future_plan(self):
        p=packet()
        p['action_plans']['055']['available_at_utc']='2026-10-23T11:01:00Z'
        with self.assertRaises(BridgeError):simulate(p)
    def test_poststart_leak(self):
        p=packet();p['actual_quality']=99.
        with self.assertRaises(BridgeError):simulate(p)
    def test_unknown_not_faked(self):
        p=packet();p['case_inputs']['027'].update(state='UNKNOWN',value=None)
        r=simulate(p)
        self.assertEqual(r['status'],'ABSTAIN_UNKNOWN')
        self.assertIsNone(r['IC_DEMO_PCT'])
    def test_twin_conflict(self):
        p=packet();p['case_inputs']['035']['value']=1.
        with self.assertRaises(BridgeError):simulate(p)
    def test_inactive_plan_is_legitimately_neutral(self):
        p=packet();p['action_plans']['061']['status']='NOT_PLANNED'
        a=simulate(p)['IC_DEMO_PCT']
        b=simulate(perturb(p,'003',.4))['IC_DEMO_PCT']
        self.assertEqual(a,b)
    def test_outcome_target_descriptions_not_used(self):
        p=packet();x=simulate(p)['IC_DEMO_PCT']
        p['target_contract']={str(i):'NOT_OBSERVED' for i in range(99,113)}
        self.assertEqual(simulate(p)['IC_DEMO_PCT'],x)
    def test_repeatable(self):
        p=packet()
        self.assertEqual(simulate(p),simulate(copy.deepcopy(p)))

if __name__=='__main__':unittest.main()
