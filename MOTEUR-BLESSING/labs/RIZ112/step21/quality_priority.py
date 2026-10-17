#!/usr/bin/env python3
"""User-confirmed qualitative priority, NOT user approval of numerical weights/Q.

Priority: tenderness 101 and grain separation 102 outrank secondary quality
criteria. This file cannot compute an empirical success probability.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime

PRIORITY=('101','102')
TARGETS=tuple(f'{i:03d}' for i in range(99,113))
class QualityContractError(ValueError): pass

def contract_from_step20(draft):
    if draft['target_ids']!=list(TARGETS) or set(draft['target_rubrics'])!=set(TARGETS):
        raise QualityContractError('Step20 target contract changed')
    if draft['approved_by_user'] or draft['Q_score_formula'] is not None:
        raise QualityContractError('Expected original unapproved source; do not silently promote')
    return {
      'schema':'riz112/step21/quality-priority/v1',
      'evidence_status':'USER_APPROVED_PRIORITY_ONLY',
      'user_statement':'Oui',
      'answered_question':'Tendreté et séparation des grains prioritaires devant goût, aspect et autres qualités ?',
      'priority_tier_1_ids':list(PRIORITY),
      'priority_tier_2_ids':[i for i in TARGETS if i not in PRIORITY and i!='112' and i!='099'],
      'mandatory_safety_separate_gate':['099'],
      'decision_label_not_a_predictor':['112'],
      'candidate_measurement_protocols':{
         '101':{'instrument':'same-person blinded if feasible, or independently identified panel',
                'candidate_unit':'ordinal 0–4 (NOT yet agreed)',
                'candidate_anchors':{'0':'dure/crue ou pâteuse non conforme','1':'fortement éloignée de la tendreté souhaitée','2':'partiellement conforme','3':'globalement conforme','4':'tendreté attendue, homogène'},
                'sampling':'three spatially separated fixed-mass samples, sample time declared',
                'status':'DRAFT_NOT_APPROVED'},
         '102':{'instrument':'image standard and manually counted adherent clusters, optionally fixed-mass sample',
                'candidate_unit':'fraction of distinct grains or cluster count; protocol calibration pending',
                'sampling':'three spatial samples, same mass and cooling interval',
                'status':'DRAFT_NOT_APPROVED'}},
      'numerical_weights':None,
      'Q_score_formula':None,
      'Q_threshold_from_user':85,
      'Q_success_probability':None,
      'calibration_training_allowed':False,
      'reason':'Priority order is an ordinal preference, not a numerical score function.',
      'source':'User explicitly answered Oui to previous question; 2026-10-17',
      'postT0_targets_excluded_from_preT0_predictors':True,
    }

def validate(contract):
    if contract['priority_tier_1_ids']!=list(PRIORITY):raise QualityContractError('User-confirmed priority altered')
    if set(contract['priority_tier_1_ids'])&set(contract['priority_tier_2_ids']):raise QualityContractError('Priority overlap')
    if set(contract['priority_tier_1_ids'])|set(contract['priority_tier_2_ids'])|set(contract['mandatory_safety_separate_gate'])|set(contract['decision_label_not_a_predictor'])!=set(TARGETS):
      raise QualityContractError('The 14 outcomes are not properly segregated')
    if contract['Q_score_formula'] is not None or contract['numerical_weights'] is not None or contract['calibration_training_allowed'] is True:
      raise QualityContractError('No approval for quantitative weighting or training')
    return True

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--draft',type=Path,required=True);a.add_argument('--out',type=Path,required=True);x=a.parse_args()
    p=contract_from_step20(json.loads(x.draft.read_text(encoding='utf8')))
    validate(p);x.out.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
