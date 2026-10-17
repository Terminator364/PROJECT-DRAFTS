#!/usr/bin/env python3
"""H3: coupled pre-T0 energy and grain path mechanisms for RIZ112.

Synthetic mechanism demonstration ONLY. No calibrated probability, no food safety advice.
Root links: 006 source availability, 039 ambient, 069 regulation, 025 grain
geometry; 024 diffusivity, 010 vessel, 011 wall, 087 anticipated response.
All parameters are declared before T0. Q*_DEMO is NOT actual rice quality.
"""
from __future__ import annotations
import copy, json, math, random, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step13'))
from hierarchical_engine import evaluate, HierarchyError, _set
from prospective_branches import RICE_PATHS
sys.path.insert(0,str(ROOT/'step9'))
from ic_simulation_v1 import sample_packet, proxy_scores, vals_from_core, physical_analyze, CONTRACT

class ModelAssumptionError(ValueError):pass

def scalar(x,lo,hi,what):
    if type(x) not in (int,float) or not math.isfinite(x) or not lo<=x<=hi:
        raise ModelAssumptionError(f'{what} must be finite in [{lo},{hi}]')
    return float(x)

def evaluate_h3(packet:dict, *, material:str='copper', heat_path:str='direct',
                wall_mm:float=2.0,diameter_cm:float=18.0,water_g:float|None=None,
                lid_present:bool|None=None,
                source_uptime:float=1.0, regulation_duty:float=1.0,
                ambient_C:float|None=None,ambient_UA_W_per_K:float=0.0,
                grain_length_mm:float|None=None, reference_length_mm:float=6.,
                diffusion_ratio:float=1.0, grain_aspect_ratio:float=3.0,
                reference_aspect_ratio:float=3.0,
                rice_profile:dict|None=None,water_policy:dict|None=None,draws:int=1000,seed:int=20261017)->dict:
    if type(draws)!=int or not 100<=draws<=20000:raise ModelAssumptionError('draws 100..20000')
    if type(seed)!=int or seed<0:raise ModelAssumptionError('seed nonnegative int')
    a=scalar(source_uptime,0,1,'source_uptime')
    b=scalar(regulation_duty,0,1,'regulation_duty')
    ua=scalar(ambient_UA_W_per_K,0,30,'ambient_UA_W_per_K')
    if ambient_C is None:
        val=packet['case_inputs']['039']['value']
        if type(val) not in (int,float):raise ModelAssumptionError('ambient C missing')
        ambient_C=val
    ambient=scalar(ambient_C,-20,70,'ambient_C')
    ref=scalar(reference_length_mm,0.2,30,'reference_length_mm')
    D=scalar(diffusion_ratio,0.05,20,'diffusion_ratio')
    ar=scalar(grain_aspect_ratio,1,20,'grain_aspect_ratio')
    ref_ar=scalar(reference_aspect_ratio,1,20,'reference_aspect_ratio')
    if grain_length_mm is not None:ell=scalar(grain_length_mm,0.2,30,'grain_length_mm')
    else:
        ell=None
        if D!=1 or ar!=3 or ref_ar!=3 or ref!=6:
            raise ModelAssumptionError('grain geometry modifiers require explicit grain_length_mm')
    h1=evaluate(packet,material=material,heat_path=heat_path,wall_mm=wall_mm,
                diameter_cm=diameter_cm,water_g=water_g,lid_present=lid_present,
                draws=100,seed=seed,return_prepared_packet=True)
    if h1['status']=='UNSAFE_DIRECT_HEAT_PATH':
        return {'schema':'riz112/H3/v1','status':'UNSAFE_PATH_UNMODELED',
                'scientific_ic_percent':None,'ic_demo_percent':None,
                'reason':'wooden/unrated direct heating is not a certified safe process; do not test directly',
                'trace':h1['anticipations']}
    if h1['status']!='DEMONSTRATION_ASSUMPTIONS_ONLY_NOT_REAL_Q':
        return {'schema':'riz112/H3/v1','status':'BASELINE_NOT_ESTIMABLE',
                'scientific_ic_percent':None,'ic_demo_percent':None,'reason':h1.get('details')}
    p=h1['prepared_packet']
    rice_trace=[]
    if rice_profile is not None:
        if not isinstance(rice_profile,dict) or not set(rice_profile)<=set(RICE_PATHS):
            raise ModelAssumptionError('rice profile keys must be declared')
        for key,val in rice_profile.items():
            case,field,lo,hi=RICE_PATHS[key]
            value=scalar(val,lo,hi,key)
            if case=='054' and p['action_plans']['054']['status']!='PLANNED':
                raise ModelAssumptionError('rinse requires a declared prestart plan')
            if case!='054':_set(p,case,value)
            p['prestart']['inputs'][field]['value']=value
            p['prestart']['inputs'][field]['source']='H3_DECLARED_RICE_PROFILE_ASSUMPTION'
            rice_trace.append({'id':'H3_RICE_PROFILE','case':case,'subparameter':key,'value':value})
    power=p['prestart']['inputs']['power_W']['value']
    base_eta=p['prestart']['inputs']['transfer_efficiency']['value']
    # Energy accounting uses an explicit INTERFACE-ONLY interpretation of eta.
    # Never silently add ambient losses to a measured total-net efficiency.
    gross=power*base_eta*a*b
    ambient_loss=ua*max(0,100-ambient)
    net=max(0,gross-ambient_loss)
    # Preserve the categorical source/equipment root 006 and the predeclared
    # action plan 069. Uptime/duty are independent nested PRE-T0 assumptions.
    # Replacing parent values with floats would silently destroy user input.
    _set(p,'039',ambient)
    if net>0:
        p['prestart']['inputs']['transfer_efficiency']['value']=net/power
        p['prestart']['inputs']['transfer_efficiency']['source']='H3_EXPLICIT_INTERFACE_AND_AMBIENT_LOSS_ASSUMPTION'
    # Crude diffusion-time scaling t~(penetration_length)^2 / D.
    # Grain length is NOT the penetration length, hence aspect ratio is explicit.
    grain_scale=None
    if ell is not None:
        radius_mm=ell/(2*ar);ref_radius=ref/(2*ref_ar)
        grain_scale=(radius_mm/ref_radius)**2 / D
        old_t=p['prestart']['inputs']['hot_time_needed_min']['value']
        new_t=old_t*grain_scale
        if not .001<=new_t<=10000:raise ModelAssumptionError('unphysical assumed hot-time result')
        _set(p,'025',ell)
        p['prestart']['inputs']['hot_time_needed_min']['value']=new_t
        p['prestart']['inputs']['hot_time_needed_min']['source']='H3_DIFFUSION_SCALING_ASSUMPTION_BASELINE_REFERENCE'
    policy=None
    if water_policy is not None:
        if not isinstance(water_policy,dict) or set(water_policy)!={'trigger_shortfall_g','dose_g','adherence_probability'}:
            raise ModelAssumptionError('policy needs trigger_shortfall_g,dose_g,adherence_probability')
        t=scalar(water_policy['trigger_shortfall_g'],0,10000,'trigger_shortfall_g')
        dose=scalar(water_policy['dose_g'],0.001,10000,'dose_g')
        adherence=scalar(water_policy['adherence_probability'],0,1,'adherence_probability')
        if p['correction_policies']['087']['status']!='DEFINED':raise ModelAssumptionError('case 087 not predeclared')
        row=p['case_inputs']['002']
        stock=row['value'] if row['state']!='UNKNOWN' and type(row['value']) in (float,int) else None
        # Stock's unit in legacy case 002 is ml, approximately converted to g under
        # explicit assumed density 1 g/ml. Treat this as TOTAL available, not extra.
        policy={'trigger_shortfall_g':t,'dose_g':dose,'adherence_probability':adherence,
                'total_water_stock_assumed_g':stock,'density_assumption_g_per_ml':1.,
                'resource_role':'case_002'}
    trace=list(h1['anticipations']) + rice_trace + [
      {'id':'H3_SOURCE_AVAILABILITY','case':'006','fraction_of_scheduled_power_available':a},
      {'id':'H3_REGULATION_DUTY','case':'069','fraction_of_available_power_delivered':b},
      {'id':'H3_AMBIENT_LOSS','case':'039','formula':'UA*max(0,100C-Tamb)',
       'ambient_C':ambient,'UA_W_per_K':ua,'lost_W':ambient_loss},
      {'id':'H3_GRAIN_PENETRATION','case':'025','length_mm':ell,
       'diffusion_ratio':D,'grain_aspect_ratio':ar,'reference_aspect_ratio':ref_ar,
       'relative_required_hot_time':grain_scale}
    ]
    if net<=0:
        # Cannot feed zero transfer eta into Step4 validator. Structural no-hot-time
        # proxy gives Q* success 0 in this model; real success is UNKNOWN.
        return {'schema':'riz112/H3/v1','status':'NO_NET_POWER_UNDER_ASSUMPTIONS',
            'ic_demo_percent':0.,'scientific_ic_percent':None,'draws':draws,
            'energy_W':{'gross_W':gross,'loss_W':ambient_loss,'net_W':net},
            'trace':trace,'note':'0 is a proxy convention; actual success probability unknown'}
    dist=json.loads(CONTRACT.read_text())
    rng=random.Random(seed)
    policy_rng=random.Random(seed^0x4A317)
    successes0=successes1=triggered=executed=0
    q0s=[];q1s=[];branch_trace=[]
    for _ in range(draws):
        sampled=sample_packet(p['prestart'],rng,dist['uncertainty_distribution'])
        initial=vals_from_core(physical_analyze(sampled))
        q0=proxy_scores(initial,sampled,dist['proxy_scales'])[1]
        q1=q0
        if policy and initial['W_shortfall']>policy['trigger_shortfall_g']:
            triggered+=1
            reserve=policy['total_water_stock_assumed_g']
            # stock is total available, not reserve; respect cumulative consumption.
            extra=max(0,min(policy['dose_g'],reserve-sampled['inputs']['water_added_g']['value'])) if reserve is not None else 0
            if extra>0 and policy_rng.random()<policy['adherence_probability']:
                executed+=1
                alternative=copy.deepcopy(sampled)
                alternative['inputs']['water_added_g']['value']+=extra
                future=vals_from_core(physical_analyze(alternative))
                q1=proxy_scores(future,alternative,dist['proxy_scales'])[1]
        q0s.append(q0);q1s.append(q1)
        successes0+=q0>=85;successes1+=q1>=85
    return {'schema':'riz112/H3/v1','status':'DEMO_ASSUMED_MECHANISMS_NOT_REAL_Q',
       'baseline_ic_demo_percent':round(100*successes0/draws,2),
       'policy_ic_demo_percent':round(100*successes1/draws,2),
       'policy_delta_percentage_points':round(100*(successes1-successes0)/draws,2),
       'scientific_ic_percent':None,'draws':draws,'seed':seed,
       'energy_W':{'gross_W':round(gross,5),'loss_W':round(ambient_loss,5),'net_W':round(net,5),
                   'nominal_W':power,'eta_wall_only':base_eta},
       'geometry':{'grain_length_mm':ell,'relative_required_hot_time':grain_scale},
       'forecast_events':{'policy_shortfall_triggers':triggered,'hypothetical_executions':executed},
       'material':material,'trace':trace,'no_poststart_values_used':True,
       'parent_categorical_case006_preserved':p['case_inputs']['006']['value']==packet['case_inputs']['006']['value'],
       'parent_action_case069_preserved':p['action_plans']['069']==packet['action_plans']['069'],
       'target_definition':'Q*_DEMO minimum four unvalidated quality proxies >=85',
       'warning':['No independent trial data; this IC is not an empirical chance of successful rice',
                  'eta_wall_only is reinterpreted by the user-declared gross interface assumption: never use if eta already includes ambient losses',
                  'Q* proxy and thermal coefficients require measurement and calibration']}

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--packet',type=Path,default=ROOT/'step6/examples/A_couvercle_ajuste_112.json')
 ap.add_argument('--material',default='copper');ap.add_argument('--draws',type=int,default=1000)
 ap.add_argument('--ambient',type=float,default=22);ap.add_argument('--ambient-UA',type=float,default=1)
 ap.add_argument('--source-uptime',type=float,default=1);ap.add_argument('--regulation-duty',type=float,default=1)
 a=ap.parse_args();p=json.loads(a.packet.read_text(encoding='utf8'))
 out=evaluate_h3(p,material=a.material,draws=a.draws,ambient_C=a.ambient,ambient_UA_W_per_K=a.ambient_UA,source_uptime=a.source_uptime,regulation_duty=a.regulation_duty)
 print(json.dumps(out,ensure_ascii=False,indent=2))
