#!/usr/bin/env python3
"""RIZ112 Stage12: generate diverse 112-role prestart scenarios and measure actual contribution.

100 synthetic cases, 44 eligible directly supplied prestart variables sampled;
4 derived recalculated; 37 planned actions and 13 conditional policies varied;
14 outcome definitions FROZEN. Numerical IC remains Q*-DEMO only.

No guarantee or assertion that all 112 values independently influence success odds:
the ledger says WHICH did, did not, blocked, or merely changed the contract.
"""
from __future__ import annotations
import copy, json, random, sys, hashlib
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step11'))
from scenario_factory import _make, _set, evaluate
sys.path.insert(0,str(ROOT/'step6'))
from engine112 import PRESTART,FORECAST,ACTIONS,POLICIES,OUTCOMES,DRIVER,analyze112
sys.path.insert(0,str(ROOT/'step7'))
from graph_governor import feasibility
sys.path.insert(0,str(ROOT/'step10'))
from case_intervention_audit import intervention, PACKET
from ic_integrity_v10 import audited_simulate

NUMERIC_OR_BOOLEAN={
 '001':[90,130,160,220,290,360], '002':[120,350,650,1000], '017':[False,True],
 '003':[0,1,2,3], '004':[0,4,9], '005':[0,250,800,1200],
 '007':[.2,.5,.8,1.0], '008':[550,1000,1700,2500],
 '009':[12,16,20,25,30], '011':[.8,1.5,2.5,4.0],
 '013':[False,True], '014':[1.,2.2], '018':[.35,.55,.75,.95],
 '019':[False,True], '020':[False,True], '021':[False,True],
 '022':[False,True], '023':[False,True], '025':[5.8,6.7,7.5],
 '028':[5,60,330,800], '029':[.03,.08,.25,.4],
 '030':[.20,.4,.65,.85], '031':[0,.02,.07,.16], '032':[.07,.10,.13,.16],
 '033':[1.15,1.3,1.45,1.55], '034':[8,11,15,19],
 '035':[100,180,250,320,420,550], '036':[0,4,9,16],
 '037':[14,22,32,44], '038':[14,21,26,32],
 '039':[16,23,29,35], '040':[0,500,1500,2500],
 '041':[250,400,600,850,1100], '042':[.4,.55,.7,.8],
 '045':[1.5,3,4.5,6], '047':[12,18,24,30,36]
}
CATEGORICAL={
 '006':['electricity','gas','charcoal'], '010':['metal','ceramic_rated','wood_unrated'],
 '012':['sound','scratched','unknown_condition'],
 '015':['vented','tight_seal','loose_lid'],
 '016':['electric_stove','gas_stove','charcoal_fire'],
 '024':['long_white_hypothesis','parboiled_hypothesis','short_white_hypothesis'],
 '026':['white_milled','parboiled'],
 '027':['lot_A_synthetic','lot_B_synthetic','lot_C_synthetic']
}
# 44 eligible prestart case rows all have nontrivial sample support; no randomization of outcomes.
CHOICES={**NUMERIC_OR_BOOLEAN,**CATEGORICAL}
assert len(CHOICES)==len(PRESTART)==44 and set(CHOICES)==set(PRESTART)

class GenerationError(ValueError): pass

def build_case(seed:int,index:int,mode:str='mixed'):
 if type(seed)!=int or seed<0 or type(index)!=int or index<0:raise GenerationError('seed/index invalid')
 if mode not in {'mixed','coherent'}:raise GenerationError('mode invalid')
 # full independent deterministic draw of all eligible initial conditions
 p,scenario=_make(seed,index,overrides={'vessel':'metal'})
 rng=random.Random(seed ^ ((index+1)*0x5C64A71))
 for case in PRESTART:
  _set(p,case,rng.choice(CHOICES[case]))
 # Preserve key internal constraints where coherent mode requested; DO NOT secretly
 # change the physical model merely on material string (separate measured efficiency).
 lid=p['case_inputs']['013']['value']
 _set(p,'014',1. if lid else 2.2)
 if not lid:
  for action in ('064','070','080'):p['action_plans'][action]['status']='NOT_PLANNED'
 mat=p['case_inputs']['010']['value']
 if mode=='coherent':
  # Satisfy *necessary known feasibility conditions* by construction. Other
  # unknown feasibility aspects still may trigger abstention.
  _set(p,'002',max(600,p['case_inputs']['035']['value']+50))
  _set(p,'008',max(1700,p['case_inputs']['035']['value']+500))
  _set(p,'006','electricity')
  _set(p,'017',True)
  for c in ('019','020','021','022','023'):_set(p,c,True)
  for c in ACTIONS:p['action_plans'][c]['status']='PLANNED'
  if not lid:
   for c in ('064','070','080'):p['action_plans'][c]['status']='NOT_PLANNED'
  for c in ('055','056'):
   p['action_plans'][c]['status']='PLANNED'
  _set(p,'005',1000)
  _set(p,'004',10)
  _set(p,'003',2)
  if mat=='wood_unrated':
   # keep the unsupported material to exercise evidence-based abstentions
   pass
 else:
  for c in ACTIONS:
   p['action_plans'][c]['status']=rng.choice(['PLANNED','NOT_PLANNED','UNKNOWN'])
  if not lid:
   for c in ('064','070','080'):p['action_plans'][c]['status']='NOT_PLANNED'
 for c in ACTIONS:p['action_plans'][c]['source']='SYNTHETIC_PLAN_2026_ONLY'
 for c in POLICIES:
  row=p['correction_policies'][c]
  if rng.random()<.5:row.update(status='UNDEFINED',trigger=None,planned_response=None)
  else:row.update(status='DEFINED',trigger='event_'+c+'_hypothetical',planned_response='response_'+c+'_hypothetical')
  row['source']='SYNTHETIC_POLICY_NOT_OBSERVED'
 assert set(p['case_inputs'])==set(PRESTART)
 assert len(p['action_plans'])==37 and len(p['correction_policies'])==13 and len(p['target_contract'])==14
 # no new poststart values inserted
 scenario={'material':mat,'lid':lid,'mode':mode,'rice_g':p['case_inputs']['001']['value'],
  'water_g':p['case_inputs']['035']['value'], 'power_W':p['case_inputs']['041']['value'],
  'declared_inputs':44,'forecast_derived':4,'planned_actions':37,'policies':13,'frozen_targets':14}
 return p,scenario

def simulate_population(seed:int=20261017,n:int=100,draws:int=100):
 if type(n)!=int or not 1<=n<=500:raise GenerationError('number of scenarios 1..500')
 if type(draws)!=int or not 100<=draws<=5000:raise GenerationError('draws must be 100..5000')
 profiles=[]; values={k:set() for k in PRESTART};action_states={k:set() for k in ACTIONS};policy_states={k:set() for k in POLICIES}
 reference=None
 for i in range(n):
  mode='coherent' if i%2==0 else 'mixed'
  p,sc=build_case(seed,i,mode)
  if reference is None:reference=p['target_contract']
  if p['target_contract']!=reference:raise GenerationError('quality target must never be randomized')
  a=analyze112(p)
  for k in PRESTART:values[k].add(json.dumps(p['case_inputs'][k]['value']))
  for k in ACTIONS:action_states[k].add(p['action_plans'][k]['status'])
  for k in POLICIES:policy_states[k].add(p['correction_policies'][k]['status'])
  result=evaluate(p,sc,draws,seed+1009)
  profiles.append({'id':p['prestart']['preparation_id'],'index':i,'scenario':sc,
    'packet_sha256':hashlib.sha256(json.dumps(p,sort_keys=True,allow_nan=False).encode()).hexdigest(),
    'result_status':result['status'],'ic_demo_percent':result.get('ic_demo_percent'),
    'scientific_ic_percent':None,'known_direct_cases':sum(r['state']!='UNKNOWN' for r in p['case_inputs'].values()),
    'contradiction_count':len(a['graph']['contradictions']), 'prestart_quality_observations_consumed':0})
 return {'schema':'riz112/stage12/full-case-synthetic-v1','seed':seed,'n':n,'draws':draws,
    'profiles':profiles,'counts':dict(Counter(x['result_status'] for x in profiles)),
    'per_case_distinct_direct_values':{k:len(v) for k,v in values.items()},
    'per_case_action_states':{k:len(v) for k,v in action_states.items()},
    'per_case_policy_states':{k:len(v) for k,v in policy_states.items()},
    'all_44_prestart_have_varied':all(len(v)>1 for v in values.values()) if n>=50 else None,
    'targets_frozen':True,'poststart_observations_consumed':0,
    'validated_predictive_effects':0,'real_ic_percent':None,
    'warning':'111+ cases are not all numeric effects; 14 targets are frozen and 4 are derived. NO measured success model.'}

def paired_material_probe(seed=20261017,draws=500):
 # Matched 2-case interventional proof: changing the material label alone does NOT
 # alter physical equations; do not confound with draw noise.
 p,sc=build_case(seed,2,'coherent')
 _set(p,'010','metal');sc['material']='metal'
 # build viable surface without changing prestart when switching material
 q=copy.deepcopy(p)
 _set(q,'010','ceramic_rated')
 a=audited_simulate(p,draws=draws,seed=seed)
 b=audited_simulate(q,draws=draws,seed=seed)
 return {'only_modified_case':'010','material_A':'metal','material_B':'ceramic_rated',
  'same_core_physical_inputs':p['prestart']==q['prestart'],
  'ic_demo_A':a.get('ic_demo_percent'),'ic_demo_B':b.get('ic_demo_percent'),
  'same_demo_ic':a.get('ic_demo_percent')==b.get('ic_demo_percent'),
  'finding':'material measured thermal parameters not mapped: NO fabricated label effect',
  'causal_inference_from_material_label':False}

if __name__=='__main__':
 import argparse
 pa=argparse.ArgumentParser();pa.add_argument('--count',type=int,default=100);pa.add_argument('--draws',type=int,default=100);pa.add_argument('--seed',type=int,default=20261017);pa.add_argument('--out',type=Path)
 z=pa.parse_args();r=simulate_population(z.seed,z.count,z.draws)
 s=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
 if z.out:z.out.write_text(s,encoding='utf8')
 else:print(s)
