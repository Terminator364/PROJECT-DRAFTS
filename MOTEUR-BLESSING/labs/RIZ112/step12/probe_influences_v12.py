#!/usr/bin/env python3
"""Paired one-at-a-time case interventions: trace effects vs real numeric Q* effects.

Audit BOTH reference baselines to mitigate one-scenario false non-influence.
No inference about effects on actual food quality.
"""
from __future__ import annotations
import copy, json, sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step10'))
from case_intervention_audit import intervention, PACKET
from ic_integrity_v10 import audited_simulate
sys.path.insert(0,str(ROOT/'step6'))
from engine112 import analyze112, PRESTART,FORECAST,ACTIONS,POLICIES,OUTCOMES
sys.path.insert(0,str(ROOT/'step8'))
from functional_routes import analyze8
sys.path.insert(0,str(ROOT/'step11'))
from scenario_factory import _set


def baselines():
 a=copy.deepcopy(PACKET)
 b=copy.deepcopy(PACKET)
 _set(b,'035',250.)
 _set(b,'041',460.)
 return (('A',a),('B',b))

def audit(draws=100,seed=20261017):
 if not isinstance(draws,int) or draws<100:raise ValueError('>=100 samples')
 entries=[]
 bs=[]
 for name,p in baselines():
  bs.append((name,p,analyze112(p),analyze8(p),audited_simulate(p,draws=draws,seed=seed)))
 for i in range(1,113):
  cid=f'{i:03}'
  role='DATA' if cid in PRESTART else 'DERIVED' if cid in FORECAST else 'ACTION_PLAN' if cid in ACTIONS else 'POLICY' if cid in POLICIES else 'QUALITY_TARGET'
  observations=[]
  for name,p,base112,base8,base_score in bs:
   q=copy.deepcopy(p);t=intervention(cid,q)
   e={'baseline':name,'kind':t,'status':None,'numeric_ic_changed':False,
      'operational_effect':False,'contract_trace_changed':False,'error':None}
   if t=='DERIVED_NOT_DIRECTLY_MUTABLE':
    e['status']='DERIVED_RECALCULATED_NOT_FREE_INPUT';observations.append(e);continue
   try:
    a=analyze112(q);b=analyze8(q)
    oldnode=next(x for x in base112['graph']['all_112_case_trace'] if x['id']==cid)
    newnode=next(x for x in a['graph']['all_112_case_trace'] if x['id']==cid)
    e['contract_trace_changed']=oldnode!=newnode
    e['operational_effect']= b['routes'].get(cid)!=base8['routes'].get(cid) if cid in b['routes'] else False
    r=audited_simulate(q,draws=draws,seed=seed)
    e['status']=r['status']
    if r.get('ic_demo_percent') is not None and base_score.get('ic_demo_percent') is not None:
     e['numeric_ic_changed']=r['ic_demo_percent']!=base_score['ic_demo_percent']
    e['target_guard_activated']=r['status']=='ABSTAIN_TARGET_CONTRACT_CHANGED'
   except (ValueError,TypeError,KeyError,ZeroDivisionError) as ex:
    e['status']='INVALID_COUNTERFACTUAL';e['error']=type(ex).__name__+': '+str(ex)[:130]
   observations.append(e)
  if cid in OUTCOMES:
   category='TARGET_DEFINITION_LOCKED_NOT_INPUT'
  elif cid in FORECAST:
   category='DERIVED_OUTPUT_NOT_INDEPENDENT_RANDOM_INPUT'
  elif any(v['numeric_ic_changed'] for v in observations):
   category='CHANGES_ASSUMED_DEMO_IC_FOR_TESTED_PERTURBATION'
  elif any(v['status'].startswith('ABSTAIN') or v['status']=='INVALID_COUNTERFACTUAL' for v in observations):
   category='CHANGES_ELIGIBILITY_OR_INVALIDATES_ASSUMPTIONS'
  elif any(v['operational_effect'] for v in observations):
   category='CHANGES_OPERATIONAL_GATES_NOT_CALIBRATED_Q'
  else:
   category='NOT_DEMONSTRATED_TO_CHANGE_IC_OR_GATE'
  entries.append({'case':cid,'role':role,'category':category,'trials':observations,
   'effect_on_real_quality_proven':False})
 return {'schema':'riz112/stage12/counterfactual-2-baselines/v1','baselines':['A','B'],'draws_per_trial':draws,
  'cases':entries,'categories':dict(Counter(x['category'] for x in entries)),
  'tested_counterfactuals':112*2,'real_trials':0,'scientific_ic':None,
  'warning':'Affects SIMULATED Q* or a gate, not necessarily real rice success; 14 outcomes are targets, not predictors.'}

if __name__=='__main__':
 d=audit()
 print(json.dumps(d,indent=2,ensure_ascii=False))
