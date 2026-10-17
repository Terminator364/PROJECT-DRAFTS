"""RIZ112 V13: correlated *hypothetical* physical submechanisms and anticipations.

Scientific status: DEMO ONLY. Material conductivities approximate indicative
values, NOT a calibrated vessel heat-transfer or rice-quality model. Do NOT
transfer numeric outputs to MOTEUR MATRICE. Outcomes are not predictor inputs.
"""
from __future__ import annotations
import copy, json, math, random, sys, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'step9'),str(ROOT/'step6'),str(ROOT/'step12'),str(ROOT/'reference'/'step4')]
from hierarchy import build_registry
from riz112 import analyze as physical_analyze
from ic_simulation_v1 import sample_packet,vals_from_core,proxy_scores,clamp
from engine112 import PRESTART,FORECAST,ACTIONS,POLICIES,OUTCOMES,DRIVER,check_keys,timecheck,utc,digest
from full_variation_v12 import build_case

# Approximate material parameters ONLY TO ILLUSTRATE mechanistic propagation.
# Real cookware uses composites, contact resistance, geometry, linings, etc.
MATERIALS={
 'metal':{'conductivity_W_mK':70.0,'direct_heat_compatible':True,'name':'generic metal assumption'},
 'iron':{'conductivity_W_mK':80.0,'direct_heat_compatible':True,'name':'iron assumption'},
 'copper':{'conductivity_W_mK':390.0,'direct_heat_compatible':True,'name':'copper assumption'},
 'ceramic_rated':{'conductivity_W_mK':2.0,'direct_heat_compatible':True,'name':'rated ceramic assumption'},
 'wood_unrated':{'conductivity_W_mK':0.16,'direct_heat_compatible':False,'name':'wood container assumption'} }
CONTRACT=ROOT/'step9/DEMONSTRATION_CONTRACT.json'

class SyntheticContractError(ValueError):pass

# Every fallback is an EXPLICIT synthetic assumption, never an imputation
# of an unknown measured value to zero. Callers see the complete assumptions.
ASSUMED_DEFAULTS={
 '002':350.,'005':1000.,'006':'electricity','007':.9,'008':1700.,
 '009':20.,'010':'metal','011':2.,'012':'sound','013':True,
 '014':1.,'015':'vented','016':'electric_stove','017':True,
 '018':.65,'021':True,'024':'long_white_hypothesis',
 '025':6.7,'026':'white_milled','029':.04,'030':.4,
 '031':.01,'032':.1,'033':1.35,'034':12.,
 '035':300.,'039':25.,'041':550.,'045':4.0
}

def num(packet,case,default=None):
 r=packet['case_inputs'][case];v=r['value']
 if v is None:
  if case in ASSUMED_DEFAULTS:return ASSUMED_DEFAULTS[case]
  if default is not None:return default
  raise SyntheticContractError('unknown with no declared synthetic prior: '+case)
 return v

def planned(packet,id):return packet['action_plans'][id]['status']=='PLANNED'
def defined(packet,id):return packet['correction_policies'][id]['status']=='DEFINED'

def normative_anticipated(packet):
 """Scenario resolution: prefer declared physical reality to impossible plan;
      no future observations, no automatic abandonment on a mismatched plan."""
 q=copy.deepcopy(packet);altered=[]
 lid=bool(num(q,'013'))
 if not lid:
  for a in ('064','070','080'):
   if planned(q,a):q['action_plans'][a]['status']='NOT_PLANNED';altered.append({'case':a,'reason':'lid missing: planned action cannot execute'})
 if not bool(num(q,'017')) and planned(q,'068'):
  q['action_plans']['068']['status']='NOT_PLANNED';altered.append({'case':'068','reason':'power control missing'})
 for tool,action in [('019','050'),('020','053'),('021','057'),('022','077'),('023','081')]:
  if not bool(num(q,tool)) and planned(q,action):
   q['action_plans'][action]['status']='NOT_PLANNED';altered.append({'case':action,'reason':'tool missing: action not executable'})
 for a in ('055','056'):
  if num(q,'005')<=0 and planned(q,a):
   q['action_plans'][a]['status']='NOT_PLANNED';altered.append({'case':a,'reason':'rinse water unavailable'})
 return q,altered

def _input(pre,name,val):
 if not math.isfinite(val):raise SyntheticContractError('nonfinite '+name)
 pre['inputs'][name]['value']=round(float(val),8)

def _get(pre,name):return float(pre['inputs'][name]['value'])

def prepare(packet:dict):
 """Transform semantic subparameters to physical parameters; use bounded
    resistance-in-series and conservation, no 'magic material bonuses'."""
 if not isinstance(packet,dict) or set(packet)!={'schema','prestart','case_inputs','action_plans','correction_policies','target_contract'}:
  raise SyntheticContractError('Invalid 112-case packet')
 if len(packet['case_inputs'])!=44 or len(packet['action_plans'])!=37 or len(packet['correction_policies'])!=13 or len(packet['target_contract'])!=14:
  raise SyntheticContractError('112 role contract incomplete')
 # Temporal contract: never feed quality labels into features.
 t=utc(packet['prestart']['freeze_utc'],'freeze');start=utc(packet['prestart']['start_utc'],'start')
 if t>=start:raise SyntheticContractError('prestart freeze after start')
 for section in ('case_inputs','action_plans','correction_policies'):
  for case,row in packet[section].items():
   if 'available_at_utc' in row and utc(row['available_at_utc'],case)>t:raise SyntheticContractError('future input '+case)
 gate=json.loads((ROOT/'step10/GATE_V10.json').read_text(encoding='utf8'))
 if digest(packet['target_contract'])!=gate['demo_quality_target_sha256']:
  raise SyntheticContractError('14 target definitions do not match the frozen demo target')
 q,adjusted=normative_anticipated(packet)
 assumed_missing={cid:ASSUMED_DEFAULTS[cid] for cid in ASSUMED_DEFAULTS if packet['case_inputs'][cid]['value'] is None}
 material=num(q,'010')
 if material not in MATERIALS:raise SyntheticContractError('Unknown material: requires explicit mechanism hypothesis')
 info=MATERIALS[material];pre=copy.deepcopy(q['prestart']);v=pre['inputs'];
 mechanisms=[];alerts=[]
 def add(cases,formula,inputs,result,unit='',evidence='ILLUSTRATIVE_UNCALIBRATED'):
  mechanisms.append({'cases':list(cases),'formula':formula,'inputs':inputs,'result':round(float(result),7),'unit':unit,'evidence':evidence})
 mass=max(1,float(num(q,'001')))
 planned_water=max(0,float(num(q,'035')))
 stock=max(0,float(num(q,'002')))
 dose=min(planned_water,stock)
 add(('002','035','053','060'),'min(planned_water,water_stock)',{'planned_g':planned_water,'stock_ml_approx':stock},dose,'g')
 if stock<planned_water:alerts.append('insufficient stock: use available water for projection')
 cap=max(1,float(num(q,'008')))
 # Load approximation intentionally parameterized: displaced grain volume & headroom.
 rice_displacement=mass/.78
 headroom=max(0,cap*.88-rice_displacement)
 if dose>headroom:
  # Anticipate boiling loss/spillage as a scenario branch, not reject the record.
  spill=max(0,dose-headroom)*.6
  dose=max(0,dose-spill)
  add(('001','008','035','059','063','093'),'spill_proxy = 0.6 * max(0, dose - (0.88 * vessel_ml - mass/0.78))',
   {'capacity_ml':cap,'rice_g':mass,'before_g':min(planned_water,stock)},spill,'g')
  alerts.append('overflow risk: provisional spill-loss scenario')
 _input(pre,'water_added_g',dose)
 diameter=max(5,float(num(q,'009')))
 thickness=max(.2,float(num(q,'011')))
 area=math.pi*(diameter/200)**2 # cm diameter -> m radius
 k=info['conductivity_W_mK']
 # illustrative thermal boundary resistance, not a literature-derived cookware fit
 boundary=.08
 resistance=boundary+(thickness/1000)/(k*area)
 reference=boundary+(.002)/(70*math.pi*(20/200)**2)
 coupling=clamp(reference/resistance,.08,1.08)
 indirect_route=(str(num(q,'016'))=='indirect_water_bath')
 if material=='wood_unrated' and indirect_route:
  # Hypothetical external hot-water/steam coupling; heat does not pass through
  # wood as a direct-flame cooking pot. NOT a recipe or validated apparatus.
  coupling=.85
 add(('009','010','011','012','018','042'),'R=0.08 + thickness_m/(conductivity*area_m2); coupling=R_reference/R',
 {'material':material,'k_W_mK':k,'diameter_cm':diameter,'thickness_mm':thickness},coupling,'relative')
 base_eff=_get(pre,'transfer_efficiency')
 contact={'sound':1.0,'scratched':.93,'unknown_condition':.85}.get(str(num(q,'012')), .9)
 spread=clamp(float(num(q,'018')),.1,1)
 actual_eff=clamp(base_eff*coupling*contact*(.88+.12*spread),.02,.95)
 source=str(num(q,'006'))
 stove=str(num(q,'016'))
 compatibility=0.82 if ('charcoal' in source or 'charcoal' in stove) else 1.0
 reliability=clamp(float(num(q,'007')),.0,1.)
 regulation=bool(num(q,'017'))
 actual_power=max(1,float(num(q,'041'))*compatibility)
 _input(pre,'power_W',actual_power)
 _input(pre,'transfer_efficiency',actual_eff)
 add(('006','007','016','017','018','041','042'),'power=declared_W * source_coupling; eta=base_eta * wall_coupling * contact * spread',
 {'source':source,'stove':stove,'reliability':reliability,'control':regulation},actual_eff,'fraction')
 # Steam loss: lid presence + ventilation + arrangement + ambient and area hypotheses
 lid=bool(num(q,'013')) and planned(q,'064')
 lid_factor=float(num(q,'014')) if lid else max(2.,float(num(q,'014')))
 lid_quality=str(num(q,'015'))
 lid_factor*= {'tight_seal':.85,'vented':1.15,'loose_lid':1.3}.get(lid_quality,1.0) if lid else 1.0
 if planned(q,'070') and lid:lid_factor*=.94
 if defined(q,'090') and not lid:alerts.append('lid policy planned but lid absent: policy cannot restore absent lid')
 air_temp=float(num(q,'039'))
 exposure=clamp(1 + .006*(air_temp-25),.7,1.25)
 evap=_get(pre,'evap_reference_g_per_min')*(diameter/20)**2*exposure
 _input(pre,'evap_reference_g_per_min',max(0,evap))
 _input(pre,'lid_multiplier',lid_factor)
 add(('009','013','014','015','039','045','064','070','090','091'),'evap_area~diameter^2; lid_multiplier=seal*management; ambient factor',
 {'lid':lid,'venting':lid_quality,'air_temp_C':air_temp},evap*lid_factor,'g/min')
 # Anticipate effect of rinsing and grain processing on residual starch proxy
 moisture=float(num(q,'032'));broken=float(num(q,'029'))
 rice_type=str(num(q,'024'))
 process=str(num(q,'026'))
 # Declared illustrative variety priors for interactions, not categorical score weights
 varietymod={'long_white_hypothesis':1.0,'parboiled_hypothesis':.92,'short_white_hypothesis':1.1}.get(rice_type,1.)
 hydration=_get(pre,'water_capacity_g_per_g')*varietymod*(1-.20*(moisture-.10))
 time_need=_get(pre,'hot_time_needed_min')*(1+.15*(float(num(q,'025'))-6.7)/6.7)
 _input(pre,'water_capacity_g_per_g',max(.1,hydration))
 _input(pre,'hot_time_needed_min',max(.1,time_need))
 add(('024','025','026','028','029','032','033','034'),'variety,grain size,initial moisture -> water absorption & hot-time proxy',
  {'variety':rice_type,'processing':process,'moisture_fraction':moisture,'broken_fraction':broken},hydration,'g/g')
 rinse_water=max(0,float(num(q,'005')))
 rinse=planned(q,'054') and (planned(q,'055') or planned(q,'056')) and rinse_water>0
 rinsed_fraction=_get(pre,'rinse_removal_fraction') if rinse else 0.0
 if rinse and planned(q,'056'):rinsed_fraction=1-(1-rinsed_fraction)**1.25
 if rinse and not bool(num(q,'021')):rinsed_fraction*=.85
 _input(pre,'rinse_removal_fraction',clamp(rinsed_fraction,0,1))
 starch=_get(pre,'surface_starch_index')
 starch*=1+.15*broken
 if process=='parboiled':starch*=.9
 _input(pre,'surface_starch_index',clamp(starch,0,1))
 if not rinse:_input(pre,'water_retained_g',0)
 add(('005','021','026','029','030','036','054','055','056','057','058'),'starch_residual=surface_starch*(1-removal_with_rinse)',
 {'rinse':rinse,'rinse_stock_ml':rinse_water,'filter_available':bool(num(q,'021'))},_get(pre,'surface_starch_index')*(1-_get(pre,'rinse_removal_fraction')),'index')
 # Anticipations: no automatic rejection on planned vs actual contradictions.
 hazard=(not info['direct_heat_compatible']) and not indirect_route
 if hazard:alerts.append('wood container + direct stove: unsafe/incompatible synthetic scenario; Q*_DEMO safety=0')
 if not regulation:alerts.append('no controllable power: wider forecast uncertainty')
 if reliability<.9:alerts.append('power may drop before completion (prestart branch)')
 # Record presence and policies: conditionally take effect on stochastic branches,
 # not as observed poststart evidence.
 policies=[i for i in POLICIES if defined(q,i)]
 # Anticipations are RISK BRANCHES from prestart, NOT already observed events.
 predicted_risks={
 '086':dose>mass*hydration*1.30,
 '087':dose< mass*hydration*.90,
 '088':actual_power>750,
 '089':actual_power<450,
 '090':not lid,
 '091':evap*lid_factor>8.0,
 '092':reliability<.7,
 '093':planned_water>headroom,
 '094':contact<.90 and actual_power>600,
 '095':starch*(1-rinsed_fraction)>.6,
 '096':time_need>float(num(q,'047',24.)),
 '097':dose>mass*hydration*1.5,
 '098':hazard
 }
 policy_forecast=[{'case':key,'declared':key in policies,'risk_predicted':bool(value),
   'response_executed':False,'source':'scenario anticipation, NOT observed future event'}
     for key,value in predicted_risks.items()]
 return {'prestart':pre,'normalized_packet':q,'material':material,'heat_route':'indirect_water_bath' if indirect_route else 'direct_heat','hazard':hazard,
         'mechanisms':mechanisms,'alerts':alerts,'reliability':reliability,
         'controllable':regulation,'policies':policies,'policy_forecast':policy_forecast,'adjusted_plans':adjusted,'assumed_missing_inputs':assumed_missing,
         'changed_drivers':{key:pre['inputs'][key]['value'] for key in ('water_added_g','power_W','transfer_efficiency','evap_reference_g_per_min','lid_multiplier','water_capacity_g_per_g','hot_time_needed_min','surface_starch_index','rinse_removal_fraction')}}

def case_impact_registry(ctx):
 reg=build_registry()['cases'];p=ctx['normalized_packet']
 numeric={i for m in ctx['mechanisms'] for i in m['cases']}
 forecasts={r['case']:r for r in ctx['policy_forecast']}
 result={}
 for cid,item in reg.items():
  role=item['role']
  if role=='INPUT':
   row=p['case_inputs'][cid]
   value=ASSUMED_DEFAULTS.get(cid) if row['value'] is None else row['value']
   status='NUMERIC_ASSUMPTION' if cid in numeric else 'STRUCTURAL_UNQUANTIFIED'
   evidence='ASSUMED_SYNTHETIC_DEFAULT' if cid in ctx['assumed_missing_inputs'] else row['state']
  elif role=='DERIVED':
   value=None;status='DERIVED_FROM_UPSTREAM';evidence='NO_FUTURE_OBSERVATION'
  elif role=='PLANNED_ACTION':
   value=p['action_plans'][cid]['status'];status='CONDITIONAL_PLAN';evidence='DECLARED_NOT_EXECUTED'
  elif role=='CONDITIONAL_POLICY':
   value=forecasts[cid];status='CONDITIONAL_SCENARIO_BRANCH';evidence='PREDICTED_NOT_OBSERVED'
  else:
   value=p['target_contract'][cid]['measurement_definition'];status='TARGET_DEFINITION';evidence='FUTURE_LABEL_NOT_USED'
  result[cid]={'case':cid,'role':role,'value_or_plan':value,'path_status':status,'evidence':evidence,
    'mechanism_channel':item['group'],'subparameter_count':len(item['subparameters']),
    'sub_subparameter_count':sum(len(s['sub_subparameters']) for s in item['subparameters'])}
 assert len(result)==112
 return result

def simulate13(packet,draws=400,seed=20261017):
 if type(draws)!=int or not 100<=draws<=10000:raise SyntheticContractError('draws range')
 if type(seed)!=int or seed<0:raise SyntheticContractError('seed')
 try:
  ctx=prepare(packet)
 except SyntheticContractError as ex:
  if 'target definitions' in str(ex):
   return {'schema':'riz112/stage13/hierarchical-IC-demo/v1',
     'status':'TARGET_CHANGED_REQUIRES_NEW_MODEL','ic_demo_percent':None,
     'scientific_ic_percent':None,'real_ic_percent':None,'reason':str(ex)}
  raise
 cfg=json.loads(CONTRACT.read_text(encoding='utf8'))
 if cfg.get('approved_for_empirical_success') is not False:raise SyntheticContractError('Unvalidated target')
 rng=random.Random(seed)
 wins=0; qs=[]; outcomes=[]
 pre=ctx['prestart'];warnings=[]
 for i in range(draws):
  shot=sample_packet(pre,rng,cfg['uncertainty_distribution'])
  # Shared physical loss event, correlated with source reliability: normal event
  # vs partial outage. The event is *simulated*, not an observed outcome.
  reliability=ctx['reliability']
  outage=(rng.random()>reliability)
  if outage:
   power=shot['inputs']['power_W']['value']
   cut=.65 if '089' not in ctx['policies'] else .4
   shot['inputs']['power_W']['value']=max(1.,power*(1-cut))
  if ctx['hazard']:
   qdemo=0.0
  else:
   physical=physical_analyze(shot)
   n=vals_from_core(physical)
   scores,qdemo=proxy_scores(n,shot,cfg['proxy_scales'])
   # proxy grain integrity and safety: only for explicit declared hazards.
   # Treat quality as weakest dimension; not summation of bonuses.
   defects=float(num(ctx['normalized_packet'],'029'))
   impurities=float(num(ctx['normalized_packet'],'031'))
   integrity=100*clamp(1-defects,0,1)
   hygiene=100*clamp(1-impurities*2,0,1)
   # last two criteria are unvalidated proxy dimensions, not measured quality
   qdemo=min(qdemo,integrity,hygiene)
  wins+= qdemo >=85
  qs.append(qdemo)
  if i<8:outcomes.append({'simulated_Qstar':round(qdemo,2),'synthetic_outage':outage})
 qs.sort()
 return {'schema':'riz112/stage13/hierarchical-IC-demo/v1',
         'status':'SYNTHETIC_IC_DEMO_ONLY_NOT_REAL_SUCCESS',
         'case_count':112,'per_case_impact_contract':case_impact_registry(ctx),'roles':{'direct':44,'derived':4,'planned_actions':37,'policies':13,'target_definitions':14},
         'ic_demo_percent':round(100*wins/draws,2),'ic_threshold_decision_0_25':wins/draws>=.25,
         'real_ic_percent':None,'scientific_ic_percent':None,'real_quality_labels':0,
         'quality_qstar_definition':'minimum of hydration, heat, free water, starch, grain-integrity, impurity proxies; synthetic threshold 85',
         'draws':draws,'seed':seed,'material':ctx['material'],'heat_route':ctx['heat_route'],
         'mechanism_count':len(ctx['mechanisms']),
         'case_paths_numeric_hypotheses':sorted({cid for m in ctx['mechanisms'] for cid in m['cases']}),
         'mechanism_trace':ctx['mechanisms'], 'anticipated_events':ctx['alerts'],
         'adapted_plans':ctx['adjusted_plans'],'assumed_missing_inputs':ctx['assumed_missing_inputs'],
         'conditional_policies_declared':ctx['policies'],'policy_risk_forecasts':ctx['policy_forecast'],
         'upstream_driver_values':ctx['changed_drivers'],
         'representative_draws':outcomes,'qstar_p50':round(qs[len(qs)//2],2),
         'warning':'All material thermodynamics, thresholds, event probabilities and quality proxies are illustrative. 112 role coverage does NOT prove 112 numeric effects; no real observations or calibration.'}

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('packet',type=Path);p.add_argument('--draws',type=int,default=400);p.add_argument('--seed',type=int,default=20261017)
 a=p.parse_args();print(json.dumps(simulate13(json.loads(a.packet.read_text()),a.draws,a.seed),indent=2,ensure_ascii=False))
