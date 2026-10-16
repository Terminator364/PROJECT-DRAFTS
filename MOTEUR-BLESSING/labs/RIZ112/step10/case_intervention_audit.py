#!/usr/bin/env python3
"""Perturb every RIZ112 case; measure actual output differences, not rhetorical coverage."""
import copy,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step9'))
from ic_simulation_v1 import simulate
sys.path.insert(0,str(ROOT/'step6'))
from engine112 import PRESTART,FORECAST,ACTIONS,POLICIES,OUTCOMES,DRIVER,analyze112
sys.path.insert(0,str(ROOT/'step8'))
from functional_routes import analyze8
PACKET=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text())
CONTRACT=json.loads((ROOT/'step9/DEMONSTRATION_CONTRACT.json').read_text())

def alternate(case,v,unit):
 if v is None:
  if unit=='bool': return True
  if unit is None:return 'assumed_alternative'
  if unit=='fraction':return .3
  if unit=='degC':return 23.0
  return 1.0
 if type(v)==bool:return not v
 if type(v)==str:return ('ALT_'+v) if not v.startswith('ALT_') else v+'2'
 if unit=='fraction':return min(.95,max(.05, float(v)*.8 if v>0 else .25))
 if unit=='degC':return float(v)+4
 return (float(v)*1.2) if v else 1.0

def intervention(case,p):
 if case in PRESTART:
  row=p['case_inputs'][case]; v=alternate(case,row['value'],row['unit'])
  row['value']=v; row['state']='ASSUMPTION';row['source']='SYNTHETIC_COUNTERFACTUAL'
  if case in DRIVER:
   key=DRIVER[case];p['prestart']['inputs'][key]['value']=v
   p['prestart']['inputs'][key]['source']='SYNTHETIC_COUNTERFACTUAL'
  return 'PRESTART_INTERVENTION'
 if case in ACTIONS:
  row=p['action_plans'][case];row['status']='NOT_PLANNED' if row['status']=='PLANNED' else 'PLANNED';return 'PLAN_INTERVENTION'
 if case in POLICIES:
  row=p['correction_policies'][case];
  if row['status']=='DEFINED':row.update(status='UNDEFINED',trigger=None,planned_response=None)
  else:row.update(status='DEFINED',trigger='hypothetical_event_before_cooking',planned_response='assumed_response_only')
  return 'POLICY_INTERVENTION'
 if case in OUTCOMES:
  row=p['target_contract'][case]
  if row['status']=='DRAFT':row.update(status='UNDEFINED',measurement_definition=None)
  else:row.update(status='DRAFT',measurement_definition='hypothetical quality definition changed')
  return 'TARGET_SPEC_INTERVENTION'
 return 'DERIVED_NOT_DIRECTLY_MUTABLE'

def run(draws=400):
 baseline=simulate(PACKET,CONTRACT,draws,20261016)
 b6=analyze112(PACKET);b8=analyze8(PACKET)
 entries=[]
 for i in range(1,113):
  k=f'{i:03}';p=copy.deepcopy(PACKET)
  role=intervention(k,p)
  item={'case':k,'intervention_role':role,'input_changed':p!=PACKET,'status':'NOT_RUN',
        'ic_demo_changed':False,'ic_demo_before':baseline['ic_demo_percent'],'ic_demo_after':None,
        'scientific_ic':None,'error':None,'operational_output_changed':False,
        'source_or_target_trace_changed':False}
  if role=='DERIVED_NOT_DIRECTLY_MUTABLE':
   item['status']='DERIVED_COMPUTED_ONLY';entries.append(item);continue
  try:
   q6=analyze112(p);q8=analyze8(p)
   trace_prev=next(x for x in b6['graph']['all_112_case_trace'] if x['id']==k)
   trace_new=next(x for x in q6['graph']['all_112_case_trace'] if x['id']==k)
   item['source_or_target_trace_changed']=trace_new!=trace_prev
   route_prev=b8['routes'].get(k);route_new=q8['routes'].get(k)
   item['operational_output_changed']=(route_new != route_prev) if route_prev is not None else False
   s=simulate(p,CONTRACT,draws,20261016)
   item['ic_demo_after']=s['ic_demo_percent']
   item['ic_demo_changed']=s['ic_demo_percent'] != baseline['ic_demo_percent']
   item['status']='ABSTAIN' if s['ic_demo_percent'] is None else 'IC_CHANGED' if item['ic_demo_changed'] else 'IC_UNCHANGED'
  except Exception as ex:
   item['status']='FAILED_INTERVENTION';item['error']=type(ex).__name__+': '+str(ex)[:190]
  entries.append(item)
 from collections import Counter
 by_status=dict(Counter(x['status'] for x in entries))
 by_role={s:sum(x['intervention_role']==s for x in entries) for s in set(x['intervention_role'] for x in entries)}
 return {'schema':'riz112/step10/experimental-intervention-audit/v1','baseline_demo_percent':baseline['ic_demo_percent'],
  'simulation_draws':draws,'timestamp_reused_hypothetical_fixture':'2026-10-16T12:00:00Z',
  'description':'One-at-a-time perturbations at baseline A, not an empirical effect / causal law; fixed MC seed',
  'counts':{'cases':len(entries),'statuses':by_status,'roles':by_role,'numeric_ic_changed':sum(x['ic_demo_changed'] for x in entries),
   'operational_trace_changed':sum(x['operational_output_changed'] for x in entries),
   'per_case_trace_changed':sum(x['source_or_target_trace_changed'] for x in entries),
   'mutations_failed':sum(x['status']=='FAILED_INTERVENTION' for x in entries)},'cases':entries,
  'caution':'Unknown/unfinished future-label targets are NOT quantitative IC predictors; no calibration. The statuses are local sensitivity only.'}
if __name__=='__main__':
 r=run();print(json.dumps(r['counts'],indent=2))
 path=ROOT/'step10'/'INTERVENTIONS_112_STAGE9.json';path.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
