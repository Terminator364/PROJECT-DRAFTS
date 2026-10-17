#!/usr/bin/env python3
"""Bounded V1 engineering release gate; never fake real-world quality or IC.

This gate is deterministic offline and reads canonical archived lab artifacts.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

class ClosureError(ValueError): pass

def load(root: Path, relative: str) -> dict:
    path = root / relative
    if not path.exists(): raise ClosureError('Missing required evidence: ' + relative)
    try: return json.loads(path.read_text(encoding='utf-8'))
    except (ValueError, UnicodeError) as exc: raise ClosureError('Invalid JSON: ' + relative) from exc

def inspect(root: Path) -> dict:
    src=load(root,'step26/REGISTRE_TRANSVERSAL_112.json')
    a=load(root,'step21/PRIORITY_CONFIRMED_NO_WEIGHTS.json')
    b=load(root,'step25/PROTOCOLE_Q_MESURES_PROPOSE_NON_APPROUVE.json')
    d=load(root,'step25/FICHE_VIDE_PRE_POST_T0.json')
    e=load(root,'step23/READINESS_NO_REAL_TRIALS.json')
    p=load(root,'step27/PROPOSITION_Q_DECISION_A_VALIDER.json')
    cp=load(root,'step26/CHECKPOINT_STEP26_20261017.json')
    if src.get('total')!=112 or len(src.get('rows',[]))!=112: raise ClosureError('112 rubric register incomplete')
    counts=src.get('counts',{})
    expected={'NOT_PROVEN_PHYSICAL_Q_EFFECT':60,'POST_T0_TARGET_ONLY':14,'PRE_T0_PLAN_RESOURCE_ROUTE_ONLY':29,'THEORETICAL_PHYSICAL_INTERMEDIATE_ONLY':9}
    if counts!=expected or sum(counts.values())!=112: raise ClosureError('Rubric partition unproven or divergent')
    ids=[x.get('rubric') for x in src['rows']]
    if sorted(ids)!=[f'{i:03d}' for i in range(1,113)]: raise ClosureError('Rubric IDs duplicate or omitted')
    if a.get('priority_tier_1_ids')!=['101','102'] or a.get('numerical_weights') is not None or a.get('Q_score_formula') is not None: raise ClosureError('User priority improperly promoted to numeric rule')
    if b.get('approved_by_user') is not False or b.get('Q_score_formula') is not None or p.get('Q_score_approved') is not False or p.get('Q_score_formula') is not None: raise ClosureError('Q approval silently fabricated')
    if sorted(b.get('target_ids',[]))!=[f'{i:03d}' for i in range(99,113)]: raise ClosureError('Post T0 targets missing')
    if d.get('status')!='EMPTY_USER_FILLABLE_TEMPLATE_NOT_EVIDENCE' or d.get('scientific_ic_percent') is not None or d.get('Q_score') is not None or d.get('real_rice_trial_count')!=0: raise ClosureError('Fake trial or outcome')
    if cp.get('real_trials_count')!=0 or cp.get('scientific_ic_percent') is not None: raise ClosureError('Empirical evidence status changed; reassess instead of assuming zero')
    if src.get('real_Q_causal_effects_proven')!=0 or src.get('scientific_ic_percent') is not None: raise ClosureError('Unsupported real causal effects claimed')
    if p['proposed_model']!='NON_COMPENSATORY_TOP_TIER_WITH_WEIGHTED_SECONDARY_PREVIEW' or p['candidate_Q_preview_executable'] is not False: raise ClosureError('Proposal incorrectly activated')
    if 'scientific_ic_percent' in e and e['scientific_ic_percent'] is not None: raise ClosureError('Evidence gate failed')
    fingerprints={k:hashlib.sha256((root/k).read_bytes()).hexdigest() for k in ['step21/PRIORITY_CONFIRMED_NO_WEIGHTS.json','step25/PROTOCOLE_Q_MESURES_PROPOSE_NON_APPROUVE.json','step26/REGISTRE_TRANSVERSAL_112.json','step27/PROPOSITION_Q_DECISION_A_VALIDER.json']}
    return {
      'schema':'riz112/engineering-v1-closure/v1',
      'release':'ENGINEERING_V1_READY__NOT_EMPIRICALLY_CALIBRATED',
      'finality':'ENGINEERING_GATE_CLOSED__EXTERNAL_EMPIRICAL_GATE_OPEN',
      'canonical_resume_code':'Moteur/continue',
      'priority_user_confirmed':['101','102'],
      'Q_formula_approved':False,'Q_user_approval_required':True,
      'Q_measurement_candidate_ready':True,
      'rubric_count':112,'partition_counts':counts,
      'original_112_rubric_empirical_effects_proven':0,
      'real_rice_trials':0,'scientific_ic_percent':None,
      'source_digests_sha256':fingerprints,
      'next_external_action':'Confirm Q measurement protocol (including numeric thresholds/weights) and carry out real independent rice trials with frozen preT0 packets and postT0 assessment',
      'why_no_calibrated_IC':'No approved quality measure, no real paired trials, no held-out calibration; technical tests never establish causal accuracy'
    }

def main():
    p=argparse.ArgumentParser();p.add_argument('--lab-root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path,default=None)
    a=p.parse_args();report=inspect(a.lab_root)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('RIZ112_V1_ENGINEERING_READY 112/112 ROLES; REAL_IC=null; NO_VALIDATED_CAUSAL_Q_EFFECTS')

if __name__=='__main__':main()
