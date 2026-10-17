"""Generate executable artifacts for the RIZ112 v13 hierarchical lab, offline-only."""
from __future__ import annotations
import copy,json,sys,hashlib,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'step13'),str(ROOT/'step12'),str(ROOT/'step11')]
from causal_demo import simulate13,prepare
from hierarchy import build_registry
from full_variation_v12 import build_case
from scenario_factory import _set
STEP=ROOT/'step13'

def save(name,object):
 path=STEP/name;path.write_text(json.dumps(object,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8');return path

def run():
 reg=build_registry();save('REGISTRE_HIERARCHIE_112.json',reg)
 base=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text())
 pairs=[]
 for material in ['metal','iron','copper','ceramic_rated','wood_unrated']:
  q=copy.deepcopy(base);_set(q,'010',material)
  result=simulate13(q,1000,seed=20261017)
  pairs.append({'material':material,'heat_mode':'direct','ic_demo_percent':result['ic_demo_percent'],
    'qstar_p50':result['qstar_p50'],'effective_transfer_efficiency':result['upstream_driver_values']['transfer_efficiency'],
    'anticipated_events':result['anticipated_events'],'numeric_path_ids':result['case_paths_numeric_hypotheses']})
 q=copy.deepcopy(base);_set(q,'010','wood_unrated');_set(q,'016','indirect_water_bath')
 z=simulate13(q,1000,seed=20261017)
 pairs.append({'material':'wood_unrated','heat_mode':'indirect_water_bath',
   'ic_demo_percent':z['ic_demo_percent'],'qstar_p50':z['qstar_p50'],
   'effective_transfer_efficiency':z['upstream_driver_values']['transfer_efficiency'],
   'anticipated_events':z['anticipated_events'],'numeric_path_ids':z['case_paths_numeric_hypotheses']})
 save('MARMITES_SCENARIOS_CONTROLES.json',pairs)
 materials=['metal','copper','iron','ceramic_rated','wood_unrated']
 cases=[];cats=collections.Counter();ns=[]
 for i in range(100):
  p,sc=build_case(20261017,i,'coherent' if i%2==0 else 'mixed')
  mat=materials[i%len(materials)]
  _set(p,'010',mat)
  # Indirect branch for a subset of wood situations so the material alone does
  # not cause an unsupported-abstention or an always zero value.
  if mat=='wood_unrated' and i%10==4:
   _set(p,'016','indirect_water_bath')
  r=simulate13(p,draws=300,seed=20261017+i)
  ns.append(r['ic_demo_percent']);cats[mat]+=1
  cases.append({'name':p['prestart']['preparation_id'],'case_roles':112,'material':mat,
   'heating_mode':r['heat_route'],'rice_g':p['case_inputs']['001']['value'],
   'water_planned_g':p['case_inputs']['035']['value'],
   'ic_demo_percent':r['ic_demo_percent'],'real_ic_percent':None,
   'qstar_median':r['qstar_p50'],'assumed_missing_count':len(r['assumed_missing_inputs']),
   'plans_reconciled':len(r['adapted_plans']), 'risk_branches':sum(x['risk_predicted'] for x in r['policy_risk_forecasts']),
   'packet_sha256':hashlib.sha256(json.dumps(p,sort_keys=True,allow_nan=False).encode()).hexdigest()})
 summary={'schema':'riz112/stage13/population/assumptions-only','count':100,'draws_per_case':300,
  'status':'ALL_100_NUMERIC_DEMO__NONE_EMPIRICALLY_CALIBRATED',
  'cases_with_ic_demo':sum(x is not None for x in ns),'cases_ic_demo_above_25_percent':sum(x>=25 for x in ns),
  'cases_ic_demo_positive':sum(x>0 for x in ns),'max_ic_demo_percent':max(ns),
  'material_count':dict(cats),'cases':cases,'target_14_frozen':True,
  'scientific_ic':None,'real_trials':0,
  'warning':'These percentages are generated from disclosed hypothetical equations, model priors and demo thresholds, not measured rice quality.'}
 save('POPULATION_100_HIERARCHIQUE.json',summary)
 return pairs,summary

if __name__=='__main__':
 a,b=run();print(json.dumps({'paired':[{k:v for k,v in x.items() if k in ('material','heat_mode','ic_demo_percent','effective_transfer_efficiency')}for x in a],
 'population':{k:b[k] for k in ('count','cases_with_ic_demo','cases_ic_demo_above_25_percent','cases_ic_demo_positive','max_ic_demo_percent')}},indent=2))
