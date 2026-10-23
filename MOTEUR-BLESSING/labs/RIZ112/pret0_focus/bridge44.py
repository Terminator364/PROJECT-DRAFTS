#!/usr/bin/env python3
"""RIZ112: 44/44 executable pre-T0 routes; NOT 44 calibrated Q effects.

Each historical PRESTART case has a mechanism, feasibility, or provenance
calculation. No post-T0 outcomes are predictors, no fictitious Q weights.
Standard library only. Optional, additive companion to existing Step6/Step9.
"""
from __future__ import annotations
from datetime import datetime, timezone
import math

PRESTART = tuple(f'{i:03d}' for i in list(range(1, 43)) + [45, 47])
TWINS = {
    '001':'rice_mass_g','014':'lid_multiplier','024':'rice_variety',
    '030':'surface_starch_index','033':'water_capacity_g_per_g',
    '034':'hot_time_needed_min','035':'water_added_g','036':'water_retained_g',
    '037':'water_initial_C','038':'rice_initial_C','041':'power_W',
    '042':'transfer_efficiency','045':'evap_reference_g_per_min',
    '047':'total_heating_min'
}
ASSUMPTIONS = {
 'dry_rice_bulk_density_g_per_ml':0.85,
 'water_specific_heat_J_per_gK':4.186,
 'rice_specific_heat_J_per_gK':1.6,
 'boiling_point_C_at_zero_m':100.0,
 'boiling_point_decline_C_per_m':0.003,
 'thermal_conductivity_W_per_mK':{
  'aluminium':205.0,'steel':16.0,'copper':385.0,
  'ceramic':2.0,'wood':0.15}
}
# Names express actual outputs, never a promised effect on empirical Q.
_ROUTE_LINES = """
001|PHYSICAL|dry_rice_sensible_heat_proxy_J
002|FEASIBILITY|available_water_minus_planned_dose_ml
003|PLAN|salt_adding_resource_quantity
004|PLAN|fat_adding_resource_quantity
005|PLAN|rinse_water_resource_quantity
006|PLAN|energy_source_consistency
007|UNCERTAINTY|declared_available_heat_duration_proxy_min
008|FEASIBILITY|pot_headspace_proxy_ml
009|PHYSICAL|pan_surface_area_cm2
010|PHYSICAL|declared_material_conductivity_W_mK
011|PHYSICAL|bottom_conduction_resistance_K_per_W
012|PHYSICAL|bottom_condition_class
013|PLAN|lid_placement_feasible
014|PHYSICAL|lid_adjustment_multiplier
015|PHYSICAL|steam_vent_class
016|PLAN|burner_matches_source
017|PLAN|heat_reduction_feasible
018|PHYSICAL|thermal_nonuniformity_proxy
019|MEASUREMENT|weighing_plan_feasible
020|MEASUREMENT|water_dosing_plan_feasible
021|PLAN|planned_draining_feasible
022|PLAN|planned_fluffing_feasible
023|PLAN|planned_serving_transfer_feasible
024|PROVENANCE|declared_rice_profile_key
025|PHYSICAL|grain_length_squared_mm2
026|PHYSICAL|processing_class
027|PROVENANCE|batch_identity_for_grouped_validation
028|PROVENANCE|storage_age_days_provenance
029|PHYSICAL|unbroken_grain_fraction_proxy
030|PHYSICAL|remaining_surface_starch_proxy
031|SAFETY|initial_non_impurity_fraction_proxy
032|PHYSICAL|initial_dry_solids_proxy_g
033|PHYSICAL|absorption_water_target_proxy_g
034|PHYSICAL|planned_hot_time_ratio_proxy
035|PHYSICAL|planned_water_before_unmodelled_losses_g
036|PHYSICAL|planned_rinse_water_fraction
037|PHYSICAL|water_sensible_heat_proxy_J
038|PHYSICAL|rice_sensible_heat_proxy_J
039|PHYSICAL|ambient_to_boil_temperature_gap_C
040|PHYSICAL|boiling_point_altitude_proxy_C
041|PHYSICAL|nominal_useful_power_proxy_W
042|PHYSICAL|expected_thermal_transfer_fraction
045|PHYSICAL|planned_evaporation_proxy_g
047|PHYSICAL|planned_nominal_heat_energy_J
"""
ROUTES = {p[0]:(p[1],p[2]) for line in _ROUTE_LINES.strip().splitlines()
          if (p:=line.strip().split('|'))}
assert set(ROUTES)==set(PRESTART)

class BridgeError(ValueError):pass

def when(s):
    if not isinstance(s,str):raise BridgeError('missing timestamp')
    try:d=datetime.fromisoformat(s.replace('Z','+00:00'))
    except ValueError as e:raise BridgeError('invalid timestamp') from e
    if d.tzinfo is None:raise BridgeError('timestamp must have timezone')
    return d.astimezone(timezone.utc)

def equal(a,b):
    if type(a) in (int,float) and type(b) in (int,float):
        return math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-9)
    return type(a) is type(b) and a==b

def evaluate44(packet):
    """Compute typed downstream output for every R001..R042,R045,R047."""
    if not isinstance(packet,dict) or not isinstance(packet.get('case_inputs'),dict):
        raise BridgeError('Step6 case_inputs required')
    rows=packet['case_inputs']
    if set(rows)!=set(PRESTART):raise BridgeError('expected exactly 44 prestart inputs')
    if set(packet)&{'poststart','observed_result','actual_quality','realized_actions'}:
        raise BridgeError('post-T0 observations cannot be predictors')
    pre=packet.get('prestart',{})
    freeze,start=when(pre.get('freeze_utc')),when(pre.get('start_utc'))
    if not freeze<start:raise BridgeError('freeze must precede start')
    vals={}
    for rid in PRESTART:
        row=rows[rid]
        if row.get('state') not in ('OBSERVED','ASSUMPTION','PLANNED','UNKNOWN'):
            raise BridgeError(rid+': invalid state')
        if not isinstance(row.get('source'),str) or not row['source'].strip():
            raise BridgeError(rid+': missing source')
        if when(row.get('available_at_utc'))>freeze:raise BridgeError(rid+': temporal leakage')
        v=row.get('value')
        if row['state']=='UNKNOWN':
            if v is not None:raise BridgeError(rid+': UNKNOWN cannot contain value')
        elif type(v) in (float,int):
            if not math.isfinite(v):raise BridgeError(rid+': nonfinite')
        elif type(v) not in (str,bool):raise BridgeError(rid+': unsupported input type')
        vals[rid]=v
    primitives=pre.get('inputs',{})
    for rid,name in TWINS.items():
        twin=primitives.get(name)
        if not isinstance(twin,dict):raise BridgeError(rid+': missing historical semantic twin')
        if when(twin.get('available_at_utc'))>freeze:
            raise BridgeError(rid+': primitive temporal leakage')
        if vals[rid] is None or not equal(vals[rid],twin.get('value')):
            raise BridgeError(rid+': semantic twin missing/conflicting')
    plans=packet.get('action_plans',{})
    def planned(rid):
        row=plans.get(rid,{})
        if row and when(row.get('available_at_utc'))>freeze:
            raise BridgeError('future action plan '+rid)
        return row.get('status')=='PLANNED'
    def val(rid):return vals[rid]
    def num(rid):
        v=val(rid)
        if v is None:return None
        if type(v) not in (float,int):raise BridgeError(rid+': expected number')
        return float(v)
    def allnum(*ids):
        vs=[num(i) for i in ids]
        return None if any(x is None for x in vs) else vs
    def gate(resource,action):
        v=val(resource)
        if v is None:return None
        return bool(v) if planned(action) else 'NOT_PLANNED'
    A=ASSUMPTIONS
    alt=num('040')
    Tb=None if alt is None else A['boiling_point_C_at_zero_m']-A['boiling_point_decline_C_per_m']*alt
    if alt is not None and not 0<=alt<=3500:
        raise BridgeError('R040 altitude outside scope of rough proxy')
    def derive(rid):
        if rid=='001':
            x=allnum('001','038')
            return None if x is None or Tb is None else x[0]*A['rice_specific_heat_J_per_gK']*(Tb-x[1])
        if rid=='002':
            x=allnum('002','035');return None if x is None else x[0]-x[1]
        if rid=='003':return num('003') if planned('061') else 'NOT_PLANNED'
        if rid=='004':return num('004') if planned('062') else 'NOT_PLANNED'
        if rid=='005':return num('005') if planned('055') or planned('056') else 'NOT_PLANNED'
        if rid=='006':
            return None if val('006') is None else (val('006'),val('016'),
             {'gas':'gas_burner','electricity':'electric_hotplate','charcoal':'charcoal_stove'}.get(str(val('006')))==val('016'))
        if rid=='007':
            x=allnum('007','047');return None if x is None else x[0]*x[1]
        if rid=='008':
            x=allnum('008','035','036','001')
            return None if x is None else x[0]-x[1]-x[2]-x[3]/A['dry_rice_bulk_density_g_per_ml']
        if rid=='009':return None if num('009') is None else math.pi*(num('009')/2)**2
        if rid=='010':return None if val('010') is None else A['thermal_conductivity_W_per_mK'].get(str(val('010')))
        if rid=='011':
            x=allnum('011','009');k=derive('010')
            return None if x is None or k is None or x[1]<=0 or k<=0 else
             (x[0]*0.001)/(k*(math.pi*(x[1]*0.01/2)**2))
        if rid=='012':return val('012')
        if rid=='013':return gate('013','064')
        if rid=='014':return num('014')
        if rid=='015':return val('015')
        if rid=='016':
            return None if val('016') is None else (val('016'),val('006'),
             {'gas_burner':'gas','electric_hotplate':'electricity','charcoal_stove':'charcoal'}.get(str(val('016')))==val('006'))
        if rid=='017':return gate('017','068')
        if rid=='018':return None if num('018') is None else 1-num('018')
        if rid=='019':return gate('019','050')
        if rid=='020':return gate('020','053')
        if rid=='021':return gate('021','057')
        if rid=='022':return gate('022','077')
        if rid=='023':return gate('023','081')
        if rid=='024':return val('024')
        if rid=='025':return None if num('025') is None else num('025')**2
        if rid=='026':return val('026')
        if rid=='027':return val('027')
        if rid=='028':return num('028')
        if rid=='029':return None if num('029') is None else 1-num('029')
        if rid=='030':
            s=num('030');p=primitives.get('rinse_removal_fraction',{}).get('value')
            return None if s is None or type(p) not in (float,int) else
             s*(1-p if planned('054') else 1)
        if rid=='031':return None if num('031') is None else 1-num('031')
        if rid=='032':
            x=allnum('001','032');return None if x is None else x[0]*(1-x[1])
        if rid=='033':
            x=allnum('001','033');return None if x is None else x[0]*x[1]
        if rid=='034':
            x=allnum('034','047');return None if x is None or x[0]<=0 else x[1]/x[0]
        if rid=='035':
            x=allnum('035','036');return None if x is None else x[0]+x[1]
        if rid=='036':
            x=allnum('035','036');return None if x is None or x[0]+x[1]<=0 else x[1]/(x[0]+x[1])
        if rid=='037':
            x=allnum('035','036','037')
            return None if x is None or Tb is None else (x[0]+x[1])*A['water_specific_heat_J_per_gK']*(Tb-x[2])
        if rid=='038':
            x=allnum('001','038')
            return None if x is None or Tb is None else x[0]*A['rice_specific_heat_J_per_gK']*(Tb-x[1])
        if rid=='039':return None if num('039') is None or Tb is None else Tb-num('039')
        if rid=='040':return Tb
        if rid=='041':
            x=allnum('041','042');return None if x is None else x[0]*x[1]
        if rid=='042':
            x=allnum('042','007');return None if x is None else x[0]*x[1]
        if rid=='045':
            x=allnum('045','047','014')
            return None if x is None else x[0]*x[1]*(x[2] if val('013') is True else 1)
        if rid=='047':
            x=allnum('041','042','047');return None if x is None else x[0]*x[1]*x[2]*60
        raise BridgeError('no route '+rid)
    routes={}
    for rid in PRESTART:
        role,name=ROUTES[rid]
        output=derive(rid)
        if type(output)==float and not math.isfinite(output):
            raise BridgeError(rid+': derived nonfinite')
        routes[rid]={
            'route':name,'type':role,
            'status':'UNKNOWN' if output is None else
                     ('NOT_PLANNED' if output=='NOT_PLANNED' else 'EVALUATED'),
            'output':output,
            'claim':'TRACE_OR_PHYSICAL_PROXY_NOT_EMPIRICAL_Q_EFFECT'}
    return {
     'schema':'riz112/pret0/bridge44/v1',
     'routed_count':len(routes),'routes':routes,
     'routing_complete':set(routes)==set(PRESTART),
     'evaluated_count':sum(v['status']=='EVALUATED' for v in routes.values()),
     'scientific_ic_percent':None,
     'fortyfour_independent_quality_effects_proven':False,
     'historical_quality_proxy_unchanged':True,
     'assumptions':A
    }
