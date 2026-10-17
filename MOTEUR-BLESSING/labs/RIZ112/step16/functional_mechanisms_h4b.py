#!/usr/bin/env python3
"""RIZ-112 H4B: remaining 15 pre-T0 rubric contracts. NO calibrated quality effect.

Pure diagnostic/conditional computations; all supplementary assumptions declare
unit, source, timestamp and role. No realized after-T0 event enters the model.
"""
from __future__ import annotations
import math
from datetime import datetime

RUBRICS = ('010','011','018','022','023','024','031','071','077','081','083','084','085','094','098')
GROUPS = {
 'thermal_wall':('010','011'), 'temperature_distribution':('018',),
 'handling':('022','071','077'), 'variety':('024',), 'impurities':('031',),
 'service':('023','081','083','084','085'), 'policies':('094','098'),
}
class H4BError(ValueError): pass

def moment(t):
    if not isinstance(t,str): raise H4BError('timezone-stamped date required')
    try: d=datetime.fromisoformat(t.replace('Z','+00:00'))
    except ValueError as e: raise H4BError('invalid date') from e
    if d.tzinfo is None or d.utcoffset() is None: raise H4BError('timezone missing')
    return d

def source_row(r, freeze, start, name, unit=None):
    if not isinstance(r,dict) or not isinstance(r.get('source'),str) or not r['source'].strip():
        raise H4BError(name+': source mandatory')
    if moment(r.get('available_at_utc'))>freeze or freeze>=start:
        raise H4BError(name+': post-freeze data')
    if unit is not None and r.get('unit')!=unit: raise H4BError(name+': incompatible unit')
    state=r.get('state',r.get('kind',r.get('status')))
    if state not in {'OBSERVED','ASSUMPTION','PLANNED','NOT_PLANNED','UNKNOWN','DEFINED','UNDEFINED'}:
        raise H4BError(name+': invalid state')
    if state=='UNKNOWN' and r.get('value') is not None:
        raise H4BError(name+': UNKNOWN must have null value')
    return state

def numerical(r, freeze, start, name, unit, low, high):
    if r is None:return None
    state=source_row(r,freeze,start,name,unit)
    if state=='UNKNOWN':return None
    if state not in ('OBSERVED','ASSUMPTION','PLANNED'):raise H4BError(name+': cannot consume future realization')
    v=r.get('value')
    if type(v) not in (int,float) or not math.isfinite(v) or not low<=v<=high:
        raise H4BError(name+': invalid finite range')
    return float(v)

def selection(r,freeze,start,name,permitted):
    if r is None:return None
    state=source_row(r,freeze,start,name,'enum')
    if state=='UNKNOWN':return None
    if state not in ('OBSERVED','ASSUMPTION','PLANNED') or type(r.get('value')) is not str or r['value'] not in permitted:
        raise H4BError(name+': invalid enumerated input')
    return r['value']

def evaluate_h4b(packet:dict,supplements:dict|None=None)->dict:
    supplements={} if supplements is None else supplements
    allowed={'conductivity_W_mK','thickness_mm','diameter_cm','contact_R_K_W','heat_delta_K',
      'temperature_min_C','temperature_max_C','burn_threshold_C','agitation_count',
      'fluff_count','utensil_type','amylose_fraction','impurity_mass_fraction',
      'sorting_removal_fraction','service_UA_W_K','service_initial_C','service_ambient_C',
      'service_heat_capacity_J_K','service_delay_min','service_target_min_C',
      'planned_max_delay_min','stop_temperature_C'}
    if not isinstance(supplements,dict) or set(supplements)-allowed:raise H4BError('unrecognized nested field')
    p=packet['prestart'];freeze=moment(p['freeze_utc']);start=moment(p['start_utc'])
    if freeze>=start:raise H4BError('freeze after start')
    for k in ('010','011','018','022','023','024','031'):
        source_row(packet['case_inputs'][k],freeze,start,'case '+k)
    for k in ('071','077','081','083','084','085'):
        source_row(packet['action_plans'][k],freeze,start,'action '+k)
    for k in ('094','098'):
        source_row(packet['correction_policies'][k],freeze,start,'policy '+k)
    def num(k,u,lo,hi):return numerical(supplements.get(k),freeze,start,k,u,lo,hi)
    k=num('conductivity_W_mK','W/m/K',0.001,1000)
    thick=num('thickness_mm','mm',0.01,100)
    diameter=num('diameter_cm','cm',1,200)
    Rc=num('contact_R_K_W','K/W',0,100)
    delta=num('heat_delta_K','K',0,500)
    wall=None
    if None not in (k,thick,diameter):
        area=math.pi*(diameter/200)**2
        resistance=(thick/1000)/(k*area)
        wall={'contact_area_m2':round(area,9),'wall_resistance_K_W':round(resistance,8),
              'status':'ILLUSTRATIVE_RESISTANCE_NOT_CALIBRATED','available_heat_W':None,
              'cases':['010','011']}
        if Rc is not None and delta is not None:
            wall['available_heat_W']=round(delta/(resistance+Rc),5)
    lo=num('temperature_min_C','degC',-50,250)
    hi=num('temperature_max_C','degC',-50,250)
    if lo is not None and hi is not None and lo>hi:raise H4BError('thermal range reversed')
    spread=round(hi-lo,5) if lo is not None and hi is not None else None
    agitation=num('agitation_count','count',0,1000)
    fluff=num('fluff_count','count',0,1000)
    tool=selection(supplements.get('utensil_type'),freeze,start,'utensil_type',
         {'spoon','spatula','fork','other_declared'})
    if agitation is not None:
        if not agitation.is_integer():raise H4BError('agitation count fractional')
        if packet['action_plans']['071']['status']!='PLANNED':raise H4BError('agitation not declared')
    if fluff is not None:
        if not fluff.is_integer():raise H4BError('fluff count fractional')
        if packet['action_plans']['077']['status']!='PLANNED':raise H4BError('fluff action not declared')
    if tool is not None and packet['case_inputs']['022']['value'] is not True:
        raise H4BError('tool availability not established')
    handling={'planned_agitations':agitation,'planned_fluffings':fluff,'tool_type':tool,
       'total_planned_contacts':int(agitation+fluff) if agitation is not None and fluff is not None else None,
       'effect_on_grain_breakage':None,'cases':['022','071','077']}
    amylose=num('amylose_fraction','dry_mass_fraction',0,1)
    if amylose is not None and (packet['case_inputs']['024']['state']=='UNKNOWN' or
          packet['case_inputs']['024']['value'] is None):
        raise H4BError('amylose cannot be detached from a declared variety')
    var={'rice_variety':packet['case_inputs']['024']['value'], 'assumed_amylose_fraction':amylose,
         'dry_amylose_mass_g':None,'cases':['024']}
    if amylose is not None:
        rice=packet['prestart']['inputs']['rice_mass_g']
        source_row(rice,freeze,start,'rice_mass_g')
        m=rice.get('value')
        if type(m) not in (int,float) or not math.isfinite(m) or m<=0:raise H4BError('rice mass invalid')
        var['dry_amylose_mass_g']=round(m*amylose,5)
    impurity=num('impurity_mass_fraction','dry_mass_fraction',0,1)
    removed=num('sorting_removal_fraction','fraction',0,1)
    if removed is not None and impurity is None:raise H4BError('sorting removal lacks impurity baseline')
    if impurity is not None and packet['case_inputs']['031']['state']!='UNKNOWN':
        existing=packet['case_inputs']['031']['value']
        if type(existing) not in (int,float) or not math.isfinite(existing) or abs(existing-impurity)>1e-9:
            raise H4BError('conflicting existing impurity fraction')
    leftovers=round(impurity*(1-removed),7) if impurity is not None and removed is not None else None
    impur={'initial_dry_mass_fraction':impurity,'assumed_sorting_removal':removed,
           'expected_remaining_dry_mass_fraction':leftovers,
           'safety_certified':False,'cases':['031']}
    ua=num('service_UA_W_K','W/K',0,500)
    T0=num('service_initial_C','degC',-20,250)
    Ta=num('service_ambient_C','degC',-20,70)
    cp=num('service_heat_capacity_J_K','J/K',1,1e8)
    delay=num('service_delay_min','min',0,10000)
    planned_max=num('planned_max_delay_min','min',0,10000)
    target=num('service_target_min_C','degC',-20,250)
    service={'forecast_service_C':None,'delay_overrun_min':None,'at_least_declared_target':None,
             'cases':['023','081','083','084','085'],'observed_service_temperature_used':False}
    if any(x is not None for x in (ua,T0,Ta,cp,delay,planned_max,target)):
        if packet['case_inputs']['023']['value'] is not True or any(
            packet['action_plans'][i]['status']!='PLANNED' for i in ('081','083')):
            raise H4BError('service vessel/transfer/check actions not predeclared')
        if delay is not None and packet['action_plans']['084']['status']!='PLANNED':
            raise H4BError('service delay plan 084 not predeclared')
        if target is not None and packet['action_plans']['085']['status']!='PLANNED':
            raise H4BError('presentation plan 085 not predeclared')
    if delay is not None and planned_max is not None:
        service['delay_overrun_min']=round(max(0,delay-planned_max),5)
    if None not in (ua,T0,Ta,cp,delay):
        forecast=Ta+(T0-Ta)*math.exp(-ua*60*delay/cp)
        service['forecast_service_C']=round(forecast,5)
        if target is not None:service['at_least_declared_target']=forecast>=target
    burn_threshold=num('burn_threshold_C','degC',0,250)
    stop_threshold=num('stop_temperature_C','degC',0,250)
    burnt_policy=packet['correction_policies']['094']
    stop_policy=packet['correction_policies']['098']
    if burn_threshold is not None and burnt_policy['status']!='DEFINED':
        raise H4BError('094 conditional response not predeclared')
    if stop_threshold is not None and stop_policy['status']!='DEFINED':
        raise H4BError('098 stop policy not predeclared')
    policies={'burn_trigger_hypothetical':bool(hi>=burn_threshold) if hi is not None and burn_threshold is not None else None,
       'stop_trigger_hypothetical':bool(hi>=stop_threshold) if hi is not None and stop_threshold is not None else None,
       'policies_executed_in_reality':False,'cases':['094','098']}
    results={'thermal_wall':wall,'temperature_distribution':{'min_C':lo,'max_C':hi,'spread_C':spread,
               'burn_threshold_predeclared_C':burn_threshold,'cases':['018']},
             'handling':handling,'variety':var,'impurities':impur,'service':service,'policies':policies}
    missing=sorted(k for k,v in results.items() if v is None or all(v.get(z) is None for z in (
         {'thermal_wall':'wall_resistance_K_W','temperature_distribution':'spread_C',
          'handling':'total_planned_contacts','variety':'dry_amylose_mass_g',
          'impurities':'expected_remaining_dry_mass_fraction',
          'service':'forecast_service_C','policies':'burn_trigger_hypothetical'}[k],)))
    if policies['stop_trigger_hypothetical'] is not None and 'policies' in missing:
        missing.remove('policies')
    return {'schema':'riz112/H4B/diagnostics/v1','status':'DIAGNOSTICS_ONLY__NOT_REAL_Q',
         'rubric_paths':list(RUBRICS),'mechanism_groups':results,'groups_without_full_numeric_path':missing,
         'scientific_ic_percent':None,'real_rice_experiments':0,'validated_Q_effects':0,
         'post_T0_observed_predictors':0,'provenance_independently_timestamped':False,
         'warnings':['Scenario equations and actions are not validated quality laws',
                     'All supplemental fields must be frozen before preparation',
                     'No implicit future measurements, no safety guarantee, no quality IC']}