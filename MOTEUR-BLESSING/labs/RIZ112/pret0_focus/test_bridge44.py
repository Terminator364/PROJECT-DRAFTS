#!/usr/bin/env python3
"""RIZ112 44-route checks (offline, no external dependency)."""
import copy
import unittest
from bridge44 import evaluate44, BridgeError, PRESTART, TWINS

VALUES={
 '001':160.,'002':400.,'003':2.,'004':5.,'005':1000.,
 '006':'gas','007':.95,'008':1800.,'009':20.,'010':'aluminium',
 '011':3.,'012':'clean_flat','013':True,'014':.8,'015':'vented',
 '016':'gas_burner','017':True,'018':.8,'019':True,'020':True,
 '021':True,'022':True,'023':True,'024':'long_white_hypothesis',
 '025':7.,'026':'polished','027':'lot_A_synthetic','028':100.,
 '029':.05,'030':.5,'031':.01,'032':.12,'033':1.35,'034':12.,
 '035':300.,'036':8.,'037':22.,'038':22.,'039':28.,'040':300.,
 '041':550.,'042':.6,'045':4.,'047':22.}
ALT={'006':'charcoal','010':'copper','012':'worn','015':'unvented',
     '016':'charcoal_stove','024':'medium_white_hypothesis',
     '026':'parboiled','027':'lot_B_synthetic'}

def packet():
    assert set(VALUES)==set(PRESTART)
    p={'prestart':{'freeze_utc':'2026-10-23T10:00:00Z',
        'start_utc':'2026-10-23T11:00:00Z','inputs':{}},
       'case_inputs':{},'action_plans':{},'correction_policies':{},
       'target_contract':{}}
    for rid,v in VALUES.items():
        p['case_inputs'][rid]={
         'state':'PLANNED' if rid in ('035','041','047') else 'ASSUMPTION',
         'value':v,'unit':None,'source':'SYNTHETIC_TEST',
         'available_at_utc':'2026-10-23T09:00:00Z'}
    for rid,name in TWINS.items():
        p['prestart']['inputs'][name]={
         'value':VALUES[rid],'kind':'ASSUMPTION','source':'SYNTHETIC_TEST',
         'available_at_utc':'2026-10-23T09:00:00Z'}
    p['prestart']['inputs']['rinse_removal_fraction']={
        'value':.4,'kind':'PLANNED','source':'SYNTHETIC_TEST',
        'available_at_utc':'2026-10-23T09:00:00Z'}
    for i in range(49,86):
        p['action_plans'][f'{i:03d}']={
         'status':'PLANNED','source':'SYNTHETIC_TEST',
         'available_at_utc':'2026-10-23T09:00:00Z'}
    return p

def mutated(p,rid):
    x=copy.deepcopy(p);old=x['case_inputs'][rid]['value']
    new=(ALT[rid] if rid in ALT else
         (not old if type(old)==bool else
          old+.1 if type(old) in (int,float) and 0<=old<1 else old+1))
    x['case_inputs'][rid]['value']=new
    if rid in TWINS:x['prestart']['inputs'][TWINS[rid]]['value']=new
    return x

class TestBridge44(unittest.TestCase):
    def setUp(self):self.p=packet()
    def test_all_44_routes_evaluated(self):
        r=evaluate44(self.p)
        self.assertTrue(r['routing_complete'])
        self.assertEqual(r['routed_count'],44)
        self.assertEqual(r['evaluated_count'],44)
        self.assertIsNone(r['scientific_ic_percent'])
    def test_all_44_have_mutation_effect_on_typed_route(self):
        baseline=evaluate44(self.p)['routes']
        for rid in PRESTART:
            with self.subTest(rid=rid):
                b=evaluate44(mutated(self.p,rid))['routes']
                self.assertNotEqual(b[rid]['output'],baseline[rid]['output'])
    def test_refuse_future_input(self):
        p=packet();p['case_inputs']['001']['available_at_utc']='2026-10-23T11:01:00Z'
        with self.assertRaisesRegex(BridgeError,'temporal leakage'):evaluate44(p)
    def test_refuse_future_plan(self):
        p=packet();p['action_plans']['064']['available_at_utc']='2026-10-23T11:01:00Z'
        with self.assertRaisesRegex(BridgeError,'future action'):evaluate44(p)
    def test_refuse_semantic_twin_divergence(self):
        p=packet();p['case_inputs']['035']['value']=200.
        with self.assertRaisesRegex(BridgeError,'semantic twin'):evaluate44(p)
    def test_refuse_outcome_leakage(self):
        p=packet();p['actual_quality']=90
        with self.assertRaisesRegex(BridgeError,'post-T0'):evaluate44(p)
    def test_unknown_is_not_zero(self):
        p=packet();p['case_inputs']['027'].update(state='UNKNOWN',value=None)
        r=evaluate44(p)['routes']['027']
        self.assertIsNone(r['output'])
        self.assertEqual(r['status'],'UNKNOWN')
    def test_feasibility_is_not_quality(self):
        p=packet();p['case_inputs']['002']['value']=100.
        r=evaluate44(p)
        self.assertLess(r['routes']['002']['output'],0)
        self.assertIsNone(r['scientific_ic_percent'])
    def test_provenance_is_not_quality_bonus(self):
        a=evaluate44(self.p);b=evaluate44(mutated(self.p,'027'))
        self.assertNotEqual(a['routes']['027']['output'],b['routes']['027']['output'])
        self.assertEqual(a['routes']['035']['output'],b['routes']['035']['output'])
    def test_explicit_approximation_constants(self):
        r=evaluate44(self.p)
        self.assertEqual(r['assumptions']['dry_rice_bulk_density_g_per_ml'],.85)
        self.assertGreater(r['routes']['011']['output'],0)
    def test_lid_mutation_changes_plan_and_evaporation(self):
        a=evaluate44(self.p)['routes']
        b=evaluate44(mutated(self.p,'013'))['routes']
        self.assertFalse(b['013']['output'])
        self.assertNotEqual(a['045']['output'],b['045']['output'])

if __name__=='__main__':unittest.main()
