#!/usr/bin/env python3
"""Candidate metrology protocol for rice quality. No scoring or approval implied.

No numeric weights, composite Q, food safety certification, or learned probability.
User's confirmed preference is ordinal: tenderness & separation are primary.
"""
from __future__ import annotations
import json
from pathlib import Path

TARGETS=[f'{i:03d}' for i in range(99,113)]
PRIORITY=['101','102']
class ContractError(ValueError):pass

PROPOSED_METHODS={
 '099': ('food_safety_separate','Food safety checklist and independent verified practices; NOT a sensory score', 'PASS/FAIL/UNKNOWN'),
 '100': ('descriptive','Weigh cooked yield or count portions on stated serving plates','g or count'),
 '101': ('priority_ordinal','Blind three-location tenderness check, with separate under/overcooking direction','ordinal 0..4 + direction'),
 '102': ('priority_fraction','On three fixed-location samples, count separable grains out of all observed grains','fraction 0..1'),
 '103': ('descriptive','Compare three pot locations for within-batch texture uniformity','ordinal 0..4'),
 '104': ('descriptive','Count broken vs whole grains on standardized samples','fraction 0..1'),
 '105': ('descriptive','Measure remaining free water after agreed interval, preferably by mass','g or observable ordinal'),
 '106': ('descriptive','Count visibly burnt areas and mass; note smoke/odour separately','g or area fraction'),
 '107': ('descriptive','Measure temperature at the declared serving time','degrees Celsius'),
 '108': ('secondary_sensory','Blind taste panel, standardized scale','ordinal 0..4'),
 '109': ('secondary_sensory','Blind aroma panel, standardized scale','ordinal 0..4'),
 '110': ('secondary_sensory','Blind photo/visual rating and description','ordinal 0..4'),
 '111': ('descriptive','Repeat primary texture measurements at agreed interval','ordinal 0..4'),
 '112': ('label_only','Independent overall judgment after observations, not predictor','UNDECIDED/GOOD/NOT_GOOD')
}

def propose(step20:dict,step21:dict)->dict:
    if step20.get('approved_by_user') is not False or step20.get('Q_score_formula') is not None:
        raise ContractError('Baseline Q source no longer in draft status')
    if step20.get('target_ids')!=TARGETS or set(step20.get('target_rubrics',{}))!=set(TARGETS):
        raise ContractError('Missing or changed quality targets')
    if step21.get('priority_tier_1_ids')!=PRIORITY or step21.get('numerical_weights') is not None:
        raise ContractError('User confirmation only covers ordinal priority')
    rows={}
    for ident in TARGETS:
        kind,method,unit=PROPOSED_METHODS[ident]
        rows[ident]={
         'name':step20['target_rubrics'][ident]['canonical_name'],
         'category':kind,'candidate_method':method,'candidate_unit':unit,
         'standardized_sample_locations':['top','middle','bottom'] if ident in PRIORITY else [],
         'assessor_blinding':'RECOMMENDED_NOT_APPROVED' if ident in PRIORITY or ident in ('108','109','110') else 'NOT_DEFINED',
         'timing_after_service_minutes':None,'sample_mass_g':None,
         'instrument_or_rater_approved':False,'measurement_approved':False,
         'field_value':None,'status':'PROPOSED_NOT_OBSERVED'
        }
    return {
      'schema':'riz112/step25/quality-metrology-proposal/v1',
      'status':'PROPOSAL_NOT_APPROVED',
      'user_confirmed_only':{'priority_tier':['101','102'],'quality_goal':'white rice for two people','Q_pass_threshold':85},
      'target_ids':TARGETS,'rubrics':rows,
      'candidate_tenderness_scale':{
       'unit':'ordinal 0..4 PROPOSED',
       'levels':{'0':'far outside acceptable texture','1':'markedly outside','2':'partially matches','3':'mostly desired','4':'desired, consistent texture'},
       'direction_required_when_below_4':['too_firm','too_soft','heterogeneous','unknown'],
       'measurement_locations':['top','middle','bottom'],
       'approval_status':'PROPOSED'},
      'candidate_separation_measure':{'unit':'fraction of separated grains','range':[0,1],
        'sample_protocol':'count discernible grains and separately adhering grains in three spatial samples; denominator strictly positive',
        'thresholds_for_0_to_4':None,'approval_status':'PROPOSED'},
      'candidate_decision_structures':[
       {'id':'NON_COMPENSATORY_PRIORITY','description':'Tenderness and separation must both clear agreed gates; secondary qualities cannot offset major failure of either','proposed_gates':None,'numeric_Q_formula':None},
       {'id':'TWO_TIER_WEIGHTED','description':'First-tier tenderness and separation outweigh each secondary attribute; explicit weights/aggregator and thresholds require separate user approval','proposed_weights':None,'numeric_Q_formula':None}
      ],
      'safety_protocol':'INDEPENDENT_NOT_CERTIFIED_BY_Q',
      'Q_score_formula':None,'Q_numerical_weights':None,'Q_success_label':None,
      'approved_by_user':False,'scientific_ic_percent':None,'real_trials_count':0,
      'no_postT0_predictor_leakage':True,
      'open_approvals':['final sample size and time window','tenderness anchors and direction','grain-separation denominator and thresholds','food safety independent safeguards','aggregation policy/weights if used','rater blinding and repeatability'],
      'scientific_claim':'NONE; only draft measurement proposal'
    }

def validate_proposal(contract:dict)->bool:
    if contract.get('schema')!='riz112/step25/quality-metrology-proposal/v1':raise ContractError('Incorrect proposal type')
    if contract.get('status')!='PROPOSAL_NOT_APPROVED' or contract.get('approved_by_user') is not False:
        raise ContractError('No user approval was given for Q measurement scheme')
    if contract.get('Q_score_formula') is not None or contract.get('Q_numerical_weights') is not None:
        raise ContractError('Unapproved formula or coefficients')
    if contract.get('scientific_ic_percent') is not None or contract.get('real_trials_count')!=0:
        raise ContractError('No empirical outcome/probability available')
    if contract.get('target_ids')!=TARGETS or set(contract.get('rubrics',{}))!=set(TARGETS):raise ContractError('Target ids drift')
    if contract.get('user_confirmed_only',{}).get('priority_tier')!=PRIORITY:raise ContractError('Priority drift')
    for i,row in contract['rubrics'].items():
        if row.get('status')!='PROPOSED_NOT_OBSERVED' or row.get('field_value') is not None or row.get('measurement_approved') is not False:
            raise ContractError('Premature observation/approval '+i)
    if contract['rubrics']['099']['category']!='food_safety_separate' or contract['rubrics']['112']['category']!='label_only':
        raise ContractError('Outcome role leakage')
    if any(mode.get('numeric_Q_formula') is not None for mode in contract['candidate_decision_structures']):
        raise ContractError('No formula is approved')
    return True

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--step20',type=Path,required=True);ap.add_argument('--step21',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 result=propose(json.loads(a.step20.read_text(encoding='utf8')),json.loads(a.step21.read_text(encoding='utf8')))
 validate_proposal(result);a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
