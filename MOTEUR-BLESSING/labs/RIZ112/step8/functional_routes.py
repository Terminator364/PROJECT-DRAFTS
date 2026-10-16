#!/usr/bin/env python3
"""RIZ112 step8: functional routing of D014 missing 62 entries.

This is an executable PRESTART decision/uncertainty graph, not a recipe or a
probability estimator. Each of 62 entries produces an operational consequence;
physical effects are allowed ONLY where an equation exists. No retrofitted Q.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter
import json, sys, math

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'step7'))
from graph_governor import analyze7
sys.path.insert(0, str(ROOT/'step6'))
from engine112 import PRESTART, FORECAST, ACTIONS, POLICIES, analyze112

REGISTRY_PATH=ROOT/'RESTANT_62_REGISTRE.json'
GAP_IDS=set(json.loads(REGISTRY_PATH.read_text(encoding='utf8'))['cases'])
SOURCE_IDS={k for k in GAP_IDS if k in PRESTART}
FORECAST_IDS={k for k in GAP_IDS if k in FORECAST}
ACTION_IDS={k for k in GAP_IDS if k in ACTIONS}
POLICY_IDS={k for k in GAP_IDS if k in POLICIES}
assert len(GAP_IDS)==62 and tuple(map(len, (SOURCE_IDS, FORECAST_IDS, ACTION_IDS, POLICY_IDS)))==(22,3,26,11)

# Only strict prerequisite relations whose absence makes a DECLARED action
# inconsistent. ALL are pre-declared, no real future action is used.
ACTION_REQUIREMENTS={
 '050':[('019','bool_resource')],
 '053':[('020','bool_resource')],
 '055':[('005','positive_resource')],
 '056':[('005','positive_resource')],
 '057':[('021','bool_resource')],
 '059':[('008','positive_resource')],
 '060':[('002','positive_resource')],
 '062':[('004','positive_resource')],
 '063':[('008','positive_resource')],
 '064':[('013','bool_resource')],
 '065':[('006','energy_resource')],
 '068':[('017','bool_resource')],
 '070':[('013','bool_resource')],
 '080':[('013','bool_resource')],
}
# Prestart plan sequencing is NOT physical dependence; no future events assumed.
PLAN_PREDECESSORS={
 '058':['057'], '059':['051'], '060':['053','059'], '063':['059'],
 '066':['065'], '067':['066'], '068':['065'],
 '070':['064'], '072':['069'], '073':['069'], '074':['073'],
 '075':['074'], '076':['075'], '078':['074'], '079':['078'], '080':['074']}

RESOURCE_CASE_TARGET={
 '002':['035','060'], '004':['062'], '005':['055','056'],
 '007':['065'], '008':['059','063'], '009':['008'], '012':['059'],
 '013':['064','070','080'], '014':['045','046'], '015':['046'],
 '016':['065'], '017':['068'], '019':['050'], '020':['053'],
 '021':['057'], '026':['024','052'], '027':['051'], '028':['027'],
 '032':['001'], '037':['043'], '038':['043'], '040':['043']}

def known(row):return row['state']!='UNKNOWN'

def check_resource(src, requirement, row):
 if not known(row):return 'UNKNOWN', None
 v=row['value']
 if requirement=='bool_resource':return ('SATISFIED' if v is True else 'CONTRADICTED'),v
 if requirement=='positive_resource':return ('SATISFIED' if float(v)>0 else 'CONTRADICTED'),v
 if requirement=='energy_resource':
  return ('CONTRADICTED' if str(v).strip().lower() in {'none','absent','unavailable'} else 'SATISFIED'),v
 raise RuntimeError('unknown predefined requirement')

def get_known(packet,k):
 row=packet['case_inputs'][k];return row['value'] if known(row) else None

def gate(status,refs,reason,measure=None):
 return {'state':status,'refs':refs,'reason':reason,'measurement':measure}

def source_route(packet,k):
 row=packet['case_inputs'][k];v=get_known(packet,k)
 res={'case':k,'route':'PRESTART_EVIDENCE_OR_CONSTRAINT','observed_state':row['state'],
      'downstream_contracts':RESOURCE_CASE_TARGET[k], 'derived':None,'decisions':[]}
 if k=='002':
  water=get_known(packet,'035')
  if v is not None and water is not None:
   res['decisions'].append(gate('SATISFIED' if v>=water else 'CONTRADICTED',['002','035'],
           'Water stock >= planned added water (ml≈g only in toy model)',round(v-water,6)))
  else:res['decisions'].append(gate('UNKNOWN',['002','035'],'Cannot quantify water-stock margin'))
 elif k=='004':
  action=packet['action_plans']['062']['status']
  state='NOT_REQUIRED' if action=='NOT_PLANNED' else 'UNKNOWN' if v is None or action in ('UNKNOWN','NOT_APPLICABLE') else 'SATISFIED' if v>0 else 'CONTRADICTED'
  res['decisions'].append(gate(state,['004','062'],'If fat addition planned, positive mass required'))
 elif k=='005':
  states=[packet['action_plans'][a]['status'] for a in ['055','056']]
  state=('UNKNOWN' if v is None else
         'CONTRADICTED' if v<=0 and any(s=='PLANNED' for s in states) else
         'SATISFIED' if v>0 and any(s=='PLANNED' for s in states) else
         'UNKNOWN' if any(s=='UNKNOWN' for s in states) else 'NOT_REQUIRED')
  res['decisions'].append(gate(state,['005','055','056'],'Rinse stock must be positive if rinsing planned; required amount UNKNOWN',v))
 elif k=='007':
  state='UNKNOWN' if v is None else 'RISK_DECLARED' if v==0 and packet['action_plans']['065']['status']=='PLANNED' else 'DESCRIPTIVE_ONLY'
  res['decisions'].append(gate(state,['007','065'],'Reliability cannot predict heat without empirical power-failure model',v))
 elif k=='008':
  water=get_known(packet,'035')
  state='UNKNOWN' if v is None or water is None else 'NECESSARY_FIT_ONLY' if v>water else 'CONTRADICTED'
  res['decisions'].append(gate(state,['008','035'],'Water alone must fit; rice volume/headspace unavailable',None if v is None or water is None else v-water))
 elif k=='009':
  if v is not None and v>0:res['derived']={'pot_surface_cm2_geometry_only':round(math.pi*(v/2)**2,6)}
  res['decisions'].append(gate('GEOMETRY_ONLY' if v is not None and v>0 else 'UNKNOWN' if v is None else 'CONTRADICTED',['009'],
     'Circular-pan assumed geometry; no evaporation effect calibrated'))
 elif k=='013':
  for a in ('064','070','080'):
   planned=packet['action_plans'][a]['status']
   state='UNKNOWN' if v is None or planned=='UNKNOWN' else 'CONTRADICTED' if planned=='PLANNED' and v is False else 'NOT_REQUIRED' if planned!='PLANNED' else 'SATISFIED'
   res['decisions'].append(gate(state,['013',a],'Action requiring lid availability'))
 elif k=='014':
  res['decisions'].append(gate('TOY_PHYSICS_DRIVER' if v is not None else 'UNKNOWN',['014','045','046'],
             'Lid multiplier enters step4 evaporation; not independently calibrated',v))
 elif k=='017':
  a=packet['action_plans']['068']['status']
  state='UNKNOWN' if v is None or a=='UNKNOWN' else 'CONTRADICTED' if a=='PLANNED' and v is False else 'SATISFIED'
  res['decisions'].append(gate(state,['017','068'],'Power adjustment needed if reduction planned'))
 elif k in ('019','020','021'):
  a={'019':'050','020':'053','021':'057'}[k]
  action=packet['action_plans'][a]['status']
  state='UNKNOWN' if v is None or action=='UNKNOWN' else 'CONTRADICTED' if action=='PLANNED' and v is False else 'SATISFIED'
  res['decisions'].append(gate(state,[k,a],'Required equipment for declared action'))
 elif k=='032':
  if v is not None:
   mass=get_known(packet,'001');mass=float(mass) if mass is not None else None
   # wet-basis moisture only ASSUMED; do not overwrite step4 effective water
   res['derived']={'dry_matter_g_assuming_wet_basis':None if mass is None else round(mass*(1-v),6),
    'moisture_g_assuming_wet_basis':None if mass is None else round(mass*v,6)}
  res['decisions'].append(gate('PROXY_ONLY' if v is not None else 'UNKNOWN',['001','032'],
             'Wet-basis mass identity conditional on moisture definition; Q effect UNKNOWN'))
 elif k in ('037','038'):
  res['decisions'].append(gate('TOY_PHYSICS_DRIVER' if v is not None else 'UNKNOWN',[k,'043'],
          'Temperature in step4 heating balance; no empirical validation',v))
 elif k=='040':
  res['decisions'].append(gate('SCENARIO_DIMENSION' if v is not None else 'UNKNOWN',['040','043'],
         'Altitude registered but omitted from fixed 100 C step4 boiling model',v))
 else:
  # An explicitly UNKNOWN relationship is MORE honest than a decorative arrow.
  res['decisions'].append(gate('DESCRIPTIVE_NOT_QUANTIFIED' if v is not None else 'UNKNOWN',[k],
       'Typed prestart source documented; relation to Q requires evidence',v))
 return res

def action_route(packet,k):
 status=packet['action_plans'][k]['status'];requirements=ACTION_REQUIREMENTS.get(k,[])
 preds=PLAN_PREDECESSORS.get(k,[])
 gates=[]
 if status=='PLANNED':
  for resource,kind in requirements:
   g,v=check_resource(resource,kind,packet['case_inputs'][resource]);gates.append(gate(g,[resource,k],'Declared resource required for action',v))
  for predecessor in preds:
   st=packet['action_plans'][predecessor]['status']
   g='SEQUENCE_PRESENT' if st=='PLANNED' else 'UNKNOWN' if st=='UNKNOWN' else 'SEQUENCE_HYPOTHESIS_ONLY'
   gates.append(gate(g,[predecessor,k],'Optional plan-sequence hypothesis, not a universal necessary condition'))
 elif status=='UNKNOWN':gates.append(gate('UNKNOWN',[k],'Action not yet specified at T0'))
 else:gates.append(gate('NOT_REQUIRED',[k],'Action not planned or not applicable at T0'))
 return {'case':k,'route':'PLANNED_ACTION_FEASIBILITY','plan_state':status,
         'prestart_requirements':requirements,'planned_predecessors':preds,
         'decisions':gates,'scenario_branch_known':status not in ('UNKNOWN',),
         'quality_effect_estimated':False}

def forecast_route(packet,k,old):
 # Cannot leak realized measurements; no Q effect.
 if k=='043':
  val=next(x for x in old['graph']['all_112_case_trace'] if x['id']=='043')['output']
  return {'case':k,'route':'PRESTART_FORECAST','state':'MODEL_PROXY',
   'meaning':'time to boiling approximated by toy physical model; pressure path unavailable',
   'value':val,'source_from_step4':True,'quality_effect_estimated':False}
 if k=='046':
  val=next(x for x in old['graph']['all_112_case_trace'] if x['id']=='046')['output']
  return {'case':k,'route':'PRESTART_FORECAST','state':'MODEL_PROXY',
    'meaning':'lid multiplier proxy, not independent measured future loss',
    'value':val,'source_from_step4':True,'quality_effect_estimated':False}
 return {'case':k,'route':'PRESTART_FORECAST','state':'NO_FORMULA',
   'meaning':'Frémissement stability cannot be forecast from declared variables without empirical model',
   'source_from_step4':False,'quality_effect_estimated':False}

def policy_route(packet,k):
 policy=packet['correction_policies'][k]
 if policy['status']=='UNDEFINED':
  return {'case':k,'route':'PREDECLARED_CONDITIONAL_POLICY','state':'NO_POLICY',
       'scenario_dispatch':'UNAVAILABLE','trigger':None,'response':None,
       'quality_effect_estimated':False}
 trigger=policy['trigger']
 return {'case':k,'route':'PREDECLARED_CONDITIONAL_POLICY','state':'BRANCH_CONFIGURED',
  'scenario_dispatch':'READY_FOR_HYPOTHETICAL_EVENT',
  'trigger':trigger,'response':policy['planned_response'],
  'quality_effect_estimated':False}

def dispatch_hypothetical(report,packet,event:str):
 # E.g. event='water_shortfall_reported' is hypothetical predeclared condition,
 # NOT an assertion that a future event has occurred.
 if not isinstance(event,str) or not event:return []
 return [{'case':k,'trigger':p['trigger'],'response':p['planned_response'],
          'quality_effect_estimated':False}
         for k,p in sorted(packet['correction_policies'].items())
         if k in POLICY_IDS and p['status']=='DEFINED' and event==p['trigger']]

def analyze8(packet):
 base=analyze7(packet)
 old=analyze112(packet)
 routes={}
 for k in sorted(GAP_IDS):
  if k in SOURCE_IDS:routes[k]=source_route(packet,k)
  elif k in FORECAST_IDS:routes[k]=forecast_route(packet,k,old)
  elif k in ACTION_IDS:routes[k]=action_route(packet,k)
  else:routes[k]=policy_route(packet,k)
 if len(routes)!=62:raise ValueError('D014 mandatory 62 routes missing')
 decisions=[x for r in routes.values() for x in r.get('decisions',[])]
 status=Counter(d['state'] for d in decisions)
 conflicts=[{'case':k,'decision':d} for k,r in routes.items() for d in r.get('decisions',[]) if d['state']=='CONTRADICTED']
 return {'schema':'riz112/step8/functional-routes/v1',
  'preparation_id':packet['prestart']['preparation_id'],
  'd014_gap_ids':sorted(routes),'d014_gap_cases_with_typed_route':len(routes),
  'distinct_prestart_checks_or_derived':len(decisions),
  'route_counts':dict(Counter(r['route'] for r in routes.values())),
  'states':dict(status),'hard_conflicts':conflicts,
  'routes':routes,
  'test_subject':'CONSTRAINT_AND_PLAN_ROUTING_NOT_QUALITY_CAUSALITY',
  'quality_probability':None,'calibrated_ic_percent':None,
  'unresolved_Q_effect_count':62,
  'label_cases_consumed_as_predictor':0,
  'actual_future_events_consumed':0,
  'quality_model_status':'NOT_CALIBRATED',
  'existing_stage7':{'structural_edges_kept':base['graph_governance']['accepted_structural_associations'],
    'cases_missing_to_Q112':len(base['graph_governance']['unlinked_to_Q112'])}}

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('packet',type=Path);p.add_argument('-o','--output',type=Path)
 args=p.parse_args();packet=json.loads(args.packet.read_text(encoding='utf8'))
 s=json.dumps(analyze8(packet),ensure_ascii=False,indent=2)+'\n'
 if args.output:args.output.write_text(s,encoding='utf8')
 else:print(s,end='')
if __name__=='__main__':main()
