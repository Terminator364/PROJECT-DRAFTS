#!/usr/bin/env python3
"""RIZ112 H4: aggregate 22 rubric diagnostic pathways, never a calibrated IC."""
from __future__ import annotations
from functional_mechanisms_h4 import evaluate_h4_diagnostics
from functional_mechanisms_h4b import evaluate_h4b, RUBRICS

H4A_RUBRICS=('003','061','049','082','029','030','054')
GAPS_H3=set(H4A_RUBRICS)|set(RUBRICS)

def evaluate_h4(packet:dict, *, a:dict|None=None, b:dict|None=None)->dict:
    """No mutation; the same pre-T0 packet is the authority for both submodels.

    Numerical diagnostic coverage != validated prediction. Missing evidence
    remains explicit in each group and cannot be promoted to Q/IC.
    """
    part_a=evaluate_h4_diagnostics(packet,**(a or {}))
    part_b=evaluate_h4b(packet,b)
    if len(GAPS_H3)!=22 or set(part_a['rubric_paths'])|set(part_b['rubric_paths'])!=GAPS_H3:
        raise ValueError('H3 gap coverage mismatch')
    return {'schema':'riz112/H4/composite/v1',
        'status':'22_RUBRIC_DIAGNOSTIC_CONTRACTS__NOT_CALIBRATED',
        'h3_original_gaps':22,'rubrics_with_diagnostic_contract':22,
        'rubric_ids':sorted(GAPS_H3),
        'number_of_new_h4_mechanism_groups':10,
        'a':part_a,'b':part_b,
        'real_Q_effects_estimated':0,
        'scientific_ic_percent':None,
        'post_T0_predictors':0,
        'actual_observations':0,
        'product_promoted':False,
        'next_gate':'Observe controlled pre-T0 to post-T0 trials, predefine Q, measure repeatability, calibrate and validate out-of-sample; then transfer only architecture to sport'}