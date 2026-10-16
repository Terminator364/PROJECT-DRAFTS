#!/usr/bin/env python3
"""Deterministic next-action backlog for the 297 genuinely unmapped requirements.

Priorities represent audit workflow dependencies, NOT scientific effect strength.
No source or formula is claimed implemented by this report.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
from requirements_plan_v3 import ROOT,build_plan
from contract_gate_v4 import build_contracts

SCHEMA='MOTEUR_MB1_V4_297_RESEARCH_BACKLOG'
PRIMARY_READY_LANES={'FIXTURE_RULES','MATCH_HISTORY','SCHEDULE_TRAVEL','STADIUM_VENUE'}

def build_backlog(root:Path=ROOT)->dict:
    plan=build_plan(root)
    gates=build_contracts(root)['contracts']
    rows=[]
    for e in plan['entries']:
        if e['semantic_class']!='NOT_LINKED':continue
        if e['role']=='GATE':
            priority='P0_GOVERNANCE_BEFORE_FEATURES'
            next_action='DEFINE_AND_PROVE_GATE_EVIDENCE'
        elif e['role']=='OUTPUT_ONLY':
            priority='P3_OUTPUT_DERIVED_NON_INDEPENDENT'
            next_action='TRACE_GENERATING_PRIMITIVES_AND_NO_DOUBLE_COUNT'
        elif e['source_lane'] in PRIMARY_READY_LANES:
            priority='P1_DEFINE_MEASURE_WITH_BASIC_PREMATCH_HISTORY'
            next_action='DEFINE_OBSERVABLE_NUMERATOR_DENOMINATOR_WINDOW'
        elif e['source_lane']=='MODEL_GOVERNANCE':
            priority='P0_GOVERNANCE_BEFORE_FEATURES'
            next_action='DESIGN_UNCERTAINTY_AND_VALIDATION_CONTRACT'
        else:
            priority='P2_SPECIALIST_SOURCE_AND_MEASURE_DESIGN'
            next_action='SECURE_DATED_SOURCE_AND_DEFINE_MEASUREMENT'
        rows.append({'id':e['id'], 'world':e['world'], 'role':e['role'],
            'proposal':e['requirement'], 'source_lane_candidate':e['source_lane'],
            'priority':priority,'next_action':next_action,
            'gate_contract_field':gates[e['id']]['field'] if e['id'] in gates else None,
            'observed_value':None,'numerical_unit':'UNSPECIFIED_REQUIRES_SPECIALIZATION',
            'measurement_window':'NOT_YET_DEFINED',
            'independent_historical_PIT_proof':'NOT_COLLECTED',
            'scoring_weight':None,'feature_enabled':False})
    ids=[r['id'] for r in rows]
    if len(rows)!=297 or len(set(ids))!=297:
        raise ValueError('all 297 unlinked contracts must be represented exactly once')
    if {r['id'] for r in rows if r['role']=='GATE'}-set(gates):
        raise ValueError('unknown governance mapping')
    return {'schema':SCHEMA,'status':'ACTIONABLE_RESEARCH_DESIGN_NOT_IMPLEMENTED',
            'unlinked_proposals_total':297,'gate_subparameters_with_typed_contracts':len(gates),
            'priority_counts':dict(sorted(Counter(r['priority'] for r in rows).items())),
            'source_lane_counts':dict(sorted(Counter(r['source_lane_candidate'] for r in rows).items())),
            'prototype_calculations_from_partial_class':['SCORING_HISTORY::R01','REST_CONGESTION::R01'],
            'prototype_calculations_PIT_certified':False,
            'verified_source_availability':False,'scoring_authorized':False,
            'entries':sorted(rows,key=lambda x:(x['priority'],x['world'],x['id']))}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args()
    if a.output.exists():parser.error('versioned output already exists; do not overwrite')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    report=build_backlog(a.root)
    a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'unlinked':297,'priorities':report['priority_counts']}))
if __name__=='__main__':main()