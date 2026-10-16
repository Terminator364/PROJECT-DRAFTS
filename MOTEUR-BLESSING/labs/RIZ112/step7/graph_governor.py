#!/usr/bin/env python3
"""RIZ-112 stage 7: typed dependency audit and constraint layer.

Separates static/reference associations from permitted PRE-T0 computation.
This module reports proposed DAG structure and strict evidence contract; it
NEVER uses observed future quality to calculate success or emits a fake IC.
"""
from __future__ import annotations
import json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step6'))
from engine112 import (analyze112, ACTION_DEPENDENCIES, POLICIES,
 POLICY_DEPENDENCIES, OUTCOME_DEPENDENCIES, OUTCOMES, ACTIONS,
 PRESTART, FORECAST, IDS, ContractError, digest)

FORECAST_LINKS={
 '043':['037','038','041','042'],
 '044':['017','018','041','069'],
 '046':['013','014','015','045'],
 '048':['001','033','034','035','036','041','042','045','047']}
DECLARED={**FORECAST_LINKS,**ACTION_DEPENDENCIES,**POLICY_DEPENDENCIES,**OUTCOME_DEPENDENCIES}
# '054' is a prior decision regarding whether to rinse; 055/056 are contingent
# implementations, not prerequisites for making the decision. Remove those
# reverse references, retaining the decision -> action links (055 -> 054).
CYCLIC_PLAN_EDGES={('054','055'),('054','056')}

class DependencyError(ValueError): pass

def edges_audit():
 accepted=[];rejected=[]
 for downstream, upstreams in sorted(DECLARED.items()):
  for upstream in upstreams:
   if upstream not in IDS or downstream not in IDS:
    raise DependencyError(f'unknown {downstream}->{upstream}')
   if downstream not in OUTCOMES and upstream in OUTCOMES:
    rejected.append({'downstream':downstream,'upstream':upstream,
      'why':'POSTSTART_TARGET_CANNOT_BE_PRESTART_INPUT'})
   elif (downstream,upstream) in CYCLIC_PLAN_EDGES:
    rejected.append({'downstream':downstream,'upstream':upstream,
      'why':'REVERSE_OF_DECLARED_PLAN_ORDER'})
   else:
    accepted.append({'downstream':downstream,'upstream':upstream,
      'status':'STRUCTURAL_ASSOCIATION_NOT_VALIDATED_CAUSAL_EFFECT'})
 return accepted,rejected

def topological_sort(accepted):
 upstreams={id:set() for id in IDS}; downstreams={id:set() for id in IDS}
 for e in accepted:
  up,down=e['upstream'],e['downstream']
  upstreams[down].add(up);downstreams[up].add(down)
 ready=sorted(v for v in IDS if not upstreams[v]);order=[]
 while ready:
  n=ready.pop(0);order.append(n)
  for child in sorted(downstreams[n]):
   upstreams[child].remove(n)
   if not upstreams[child]:ready.append(child);ready.sort()
 if len(order)!=112:
  raise DependencyError('Directed dependency cycle remained in graph: '+str(sorted(set(IDS)-set(order))))
 return order

def _known(entry):return entry['state']!='UNKNOWN'

def _bool_plan(packet,case_input_id,action_id,meaning):
 info=packet['case_inputs'][case_input_id]
 plan=packet['action_plans'][action_id]
 if not _known(info) or plan['status']=='UNKNOWN':
  return {'cases':[case_input_id,action_id], 'status':'UNRESOLVED', 'meaning':meaning,
          'scientific_impact':'NOT_QUANTIFIED'}
 if plan['status']=='PLANNED' and info['value'] is False:
  return {'cases':[case_input_id,action_id], 'status':'INCONSISTENT', 'meaning':meaning,
          'scientific_impact':'NOT_QUANTIFIED'}
 return {'cases':[case_input_id,action_id], 'status':'CONSISTENT', 'meaning':meaning,
          'scientific_impact':'NOT_QUANTIFIED'}

def feasibility(packet):
 """Computable feasibility NECESSARY conditions, never quality/prediction bonuses."""
 inp=packet['case_inputs']; plans=packet['action_plans'];out=[]
 for src,act,label in [
  ('013','064','couvercle présent si placement annoncé'),
  ('019','050','balance présente si pesée annoncée'),
  ('020','053','instrument de mesure présent si dosage annoncé'),
  ('021','057','passoire présente si égouttage annoncé'),
  ('022','077','ustensile présent si égrainage annoncé'),
  ('023','081','récipient disponible si transfert annoncé'),
  ('017','068','contrôle puissance si réduction de feu prévue')]:
  out.append(_bool_plan(packet,src,act,label))
 # stock necessary, not sufficient: 1ml of water ≈ 1g in simplified demo
 a=inp['002'];b=inp['035'];density_assumption='WATER_DENSITY_1G_PER_ML_UNCALIBRATED'
 if not (_known(a) and _known(b)):
  status='UNRESOLVED';margin=None
 else:
  margin=float(a['value'])-float(b['value'])
  status='CONSISTENT' if margin>=0 else 'INCONSISTENT'
 out.append({'cases':['002','035'],'status':status,'meaning':'stock eau disponible >= eau ajoutée',
             'margin_ml_approx':margin,'assumption':density_assumption,
             'scientific_impact':'NOT_QUANTIFIED'})
 # total initial water alone cannot exceed vessel capacity; does not establish
 # sufficient headspace, rice displacement or safe boiling level.
 cap=inp['008'];w=inp['035']
 if not (_known(cap) and _known(w)):
  status='UNRESOLVED';margin=None
 else:
  margin=float(cap['value'])-float(w['value'])
  status='CONSISTENT_NECESSARY_ONLY' if margin>0 else 'INCONSISTENT'
 out.append({'cases':['008','035'],'status':status,
             'meaning':'liquid alone must fit in vessel (rice volume/headspace unknown)',
             'margin_ml_upper_bound':margin,'scientific_impact':'NOT_QUANTIFIED'})
 # declared power-control plan vs resource availability: no energy type inference
 energy=inp['006'];heat=plans['065']
 status='UNRESOLVED' if not _known(energy) or heat['status']=='UNKNOWN' else (
      'INCONSISTENT' if heat['status']=='PLANNED' and str(energy['value']).lower() in ('none','absent','unavailable')
      else 'CONSISTENT')
 out.append({'cases':['006','065'],'status':status,'meaning':'energy declared for planned heating',
             'scientific_impact':'NOT_QUANTIFIED'})
 return out

def analyze7(packet):
 old=analyze112(packet)
 accepted,rejected=edges_audit();order=topological_sort(accepted)
 checks=feasibility(packet)
 counts=dict(Counter(x['status'] for x in checks));baddies=[r for r in checks if r['status']=='INCONSISTENT']
 declared_roles={r['id']:r['role'] for r in old['graph']['all_112_case_trace']}
 prestart_only={k for k,v in declared_roles.items() if v!='POSTSTART_TARGET_NOT_FEATURE'}
 for e in accepted:
  if e['downstream'] in prestart_only and e['upstream'] not in prestart_only:
   raise DependencyError('future label leaks into forward prestart graph')
 # Reachability to target 112 counts hypotheses *as such*, NOT proven pathways
 adj=defaultdict(set)
 for e in accepted:adj[e['upstream']].add(e['downstream'])
 reachable=[];missing=[]
 for case in sorted(IDS):
  seen={case}; q=[case]
  while q:
   cur=q.pop()
   for d in adj[cur]:
    if d not in seen:seen.add(d);q.append(d)
  (reachable if '112' in seen else missing).append(case)
 return {
  'schema':'riz112/stage7/graph-audit/v1',
  'case_count':112,
  'v6_case_processing':old['case_execution'],
  'graph_governance':{'declared_edges':len(accepted)+len(rejected),
    'accepted_structural_associations':len(accepted),
    'rejected_wrong_direction_edges':rejected,
    'removed_edges':len(rejected),
    'forward_graph_is_acyclic':True,'topological_case_order':order,
    'no_poststart_target_as_prestart_dependency':True,
    'structural_hypothesis_paths_to_Q112':reachable,
    'unlinked_to_Q112':missing,
    'interpretation':'A graph path is NOT an estimated physical effect or predictive contribution'},
  'feasibility':{'checks':checks,'counts':counts,'hard_conflicts':baddies,
     'method':'necessary conditions only; may flag inconsistency, not assign numerical IC malus'},
  'case_112_contract':old['graph']['all_112_case_trace'][-1],
  'prestart_evidence_proven':False,
  'quality_protocol_approved':False,
  'observed_real_trials':0,
  'quantified_physical_case_paths':old['case_execution']['numeric_path_cases_without_scientific_calibration'],
  'validated_case_effects':0,
  'ic_percent':None,
  'prediction_status':'ABSTAIN__NO_Q_PROTOCOL_OR_CALIBRATION',
  'packet_sha256':digest(packet),
 }

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('packet',type=Path);p.add_argument('--output','-o',type=Path);args=p.parse_args()
 packet=json.loads(args.packet.read_text(encoding='utf8'));result=analyze7(packet)
 s=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
 if args.output:args.output.write_text(s,encoding='utf8')
 else:print(s,end='')
if __name__=='__main__':main()
