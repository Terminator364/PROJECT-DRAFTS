#!/usr/bin/env python3
"""Step20 physical influence envelope, NOT a predictor of actual rice quality.

Thermodynamic upper-capacity estimate, not a cooking trajectory. No artificial
quality weights, no double counting with H3 and no post-T0 information.
All non-packet physical constants are disclosed as predeclared assumptions.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import copy, json, hashlib, math, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'step16'))
from riz112_unified import verify_packet, moment

class PhysicalEvidenceError(ValueError): pass

FIELDS={
 '001':('rice_mass_g','g'),
 '033':('water_capacity_g_per_g','g_per_g'),
 '035':('water_added_g','g'),
 '036':('water_retained_g','g'),
 '037':('water_initial_C','degC'),
 '038':('rice_initial_C','degC'),
 '041':('power_W','W'),
 '042':('transfer_efficiency','fraction'),
 '047':('total_heating_min','min')
}
# Bounds are numerical input/validation limits, NOT learned rice physiology.
BOUNDS={'rice_mass_g':(0.001,100000),'water_capacity_g_per_g':(0.01,20),
 'water_added_g':(0,1000000),'water_retained_g':(0,1000000),
 'water_initial_C':(-30,120),'rice_initial_C':(-30,120),
 'power_W':(0,100000),'transfer_efficiency':(0,1),
 'total_heating_min':(0,100000)}
ASSUMPTIONS={
 'water_specific_heat_J_per_gK':('J/g/K',0.01,50),
 'rice_specific_heat_J_per_gK':('J/g/K',0.01,50),
 'latent_vaporization_J_per_g':('J/g',0.01,10000),
 'target_water_temperature_C':('degC',0,120),
 'source_uptime_fraction':('fraction',0,1),
 'regulation_duty_fraction':('fraction',0,1),
 'ambient_heat_loss_W':('W',0,100000)
}

def number(x, label, lo, hi):
 if isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x) or not lo<=x<=hi:
  raise PhysicalEvidenceError(f'{label}: finite numerical value in [{lo},{hi}] required')
 return float(x)

def _evidence(row, freeze, name, *, kind_key='state'):
 if not isinstance(row,dict): raise PhysicalEvidenceError('Missing evidence record '+name)
 if row.get(kind_key) not in ('OBSERVED','PLANNED','ASSUMPTION'):
  if row.get(kind_key)=='UNKNOWN': raise PhysicalEvidenceError('UNKNOWN must abstain rather than simulate zero: '+name)
  raise PhysicalEvidenceError('Unsupported source status: '+name)
 if not isinstance(row.get('source'),str) or not row['source'].strip():
  raise PhysicalEvidenceError('Missing provenance: '+name)
 try: t=moment(row.get('available_at_utc'))
 except Exception as e: raise PhysicalEvidenceError('Timestamp missing/invalid: '+name) from e
 if t>freeze:raise PhysicalEvidenceError('POST_FREEZE_LEAKAGE: '+name)

def validate_semantic_twins(packet):
 """A JSON field and H3 primitive representing one quantity must agree."""
 verify_packet(packet)
 freeze=moment(packet['prestart']['freeze_utc'])
 result={}
 for rid,(field,unit) in FIELDS.items():
  row=packet['case_inputs'][rid]
  prim=packet['prestart']['inputs'].get(field)
  _evidence(row,freeze,'case '+rid)
  _evidence(prim,freeze,'primitive '+field,kind_key='kind')
  if row.get('unit')!=unit:raise PhysicalEvidenceError(f'{rid}: expected {unit}')
  a=number(row.get('value'),f'case {rid}',*BOUNDS[field]);b=number(prim.get('value'),field,*BOUNDS[field])
  if not math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-10):
   raise PhysicalEvidenceError(f'SEMANTIC_TWIN_CONFLICT: case_inputs.{rid} != prestart.inputs.{field}')
  result[rid]={'field':field,'value':a,'unit':unit,'linked':True}
 return result

def read_assumptions(packet,assumptions):
 if not isinstance(assumptions,dict) or set(assumptions)!=set(ASSUMPTIONS):
  raise PhysicalEvidenceError('Explicit seven-parameter assumptions required, no hidden defaults')
 freeze=moment(packet['prestart']['freeze_utc'])
 values={}
 for key,(unit,lo,hi) in ASSUMPTIONS.items():
  row=assumptions[key]
  _evidence(row,freeze,key,kind_key='kind')
  if row.get('unit')!=unit:raise PhysicalEvidenceError(key+': incorrect unit')
  values[key]=number(row.get('value'),key,lo,hi)
 return values

def _digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')).hexdigest()

def calculate(packet,assumptions):
 linked=validate_semantic_twins(packet);c=read_assumptions(packet,assumptions)
 v={t[0]:linked[k]['value'] for k,t in FIELDS.items()}
 mass=v['rice_mass_g'];water=v['water_added_g']+v['water_retained_g']
 T=c['target_water_temperature_C']
 # Prevent false 'sufficient energy' claims when inputs start above the target.
 if v['water_initial_C']>T or v['rice_initial_C']>T:
  raise PhysicalEvidenceError('Initial temperature exceeds target: target-stage physics outside scope')
 heat_water=water*c['water_specific_heat_J_per_gK']*(T-v['water_initial_C'])
 heat_rice=mass*c['rice_specific_heat_J_per_gK']*(T-v['rice_initial_C'])
 seconds=60*v['total_heating_min']
 delivered=v['power_W']*v['transfer_efficiency']*c['source_uptime_fraction']*c['regulation_duty_fraction']*seconds
 loss=c['ambient_heat_loss_W']*seconds
 net=max(0.0,delivered-loss)
 required=heat_water+heat_rice
 surplus=net-required
 theoretical_steam_ceiling=min(water,max(0,surplus)/c['latent_vaporization_J_per_g'])
 # Steam ceiling: maximal thermal conversion if all surplus heats evaporation,
 # NOT predicted evaporated mass, not net final absorption or cooked yield.
 target_absorb=mass*v['water_capacity_g_per_g']
 max_water_mass_before_unmodeled_losses=water
 return {'schema':'riz112/step20/conditional-physical-envelope/v1',
 'status':'THEORETICAL_ENERGY_AND_WATER_BUDGET_ONLY',
 'physical_account':{
  'planned_total_water_g':round(water,8),'dry_rice_g':mass,
  'water_heat_required_J':round(heat_water,8),'rice_heat_required_J':round(heat_rice,8),
  'nominal_energy_delivered_J':round(delivered,8),'assumed_heat_loss_J':round(loss,8),
  'nonnegative_available_energy_J':round(net,8),'heat_to_target_required_J':round(required,8),
  'energy_margin_for_target_J':round(surplus,8),
  'energy_target_feasible_in_idealized_budget':net>=required,
  'water_for_absorption_target_g':round(target_absorb,8),
  'max_water_before_unmodeled_loss_g':round(max_water_mass_before_unmodeled_losses,8),
  'water_target_mass_feasible_before_losses':water>=target_absorb,
  'thermal_ceiling_on_evaporation_g':round(theoretical_steam_ceiling,8),
  'thermal_ceiling_is_not_predicted_evaporation':True},
 'active_semantic_twins':linked,'assumptions':c,
 'provenance':{'packet_sha256':_digest(packet),'assumptions_sha256':_digest(assumptions)},
 'scientific_ic_percent':None,'Q_real_observed':None,'real_Q_effects_proven':0,
 'not_a_real_Q_probability':True,
 'limitations':['Constant specific heats and fixed target temperature are explicit simplifications',
 'Vessel sensible energy, spatial gradients, mass transfer, phase timing, convection, steam loss and pressure are unmodelled',
 'A nonnegative budget is a necessary-resource proxy, NOT sufficient proof of correct cooking or food safety',
 'A negative budget does not establish the real physical outcome without measured boundary losses and time profiles',
 'No quality (Q) score or rice-success probability is inferred from this envelope']}

def coherent_perturbation(packet,case_id,new_value):
 if case_id not in FIELDS:raise PhysicalEvidenceError('Only linked physical twins may be modified')
 validate_semantic_twins(packet)
 field=FIELDS[case_id][0];v=number(new_value,field,*BOUNDS[field]);out=copy.deepcopy(packet)
 out['case_inputs'][case_id]['value']=v
 out['prestart']['inputs'][field]['value']=v
 validate_semantic_twins(out)
 return out

def audit_perturbations(packet,assumptions,*,fraction=0.01):
 number(fraction,'fraction',0.000001,0.5)
 baseline=calculate(packet,assumptions)
 rows=[]
 metrics=('energy_margin_for_target_J','water_for_absorption_target_g','max_water_before_unmodeled_loss_g',
          'thermal_ceiling_on_evaporation_g')
 for rid,(field,unit) in FIELDS.items():
  v=baseline['active_semantic_twins'][rid]['value'];lo,hi=BOUNDS[field]
  alt=max(lo,min(hi,v*(1+fraction) if v else fraction*hi))
  if alt==v:alt=max(lo,min(hi,v*(1-fraction)))
  if alt==v: rows.append({'id':rid,'status':'NO_ADMISSIBLE_ALTERNATIVE','quality_effect_verified':False});continue
  changed=calculate(coherent_perturbation(packet,rid,alt),assumptions)
  delta={k:round(changed['physical_account'][k]-baseline['physical_account'][k],8) for k in metrics}
  rows.append({'id':rid,'field':field,'before':v,'after':alt,
               'physical_metric_deltas':delta,'physical_intermediate_responded':any(x!=0 for x in delta.values()),
               'scientific_IC_delta_percent':None,'quality_effect_verified':False})
 return {'schema':'riz112/step20/nine-coupled-counterfactuals/v1',
         'perturbation_fraction':fraction,'tested_semantic_twins':len(rows),'rows':rows,
         'baseline':baseline,'scientific_ic_percent':None,'actual_Q_effects_verified':0}

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True)
 p.add_argument('--assumptions',type=Path,required=True)
 p.add_argument('--output',type=Path)
 a=p.parse_args();obj=audit_perturbations(json.loads(a.packet.read_text(encoding='utf8')),
 json.loads(a.assumptions.read_text(encoding='utf8')))
 text=json.dumps(obj,ensure_ascii=False,indent=2)+'\n'
 if a.output:a.output.write_text(text,encoding='utf8')
 else:print(text,end='')
