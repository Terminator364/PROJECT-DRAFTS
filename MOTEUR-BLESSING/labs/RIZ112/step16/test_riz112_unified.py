import copy
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from riz112_unified import run,verify_packet,PacketError,main,DERIVED_IDS

TS='2026-10-16T11:00:00Z'
def role(status,value=None,unit=None):
    return {'state':status,'value':value,'unit':unit,'available_at_utc':TS,'source':'SYNTHETIC_FIXTURE'}
def plan(status='UNKNOWN'):
    return {'status':status,'available_at_utc':TS,'source':'SYNTHETIC_FIXTURE'}
def fixture():
    p={'schema':'riz112/step6/prestart/v1',
       'prestart':{'preparation_id':'SYNTHETIC_A','freeze_utc':'2026-10-16T12:00:00Z','start_utc':'2026-10-16T13:00:00Z','inputs':{}},
       'case_inputs':{},'action_plans':{},'correction_policies':{},'target_contract':{}}
    def inp(value, kind='ASSUMPTION'):
        return {'value':value,'kind':kind,'available_at_utc':TS,'source':'SYNTHETIC_FIXTURE'}
    p['prestart']['inputs']={'rice_mass_g':inp(160),'surface_starch_index':inp(.5),'rinse_removal_fraction':inp(.4,'PLANNED')}
    for i in range(1,49):
        k=f'{i:03d}'
        if k not in DERIVED_IDS:p['case_inputs'][k]=role('UNKNOWN')
    for i in range(49,86):p['action_plans'][f'{i:03d}']=plan()
    for i in range(86,99):p['correction_policies'][f'{i:03d}']=plan('UNDEFINED')
    for i in range(99,113):p['target_contract'][f'{i:03d}']={'status':'DRAFT','measurement_definition':'Not yet approved','protocol_reference':'UNAPPROVED'}
    p['case_inputs']['001']=role('OBSERVED',160,'g')
    p['case_inputs']['003']=role('UNKNOWN',None,'g')
    p['case_inputs']['029']=role('UNKNOWN',None,'fraction')
    p['case_inputs']['030']=role('ASSUMPTION',.5,'fraction')
    p['case_inputs']['022']=role('ASSUMPTION',True,'bool')
    p['case_inputs']['023']=role('ASSUMPTION',True,'bool')
    p['case_inputs']['024']=role('OBSERVED','long_white_hypothesis')
    for k in ('049','054','061','082','077','081','083'):
        p['action_plans'][k]=plan('PLANNED')
    p['correction_policies']['098']=plan('DEFINED')
    p['correction_policies']['098']['trigger']='unsafe_condition';p['correction_policies']['098']['planned_response']='terminate'
    return p

class UnifiedTest(unittest.TestCase):
    def test_full_logical_112(self):
        rec=verify_packet(fixture());self.assertEqual(rec['declared_prestart_or_target_records'],108)
        self.assertEqual(rec['logical_total_rubrics'],112)
        self.assertEqual(rec['derived_forecast_roles'],['043','044','046','048'])
    def test_original_h3_absent_explicit(self):
        report=run(fixture());self.assertEqual(report['H3_demonstration']['status'],'BLOCKED_H3_DEPENDENCY')
        self.assertIsNone(report['ic_demo_percent']);self.assertIsNone(report['scientific_ic_percent'])
        self.assertEqual(report['H4']['rubrics_with_diagnostic_contract'],22)
    def test_immutable_report(self):
        p=fixture();before=copy.deepcopy(p)
        result=run(p);self.assertEqual(p,before);self.assertEqual(result['input_sha256'],run(p)['input_sha256'])
    def test_h4a_diagnostics_shared_input(self):
        v={'salt_stock':{'value':3,'unit':'g','state':'OBSERVED','available_at_utc':TS,'source':'TEST'},
           'salt_dose':{'value':5,'unit':'g','state':'PLANNED','available_at_utc':TS,'source':'TEST'}}
        report=run(fixture(),h4a=v)
        self.assertEqual(report['H4']['a']['mechanisms']['salt']['shortfall_g'],2)
    def test_h4b_integration(self):
        v={'amylose_fraction':{'value':.25,'unit':'dry_mass_fraction','state':'ASSUMPTION','available_at_utc':TS,'source':'TEST'}}
        self.assertEqual(run(fixture(),h4b=v)['H4']['b']['mechanism_groups']['variety']['dry_amylose_mass_g'],40)
    def test_unknown_not_zero(self):
        r=run(fixture())['H4']['a'];self.assertIsNone(r['mechanisms']['salt']['available_g'])
    def test_missing_one_input_fails_closed(self):
        p=fixture();del p['case_inputs']['001']
        with self.assertRaises(PacketError):run(p)
    def test_derived_as_fifth_forecast_fails(self):
        p=fixture();p['case_inputs']['043']=role('OBSERVED',4)
        with self.assertRaises(PacketError):run(p)
    def test_all_4_forecasts_are_derived_only(self):
        for k in DERIVED_IDS:
            p=fixture();p['action_plans'][k]=plan('PLANNED')
            with self.subTest(k=k),self.assertRaises(PacketError):verify_packet(p)
    def test_unknown_number_rejected(self):
        p=fixture();p['case_inputs']['003']['value']=0
        with self.assertRaises(PacketError):run(p)
    def test_future_case_rejected(self):
        p=fixture();p['case_inputs']['023']['available_at_utc']='2026-10-16T13:10:00Z'
        with self.assertRaises(PacketError):run(p)
    def test_future_physics_rejected(self):
        p=fixture();p['prestart']['inputs']['rice_mass_g']['available_at_utc']='2026-10-16T12:10:00Z'
        with self.assertRaises(PacketError):run(p)
    def test_undeclared_timezone_rejected(self):
        p=fixture();p['case_inputs']['001']['available_at_utc']='2026-10-16T10:00:00'
        with self.assertRaises(PacketError):run(p)
    def test_poststart_final_target_does_not_affect_prediction(self):
        p=fixture();a=run(p)
        p['target_contract']['101']['measurement_definition']='TEXT CHANGED POSTSTART (invalid real evidence)'
        b=run(p)
        self.assertEqual(a['H4'],b['H4']);self.assertEqual(a['ic_demo_percent'],b['ic_demo_percent'])
        self.assertNotEqual(a['input_sha256'],b['input_sha256'])
    def test_h3_dependency_mandatory(self):
        with self.assertRaises(PacketError):run(fixture(),require_h3=True)
    def test_batch_cli_scenarios_no_fake_ic(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);src=d/'input.json';out=d/'result.json'
            src.write_text(json.dumps(fixture()),encoding='utf8')
            self.assertEqual(main(['--packet',str(src),'--output',str(out)]),0)
            r=json.loads(out.read_text());self.assertEqual(r['scenario_count'],3)
            self.assertTrue(all(x['report']['ic_demo_percent'] is None for x in r['results']))
    def test_batch_duplicate_fails(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);p=d/'i.json';s=d/'s.json';p.write_text(json.dumps(fixture()));s.write_text(json.dumps([{'name':'A'},{'name':'A'}]))
            with self.assertRaises(PacketError):main(['--packet',str(p),'--scenarios',str(s)])
    def test_default_blocks_h3_fabrication_even_nonempty_h4(self):
        v={'portion_count':{'value':2,'unit':'count','state':'PLANNED','available_at_utc':TS,'source':'TEST'}}
        r=run(fixture(),h4a=v);self.assertEqual(r['H4']['a']['mechanisms']['portions']['dry_rice_per_portion_g'],80)
        self.assertIsNone(r['ic_demo_percent'])
    def test_real_q_effects_always_unvalidated(self):
        r=run(fixture());self.assertEqual(r['validated_Q_effects'],0);self.assertEqual(r['real_rice_trials'],0)
    def test_output_serializable(self):
        json.dumps(run(fixture()),allow_nan=False)

if __name__=='__main__':unittest.main()
