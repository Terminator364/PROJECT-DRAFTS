#!/usr/bin/env python3
"""Auditable, non-calibrating rubric-by-rubric counterfactual scan.

A declared variable is *not* evidence of a causal effect. Distinguish packet-only
interventions, coherently linked pre-T0 primitives, and target/derived roles.
No synthetic IC is presented as a real probability or a validated quality effect.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, math, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
STAGE16=ROOT/'step16'
if str(STAGE16) not in sys.path:sys.path.insert(0,str(STAGE16))
from riz112_unified import run,verify_packet,PacketError

# Only documented exact matches to prestart physical inputs are intervened on together.
# The correspondence is checked against the original packet's observed values.
LINKED_PHYSICAL={
 '001':'rice_mass_g', '014':'lid_multiplier', '030':'surface_starch_index',
 '033':'water_capacity_g_per_g','034':'hot_time_needed_min',
 '035':'water_added_g','036':'water_retained_g','037':'water_initial_C',
 '038':'rice_initial_C','041':'power_W','042':'transfer_efficiency',
 '045':'evap_reference_g_per_min','047':'total_heating_min',
}
OPTIONS={'source_uptime':1.0,'water_g':300.0,'seed':20261017,'draws':400}


def canonical(x):
 return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)

def digest(x):return hashlib.sha256(canonical(x).encode('utf-8')).hexdigest()

def delta_value(v,unit=None):
 """Single bounded 1% perturbation for local sensitivities, NOT a fitted Q coefficient."""
 if isinstance(v,bool):return not v
 if not isinstance(v,(int,float)) or not math.isfinite(v):return None
 amount=max(abs(v)*0.01,0.01)
 fractional=(unit in ('fraction','ratio','probability','multiplier'))
 if fractional and v+amount>1: n=v-amount
 else: n=v+amount
 if fractional and not 0<=n<=1:return None
 return n

def impact(base,trial):
 a=base['ic_demo_percent'];b=trial['ic_demo_percent']
 delta=None if a is None or b is None else round(float(b)-float(a),9)
 h3_keys=('energy_W','geometry','forecast_events','trace','policy_delta_percentage_points')
 h3_changed=any(canonical(base['H3_demonstration'].get(k))!=canonical(trial['H3_demonstration'].get(k)) for k in h3_keys)
 a0=base['H4']['a'].get('mechanisms');a1=trial['H4']['a'].get('mechanisms')
 b0=base['H4']['b'].get('mechanism_groups');b1=trial['H4']['b'].get('mechanism_groups')
 h4_changed=canonical((a0,b0))!=canonical((a1,b1))
 return {'ic_demo_delta_points':delta,'h3_intermediates_changed':h3_changed,
   'h4_diagnostic_changed':h4_changed,
   'response':('IC_DEMO_CHANGED_ONLY' if delta is not None and abs(delta)>1e-9
         else 'INTERMEDIATE_CHANGED_IC_DEMO_STABLE' if h3_changed or h4_changed
         else 'NO_DOWNSTREAM_RESPONSE_IN_IMPLEMENTED_CODE')}

def attempt(packet,baseline,*,case_id,group,new_value,link=None,lab_root=ROOT):
 modified=copy.deepcopy(packet)
 if group=='action_plans':
  modified[group][case_id]['status']=new_value
 elif group=='correction_policies':
  modified[group][case_id]['status']=new_value
  if new_value=='UNDEFINED':
   modified[group][case_id]['trigger']=None
   modified[group][case_id]['planned_response']=None
 else:modified[group][case_id]['value']=new_value
 if link:
  modified['prestart']['inputs'][link]['value']=new_value
 try:
  computed=run(modified,lab_root=lab_root,h3_options=OPTIONS,require_h3=True)
  return {'status':'EXECUTED','evidence':impact(baseline,computed)}
 except (ValueError,TypeError,KeyError,ArithmeticError,OverflowError) as ex:
  return {'status':'REJECTED_BY_MODEL_OR_CONTRACT','error_type':type(ex).__name__,
          'error_excerpt':str(ex)[:180]}

def audit(packet:dict,lab_root:Path=ROOT)->dict:
 valid=verify_packet(packet)
 initial=digest(packet)
 base=run(packet,lab_root=lab_root,h3_options=OPTIONS,require_h3=True)
 out=[]
 for i in range(1,113):
  k=f'{i:03d}'
  if k in valid['derived_forecast_roles']:
   out.append({'rubric':k,'group':'derived','state':'DERIVED_OUTPUT_NOT_INDEPENDENT_INPUT',
               'intervention':None,'effect_on_Q':'NOT_IDENTIFIABLE_WITHOUT_REAL_TRIALS'});continue
  group=next(g for g in ('case_inputs','action_plans','correction_policies','target_contract') if k in packet[g])
  row=packet[group][k]
  item={'rubric':k,'group':group,'source':row.get('source'),
        'state':row.get('state',row.get('status')),
        'effect_on_Q':'NOT_IDENTIFIABLE_WITHOUT_REAL_TRIALS'}
  if group=='target_contract':
   item.update(intervention=None,reason='TARGET_IS_A_LABEL_OR_MEASUREMENT_RULE_NOT_PRET0_CAUSAL_INPUT')
  elif group=='case_inputs':
   old=row.get('value');new=delta_value(old,row.get('unit'))
   if item['state']=='UNKNOWN' or old is None:
    item.update(intervention=None,reason='UNKNOWN_NO_MEASURED_BASELINE__NO_FAKE_ZERO')
   elif new is None:
    item.update(intervention=None,reason='NO_PREDECLARED_VALID_ALTERNATIVE_FOR_CATEGORICAL_INPUT')
   else:
    item['intervention']={'before':old,'after':new,'test_type':'SINGLE_CASE_RECORD'}
    item['case_only']=attempt(packet,base,case_id=k,group=group,new_value=new,lab_root=lab_root)
    physical=LINKED_PHYSICAL.get(k)
    if physical:
     physicalrow=packet['prestart']['inputs'].get(physical)
     if physicalrow and type(physicalrow['value'])==type(old) and physicalrow['value']==old:
      item['linked_primitive']=physical
      item['coherent_case_plus_physical']=attempt(packet,base,case_id=k,group=group,new_value=new,link=physical,lab_root=lab_root)
     else:
      item['linked_primitive_warning']='NO_EXACT_MATCH_TO_PRESPECIFIED_PHYSICAL_INPUT'
  elif group=='action_plans':
   old=row.get('status')
   if old=='PLANNED':
    item['intervention']={'before':old,'after':'NOT_PLANNED','test_type':'COUNTERFACTUAL_CANCEL_PLANNED_ACTION'}
    item['case_only']=attempt(packet,base,case_id=k,group=group,new_value='NOT_PLANNED',lab_root=lab_root)
   elif old=='NOT_PLANNED':
    item.update(intervention=None,reason='NO_ALTERNATIVE_ACTION_HAS_BEEN_PREDECLARED')
   else:item.update(intervention=None,reason='UNKNOWN_PLANNED_ACTION__DO_NOT_INVENT_ACTION')
  elif group=='correction_policies':
   if row.get('status')=='DEFINED':
    item['intervention']={'before':'DEFINED','after':'UNDEFINED','test_type':'REMOVE_PREDECLARED_POLICY'}
    item['case_only']=attempt(packet,base,case_id=k,group=group,new_value='UNDEFINED',lab_root=lab_root)
   else:item.update(intervention=None,reason='POLICY_UNDEFINED_OR_UNKNOWN__NO_INVENTED_CORRECTION')
  out.append(item)
 if len(out)!=112 or len({x['rubric'] for x in out})!=112:raise AssertionError('112 rubric accounting must be exact')
 counts={}
 for row in out:
  typ=(row.get('coherent_case_plus_physical') or row.get('case_only') or {}).get('evidence',{}).get('response')
  if typ is None: typ=row.get('reason','COUNTERFACTUAL_REJECTED')
  counts[typ]=counts.get(typ,0)+1
 if digest(packet)!=initial:raise AssertionError('Never mutate source inputs')
 return {'schema':'riz112/step17/effect-path-audit/v1','input_sha256':initial,
  'baseline_ic_demo_percent':base['ic_demo_percent'],
  'baseline_scientific_ic_percent':None,
  'rubrics_total':112,'rubrics_by_group':{g:sum(x['group']==g for x in out) for g in ('case_inputs','action_plans','correction_policies','target_contract','derived')},
  'summary_response_counts':counts,
  'intervention_size_policy':'local 1% counterfactual for numeric values, not a causal effect magnitude',
  'does_not_establish_real_Q_effects':True,
  'caveat':'Changes in IC_DEMO are conditional properties of the existing synthetic model, never measurements or calibrated percentages for real quality.',
  'rows':out}

def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,default=ROOT/'step6/examples/A_couvercle_ajuste_112.json');p.add_argument('--lab-root',type=Path,default=ROOT);p.add_argument('--output',type=Path)
 a=p.parse_args(argv);packet=json.loads(a.packet.read_text(encoding='utf8'));res=audit(packet,a.lab_root)
 doc=json.dumps(res,indent=2,ensure_ascii=False,allow_nan=False)+'\n'
 if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(doc,encoding='utf8')
 else:print(doc)
 return 0
if __name__=='__main__':raise SystemExit(main())
