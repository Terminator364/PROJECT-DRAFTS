#!/usr/bin/env python3
"""Cross-stage evidence ledger. Records paths/limits, never fabricates Q effects."""
from __future__ import annotations
import json
from pathlib import Path
from collections import Counter

IDS=[f'{i:03d}' for i in range(1,113)]
PHYSICAL=set(['001','033','035','036','037','038','041','042','047'])
TARGET=set(f'{i:03d}' for i in range(99,113))
class LedgerError(ValueError):pass

def compile_ledger(r17,r19,r20,r24,q25):
    d17={x['rubric']:x for x in r17['rows']}
    d20={x['rubric']:x for x in r20['rows']}
    d19={x['rubric']:x for x in r19['rubrics']}
    if set(d17)!=set(IDS) or set(d20)!=set(IDS):raise LedgerError('A prior source omits rubric(s)')
    if set(d19)&TARGET or len(d19)!=30:raise LedgerError('Unexpected physical/target route split')
    if set(q25['rubrics'])!=TARGET or q25['approved_by_user'] is not False:raise LedgerError('Q is not approved')
    if r24.get('pair_count')!=36 or r24.get('nonadditive_physics_pairs')!=7:raise LedgerError('Pairwise theoretical audit not intact')
    if r17['baseline_scientific_ic_percent'] is not None or r20['scientific_ic_percent'] is not None:
        raise LedgerError('Prior fake scientific IC detected')
    pairs={i:[] for i in IDS}
    for p in r24['tested_interactions']:
        if len(p['pair'])!=2 or not set(p['pair'])<=PHYSICAL:raise LedgerError('Unsupported tested pair')
        for i in p['pair']:pairs[i].append({'other_id':next(x for x in p['pair'] if x!=i),'status':p['status']})
    rows=[]
    for ident in IDS:
        x=d17[ident];phys=d20[ident]
        if ident in TARGET:category='POST_T0_TARGET_ONLY'; next_test='Finalize measurement method with user then observe after cooking; never feed into pre-T0 prediction'
        elif ident in PHYSICAL:category='THEORETICAL_PHYSICAL_INTERMEDIATE_ONLY';next_test='Independent paired physical measurements and modeled sensitivity vs actual outcome; quantify uncertainty'
        elif ident in d19:category='PRE_T0_PLAN_RESOURCE_ROUTE_ONLY';next_test='Assess whether specified pre-T0 plan alters a verified physical trajectory; log realized action separately after T0'
        else:category='NOT_PROVEN_PHYSICAL_Q_EFFECT';next_test='Determine physical applicability/identifiability from pre-T0 inputs; do not force any IC change'
        row={'rubric':ident,'canonical_name':phys['canonical_name'],'role_group':phys['role_group'],
          'evidence_category':category,
          'step17_local_perturbation':x.get('reason') or x.get('coherent_case_plus_physical',{}).get('status','NOT_MEASURED'),
          'step20_response':phys['step20_evidence_status'],
          'step19_route_checked':ident in d19,'step24_pairwise_physical_checks':len(pairs[ident]),
          'Q_real_causal_effect_verified':False,'scientific_IC_delta_percent':None,
          'next_test':next_test,
          'source_refs':['step17/RAPPORT_112_INFLUENCES_DEMO_20261017.json','step20/REGISTRE_STEP20_112.json']+(['step19/REPORT_30_ROUTES_20261017.json'] if ident in d19 else [])+(['step24/INTERACTIONS_36_PHYSIQUES_A.json'] if ident in PHYSICAL else [])}
        rows.append(row)
    counts=dict(sorted(Counter(x['evidence_category'] for x in rows).items()))
    return {'schema':'riz112/step26/evidence-ledger-112/v1','total':112,'counts':counts,'reference_synthetic_scenario':'A',
      'user_priority_tier':['101','102'],'Q_scoring_approved':False,'Q_formula':None,
      'authentic_rice_trials':0,'scientific_ic_percent':None,'real_Q_causal_effects_proven':0,
      'pairwise_theoretical_interactions_tested':36,'nonadditive_theoretical_pairs':7,
      'note':'Theoretical derivatives/route status, not empirical prediction. NO universal claim of 112 independent nonzero effects.',
      'rows':rows}

def validate_ledger(d):
    if d['total']!=112 or len(d['rows'])!=112 or [x['rubric'] for x in d['rows']]!=IDS:raise LedgerError('Missing/reordered cases')
    if sum(d['counts'].values())!=112:raise LedgerError('Category count invalid')
    if d['counts'].get('THEORETICAL_PHYSICAL_INTERMEDIATE_ONLY')!=9 or d['counts'].get('POST_T0_TARGET_ONLY')!=14:
        raise LedgerError('Mandatory role groups altered')
    if d['Q_scoring_approved'] or d['Q_formula'] is not None or d['authentic_rice_trials']!=0 or d['scientific_ic_percent'] is not None:
        raise LedgerError('Evidence wrongly promoted')
    if any(x['Q_real_causal_effect_verified'] or x['scientific_IC_delta_percent'] is not None for x in d['rows']):
        raise LedgerError('Causal/IC effect fabricated')
    return True

if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--lab',type=Path,required=True);a.add_argument('--out',type=Path,required=True);p=a.parse_args();lab=p.lab
 def load(f):return json.loads((lab/f).read_text(encoding='utf8'))
 result=compile_ledger(load('step17/RAPPORT_112_INFLUENCES_DEMO_20261017.json'),load('step19/REPORT_30_ROUTES_20261017.json'),load('step20/REGISTRE_STEP20_112.json'),load('step24/INTERACTIONS_36_PHYSIQUES_A.json'),load('step25/PROTOCOLE_Q_MESURES_PROPOSE_NON_APPROUVE.json'))
 validate_ledger(result);p.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
