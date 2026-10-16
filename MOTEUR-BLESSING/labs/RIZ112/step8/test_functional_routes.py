import copy, json, sys, unittest, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step8'))
from functional_routes import analyze8, dispatch_hypothetical, GAP_IDS, SOURCE_IDS, FORECAST_IDS, ACTION_IDS, POLICY_IDS

def packet():
 return json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text(encoding='utf8'))

class CasesTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.p=packet();cls.x=analyze8(cls.p)
 def test_62_typing(self):
  self.assertEqual(len(GAP_IDS),62)
  self.assertEqual(tuple(map(len,[SOURCE_IDS,FORECAST_IDS,ACTION_IDS,POLICY_IDS])),(22,3,26,11))
  self.assertEqual(set(self.x['routes']),GAP_IDS)
 def test_scientific_gate(self):
  self.assertIsNone(self.x['calibrated_ic_percent'])
  self.assertIsNone(self.x['quality_probability'])
  self.assertEqual(self.x['actual_future_events_consumed'],0)
  self.assertEqual(self.x['label_cases_consumed_as_predictor'],0)
 def test_water_exact_margin(self):
  self.assertAlmostEqual(self.x['routes']['002']['decisions'][0]['measurement'],50.)
  p=packet();p['case_inputs']['002']['value']=50
  x=analyze8(p)
  self.assertEqual(x['routes']['002']['decisions'][0]['state'],'CONTRADICTED')
 def test_rinse_stock_known_vs_unknown_plan(self):
  p=packet();p['case_inputs']['005']['value']=0
  self.assertEqual(analyze8(p)['routes']['005']['decisions'][0]['state'],'CONTRADICTED')
  p['case_inputs']['005']['state']='UNKNOWN';p['case_inputs']['005']['value']=None
  self.assertEqual(analyze8(p)['routes']['005']['decisions'][0]['state'],'UNKNOWN')
 def test_lid_action_conflict(self):
  p=packet();p['case_inputs']['013']['value']=False
  x=analyze8(p);self.assertTrue(any(d['state']=='CONTRADICTED' for d in x['routes']['013']['decisions']))
  self.assertTrue(any(d['state']=='CONTRADICTED' for d in x['routes']['064']['decisions']))
 def test_geometry_positive(self):
  p=packet();p['case_inputs']['009'].update(state='ASSUMPTION',value=20)
  a=analyze8(p)['routes']['009']['derived']['pot_surface_cm2_geometry_only']
  self.assertAlmostEqual(a,100*math.pi,places=5)
  p['case_inputs']['009']['value']=40
  b=analyze8(p)['routes']['009']['derived']['pot_surface_cm2_geometry_only']
  self.assertAlmostEqual(b,4*a,places=5)
 def test_moisture_conditional_dry_mass(self):
  p=packet();p['case_inputs']['032'].update(state='ASSUMPTION',value=.12)
  d=analyze8(p)['routes']['032']['derived']
  self.assertAlmostEqual(d['dry_matter_g_assuming_wet_basis'],140.8)
  self.assertAlmostEqual(d['moisture_g_assuming_wet_basis'],19.2)
 def test_power_reliability_not_confused_with_outage(self):
  p=packet();p['case_inputs']['007'].update(state='ASSUMPTION',value=0)
  self.assertEqual(analyze8(p)['routes']['007']['decisions'][0]['state'],'RISK_DECLARED')
  self.assertIsNone(analyze8(p)['quality_probability'])
 def test_no_fake_altitude_physics(self):
  p=packet();p['case_inputs']['040'].update(state='ASSUMPTION',value=1200)
  x=analyze8(p);self.assertEqual(x['routes']['040']['decisions'][0]['state'],'SCENARIO_DIMENSION')
  self.assertNotIn('boiling_point_C',x['routes']['040'])
 def test_physical_proxy_varies_when_inputs_consistent(self):
  p=packet();a=analyze8(p)['routes']['043']['value']
  p['case_inputs']['037']['value']+=6
  p['prestart']['inputs']['water_initial_C']['value']+=6
  self.assertNotEqual(a,analyze8(p)['routes']['043']['value'])
  p=packet();a=analyze8(p)['routes']['046']['value']
  p['case_inputs']['014']['value']=1.9
  p['prestart']['inputs']['lid_multiplier']['value']=1.9
  self.assertNotEqual(a,analyze8(p)['routes']['046']['value'])
 def test_stability_refused(self):self.assertEqual(self.x['routes']['044']['state'],'NO_FORMULA')
 def test_plan_required_resource_absent(self):
  p=packet();p['case_inputs']['019']['value']=False
  self.assertTrue(any(d['state']=='CONTRADICTED' for d in analyze8(p)['routes']['050']['decisions']))
 def test_plan_sequence_not_hard_conflict(self):
  p=packet();p['action_plans']['059']['status']='PLANNED';p['action_plans']['051']['status']='NOT_PLANNED'
  gates=analyze8(p)['routes']['059']['decisions']
  self.assertTrue(any(d['state']=='SEQUENCE_HYPOTHESIS_ONLY' for d in gates))
 def test_policy_hypothetical_dispatch(self):
  p=packet();event=p['correction_policies']['086']['trigger'];results=dispatch_hypothetical(self.x,p,event)
  self.assertTrue(any(r['case']=='086' for r in results))
  self.assertEqual(dispatch_hypothetical(self.x,p,'ABSENT_EVENT'),[])
 def test_undefined_policy_cannot_be_dispatched(self):
  p=packet();p['correction_policies']['086'].update(status='UNDEFINED',trigger=None,planned_response=None)
  x=analyze8(p);self.assertEqual(x['routes']['086']['state'],'NO_POLICY')
  self.assertNotIn('086',[r['case'] for r in dispatch_hypothetical(x,p,'water_excess_reported')])
 def test_poststart_feature_cannot_enter(self):
  p=packet();p['realized_actions']={'065':'FAILED'}
  with self.assertRaises(ValueError):analyze8(p)
 def test_all_22_prestart_cases_have_observable_route_mutation(self):
  base=self.x
  for k in sorted(SOURCE_IDS):
   with self.subTest(k=k):
    p=packet();row=p['case_inputs'][k]
    if k in {'014','037','038'}:
     driver={'014':'lid_multiplier','037':'water_initial_C','038':'rice_initial_C'}[k]
     row['value']+=1
     p['prestart']['inputs'][driver]['value']+=1
    elif row['state']=='UNKNOWN':
     row['state']='ASSUMPTION'
     u=row['unit']
     row['value']= True if u=='bool' else 'example_category' if u is None else .15 if u=='fraction' else 10
    else:
     if row['unit']=='bool':row['value']=not row['value']
     elif row['unit'] is None:row['value']='different_category'
     else:row['value']=row['value']+1
    new=analyze8(p)
    self.assertNotEqual(base['routes'][k],new['routes'][k])
 def test_each_26_planned_action_mutation_changes_routing(self):
  for k in sorted(ACTION_IDS):
   with self.subTest(k=k):
    p=packet();row=p['action_plans'][k]
    row['status']='PLANNED' if row['status']!='PLANNED' else 'NOT_PLANNED'
    self.assertNotEqual(self.x['routes'][k],analyze8(p)['routes'][k])
 def test_each_11_policy_mutation_changes_routing(self):
  for k in sorted(POLICY_IDS):
   with self.subTest(k=k):
    p=packet();row=p['correction_policies'][k]
    if row['status']=='DEFINED':row.update(status='UNDEFINED',trigger=None,planned_response=None)
    else:row.update(status='DEFINED',trigger='hypothetical_event',planned_response='hypothetical_response')
    self.assertNotEqual(self.x['routes'][k],analyze8(p)['routes'][k])

if __name__=='__main__':unittest.main()
