#!/usr/bin/env python3
"""RIZ-112 D025/H2: nested conditions + prospective (not observed) corrective policy.

ALL numbers are for Q*_DEMO, which is a synthetic proxy, NOT true rice success.
Different planned futures are integrated by Monte-Carlo draws using an explicit
pre-T0 action policy. No post-start measurements are accepted as input.
"""
from __future__ import annotations
import copy, json, math, random, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step13'))
from hierarchical_engine import evaluate, _set, HierarchyError
sys.path.insert(0,str(ROOT/'step9'))
from ic_simulation_v1 import sample_packet, proxy_scores, vals_from_core, CONTRACT
from ic_simulation_v1 import physical_analyze

RICE_PATHS={
 'water_capacity_g_per_g':('033','water_capacity_g_per_g',0.2,3.5),
 'hot_time_needed_min':('034','hot_time_needed_min',1,120),
 'surface_starch_index':('030','surface_starch_index',0,1),
 'rinse_removal_fraction':('054','rinse_removal_fraction',0,1),
}

def number(value,lo,hi,name):
 if type(value) not in (int,float) or not math.isfinite(value) or not lo<=value<=hi:
  raise HierarchyError(f'{name}: finite number required in [{lo},{hi}]')
 return float(value)

def evaluate_branches(packet:dict, *, material:str, lid_present:bool|None=None,
    diameter_cm:float=18,wall_mm:float=2,water_g:float|None=None,
    rice_profile:dict|None=None, conditional_water_policy:dict|None=None,
    heat_path:str='direct',draws:int=700,seed:int=20261017,
    measured_k:float|None=None,contact_resistance_K_W:float=.065,
    driving_deltaT_K:float=24.) -> dict:
 """Pre-T0 model comparison with common uncertainty for no-policy / policy paths.

 `conditional_water_policy` is not a future observation. It declares an intended
 rule + available stock and hypothetical adherence probability at T0.
 """
 if type(draws)!=int or not 100<=draws<=20000:raise HierarchyError('draws 100..20000')
 if type(seed)!=int or seed<0:raise HierarchyError('seed nonnegative integer')
 if rice_profile is not None and (not isinstance(rice_profile,dict) or not set(rice_profile)<=set(RICE_PATHS)):
  raise HierarchyError('unknown rice profile subparameter')
 start=evaluate(packet,material=material,lid_present=lid_present,
   diameter_cm=diameter_cm,wall_mm=wall_mm,water_g=water_g,
   heat_path=heat_path,draws=100,seed=seed,measured_k=measured_k,
   contact_resistance_K_W=contact_resistance_K_W,
   driving_deltaT_K=driving_deltaT_K,return_prepared_packet=True)
 if start['status']=='UNSAFE_DIRECT_HEAT_PATH':
  return {'status':'UNSAFE_PATH_WITHOUT_SAFE_PROSPECTIVE_MODEL',
    'scientific_ic_percent':None,'ic_demo_percent':None,
    'reason':'Unrated wooden vessel on direct heat: do not test physically; no valid safe process model.',
    'anticipations':start['anticipations']}
 if start['status']!='DEMONSTRATION_ASSUMPTIONS_ONLY_NOT_REAL_Q':
  return {'status':'BASELINE_NOT_ESTIMABLE','scientific_ic_percent':None,
    'ic_demo_percent':None,'details':start.get('details',[])}
 work=start['prepared_packet']
 lineage=list(start['anticipations']);root_sids={'009','010','011','013','014','035','041','042'}
 if rice_profile:
  for name,val in rice_profile.items():
   case,field,lo,hi=RICE_PATHS[name]
   value=number(val,lo,hi,name)
   # Actions must not be silently converted into initial observations.
   if case=='054':
    if work['action_plans']['054']['status']!='PLANNED':
     raise HierarchyError('rinse fraction can be changed only with predeclared rinsing plan')
    work['prestart']['inputs'][field]['value']=value
    work['prestart']['inputs'][field]['source']='PRE_T0_RICE_PROFILE_ASSUMPTION'
   else:_set(work,case,value,field)
   root_sids.add(case)
   lineage.append({'id':'RICE_SUBPARAMETER_TO_PHYSICAL_FIELD','case':case,'field':field,
      'value':value,'model_status':'HYPOTHESIS_NOT_CALIBRATED'})
 policy=None
 if conditional_water_policy is not None:
  if not isinstance(conditional_water_policy,dict) or set(conditional_water_policy)!={'trigger_shortfall_g','dose_g','adherence_probability'}:
   raise HierarchyError('water policy must declare exactly trigger_shortfall_g,dose_g,adherence_probability')
  t=number(conditional_water_policy['trigger_shortfall_g'],0,10000,'trigger_shortfall_g')
  d=number(conditional_water_policy['dose_g'],0.001,10000,'dose_g')
  a=number(conditional_water_policy['adherence_probability'],0,1,'adherence_probability')
  base_policy=work['correction_policies']['087']
  if base_policy['status']!='DEFINED':raise HierarchyError('case 087 must be predeclared')
  # The policy is predeclared explicitly. None of its triggers is a realized measurement.
  base_policy['trigger']='modeled_shortfall_not_observed'
  base_policy['planned_response']='use_predeclared_extra_water_if_available'
  reserve_row=work['case_inputs']['002']
  stock=reserve_row['value']
  if reserve_row['state']=='UNKNOWN' or type(stock) not in (float,int) or not math.isfinite(stock) or stock<0:
   stock=None
  policy={'trigger_shortfall_g':t,'requested_dose_g':d,'adherence_probability':a,
          'stock_g_prestart':stock,'source_case':'087','resource_case':'002',
          'state':'PRE_T0_DECLARED_POLICY_NOT_REALIZED'}
  lineage.append({'id':'ANTICIPATE_WATER_SHORTFALL','if':'modeled W_shortfall > trigger',
     'then':'add at most remaining water stock, if planned and hypothetically executed',
     'dependency_cases':['001','002','033','034','035','041','042','045','046','047','087'],
     'status':'PROSPECTIVE_UNVALIDATED_BRANCH'})
  root_sids.update({'002','087'})
 dist=json.loads(CONTRACT.read_text())['uncertainty_distribution']
 scales=json.loads(CONTRACT.read_text())['proxy_scales']
 rng=random.Random(seed)
 policy_rng=random.Random(seed ^ 0x5A27D025)
 base_success=0;policy_success=0;event_count=0;executed_count=0
 deficits=[];available_dose=[];base_quality=[];corrected_quality=[]
 # Common random numbers make contrasts much less noisy; policy decision uses
 # hypothetical latent future states, never observed data after T0.
 for _ in range(draws):
  sampled=sample_packet(work['prestart'],rng,dist)
  nodes=vals_from_core(physical_analyze(sampled))
  q0=proxy_scores(nodes,sampled,scales)[1];q1=q0
  deficit=max(0,nodes['W_shortfall'])
  deficits.append(deficit)
  if policy is not None and deficit>policy['trigger_shortfall_g']:
   event_count+=1
   stock=policy['stock_g_prestart']
   # No additional quantity if stock availability is unknown; never assume infinite water.
   extra=max(0,min(policy['requested_dose_g'],stock-sampled['inputs']['water_added_g']['value'])) if stock is not None else 0
   available_dose.append(extra)
   if extra>0 and policy_rng.random()<policy['adherence_probability']:
    executed_count+=1
    branch=copy.deepcopy(sampled)
    branch['inputs']['water_added_g']['value']+=extra
    after=vals_from_core(physical_analyze(branch))
    q1=proxy_scores(after,branch,scales)[1]
  base_quality.append(q0);corrected_quality.append(q1)
  base_success+=q0>=85;policy_success+=q1>=85
 def pct(n):return round(n/draws*100,2)
 return {'schema':'riz112/hierarchical-prospective-branches/h2',
   'status':'DEMONSTRATION_ASSUMPTIONS_ONLY_NOT_REAL_Q',
   'baseline_ic_demo_percent':pct(base_success),
   'conditional_plan_ic_demo_percent':pct(policy_success),
   'conditional_plan_delta_percentage_points':round((policy_success-base_success)/draws*100,2),
   'scientific_ic_percent':None,'real_success_ic_percent':None,
   'draws':draws,'seed':seed,
   'forecast_conditional_events':event_count,
   'hypothetical_policy_executions':executed_count,
   'expected_water_shortfall_g':round(sum(deficits)/draws,3),
   'avg_feasible_extra_water_g_when_triggered':round(sum(available_dose)/len(available_dose),3) if available_dose else 0,
   'baseline_median_q_demo':round(sorted(base_quality)[draws//2],2),
   'policy_median_q_demo':round(sorted(corrected_quality)[draws//2],2),
   'thermal_path':start['thermal_path'],
   'rice_profile_subparameters':rice_profile or {},
   'policy':policy,
   'trace':lineage,
   'active_parent_cases':sorted(root_sids),
   'targets_used_as_predictors':0,
   'post_T0_measured_values_used':0,
   'model_assumption_warnings':['Thresholds, thermal material model, and adherence probability are uncalibrated',
      'Branching on a SIMULATED future shortfall is a prestart forecast, NOT a future observation',
      'Not a cooking recipe, food-safety certification or empirically calibrated chance of good rice']}

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--material',default='copper');ap.add_argument('--water',type=float,default=180)
 ap.add_argument('--dose',type=float,default=65);ap.add_argument('--draws',type=int,default=800)
 a=ap.parse_args();p=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text())
 print(json.dumps(evaluate_branches(p,material=a.material,water_g=a.water,diameter_cm=18,wall_mm=2,
  conditional_water_policy={'trigger_shortfall_g':5,'dose_g':a.dose,'adherence_probability':.75},draws=a.draws),indent=2,ensure_ascii=False))
