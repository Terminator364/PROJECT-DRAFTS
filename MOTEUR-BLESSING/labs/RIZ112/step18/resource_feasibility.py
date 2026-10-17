#!/usr/bin/env python3
"""RIZ-112 Step18: explicit resource-availability constraints, not Q effects.

Computes only pre-T0 mass/volume feasibility with supplied conversions.
No treatment of a diagnostic change as a probability of rice success.
"""
from __future__ import annotations
import copy
import math
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'step16'))
from riz112_unified import verify_packet,moment,PacketError

class ResourceContractError(ValueError):pass

def _number(value, label, *, positive=False):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ResourceContractError(label+': finite nonboolean number required')
    if (value <= 0 if positive else value < 0):
        raise ResourceContractError(label+': nonnegative/positive physical bound violated')
    return float(value)

def _reading(packet,field,unit):
    row=packet['case_inputs'].get(field)
    if row is None or row.get('state')=='UNKNOWN':return None
    if row.get('unit')!=unit:raise ResourceContractError('case '+field+' expected '+unit)
    if row.get('state') not in ('OBSERVED','ASSUMPTION','PLANNED'):
        raise ResourceContractError('unsupported input state: '+field)
    return _number(row.get('value'),'case '+field)

def _assumption(packet, assumptions, name, unit):
    row=assumptions.get(name)
    if row is None:return None
    if not isinstance(row,dict) or row.get('unit')!=unit or row.get('kind') not in ('OBSERVED','ASSUMPTION'):
        raise ResourceContractError('metadata required for '+name)
    if not isinstance(row.get('source'),str) or not row['source'].strip():
        raise ResourceContractError('source required for '+name)
    freeze=moment(packet['prestart']['freeze_utc'])
    try:stamp=moment(row.get('available_at_utc'))
    except PacketError as e:raise ResourceContractError('date required for '+name) from e
    if stamp > freeze:raise ResourceContractError('post-freeze assumption not admissible: '+name)
    return _number(row.get('value'),name,positive=True)

def evaluate_resources(packet:dict, assumptions:dict|None=None)->dict:
    verify_packet(packet)
    assumptions={} if assumptions is None else assumptions
    if not isinstance(assumptions,dict):raise ResourceContractError('assumptions must be a mapping')
    allowed={'water_density_g_per_ml','rinse_volume_planned_ml','rice_bulk_density_g_per_ml'}
    if set(assumptions)-allowed:raise ResourceContractError('unsupported assumption')
    rho=_assumption(packet,assumptions,'water_density_g_per_ml','g/ml')
    rinse_target=_assumption(packet,assumptions,'rinse_volume_planned_ml','ml')
    bulk=_assumption(packet,assumptions,'rice_bulk_density_g_per_ml','g/ml')
    stock=_reading(packet,'002','ml')
    rinse_stock=_reading(packet,'005','ml')
    capacity=_reading(packet,'008','ml')
    rice=_reading(packet,'001','g')
    water=_reading(packet,'035','g')
    def result(status,margin=None,details=None):
        return {'status':status,'margin_ml':margin,'details':details or {},
                'is_quality_effect':False,'scientific_ic_percent':None}
    if stock is None or water is None or rho is None:
        cooking=result('ABSTAIN_MISSING_OBSERVATION_OR_CONVERSION')
    else:
        required=water/rho
        cooking=result('COMPUTED_PLAN_FEASIBILITY',stock-required,{'stock_ml':stock,'planned_water_ml':required,'feasible_by_volume':stock >=required})
    if packet['action_plans']['054']['status']!='PLANNED':
        rinsing=result('NOT_PLANNED_ACTION')
    elif rinse_stock is None or rinse_target is None:
        rinsing=result('ABSTAIN_MISSING_RINSE_PLAN_OR_STOCK')
    else:
        rinsing=result('COMPUTED_PLAN_FEASIBILITY',rinse_stock-rinse_target,{'stock_ml':rinse_stock,'planned_rinse_ml':rinse_target,'feasible_by_volume':rinse_stock>=rinse_target})
    if capacity is None or rice is None or water is None or rho is None or bulk is None:
        pot=result('ABSTAIN_MISSING_GEOMETRY_OR_CONVERSION')
    else:
        initial_dry_bulk_ml=rice/bulk
        liquid_ml=water/rho
        occupancy_proxy=initial_dry_bulk_ml+liquid_ml
        pot=result('COMPUTED_INITIAL_LOAD_PROXY_NOT_SAFETY_APPROVAL',capacity-occupancy_proxy,
            {'pot_capacity_ml':capacity,'dry_rice_bulk_volume_ml':initial_dry_bulk_ml,
             'planned_liquid_ml':liquid_ml,'additive_loading_proxy_ml':occupancy_proxy,
             'proxy_margin_nonnegative':capacity>=occupancy_proxy,
             'limitation':'Dry bulk plus water is a planning proxy; trapped voids, mixing and grain swelling make it nonvalidated for final fill or overflow.'})
    return {'schema':'riz112/step18/resource-feasibility/v1','case_ids':['001','002','005','008','035','054'],
            'diagnostics':{'cooking_water_inventory':cooking,'rinse_water_inventory':rinsing,'pot_initial_load_proxy':pot},
            'assumptions_used':sorted(assumptions),'scientific_ic_percent':None,
            'limits':'Only local resource constraints; no evidence of change to the real quality Q, IC_DEMO or physiological food safety.'}

def perturb_resource(packet,assumptions,case_id,factor=1.01):
    if case_id not in ('002','005','008'):
        raise ResourceContractError('Only one of 002,005,008 can be perturbed')
    _number(factor,'factor',positive=True)
    baseline=evaluate_resources(packet,assumptions)
    future=copy.deepcopy(packet)
    row=future['case_inputs'][case_id]
    if row['state']=='UNKNOWN':return {'case_id':case_id,'status':'ABSTAIN_UNKNOWN_BASELINE','baseline':baseline,'after':None,'scientific_ic_percent':None}
    row['value']=_number(row['value'],'counterfactual before')*factor
    after=evaluate_resources(future,assumptions)
    key={'002':'cooking_water_inventory','005':'rinse_water_inventory','008':'pot_initial_load_proxy'}[case_id]
    left=baseline['diagnostics'][key]['margin_ml'];right=after['diagnostics'][key]['margin_ml']
    return {'case_id':case_id,'status':'COUNTERFACTUAL_EXECUTED' if left is not None and right is not None else 'ABSTAIN',
            'mechanism':key,'delta_margin_ml':None if left is None or right is None else round(right-left,10),
            'scientific_ic_percent':None}
