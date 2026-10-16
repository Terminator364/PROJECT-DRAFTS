#!/usr/bin/env python3
"""Build a 112-case gap ledger and dry-run reports; no external data/score."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'step7'))
from graph_governor import analyze7, edges_audit
from engine112 import catalogue
OUT=ROOT/'step7';OUT.mkdir(exist_ok=True)
scenarios={}
for n in ('A_couvercle_ajuste','B_couvercle_fuyant','C_chaleur_faible'):
 p=json.loads((ROOT/f'step6/examples/{n}_112.json').read_text(encoding='utf8'))
 d=analyze7(p)
 scenarios[n]=d
 (OUT/f'{n}_v7_report.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
original=scenarios['A_couvercle_ajuste'];cat=catalogue()
unlinked=set(original['graph_governance']['unlinked_to_Q112'])
linked=set(original['graph_governance']['structural_hypothesis_paths_to_Q112'])
physical=set(original['quantified_physical_case_paths'])
trace={row['id']:row for row in original['case_112_contract'].get('unused',[])} if False else None
from engine112 import PRESTART, FORECAST, ACTIONS, POLICIES, OUTCOMES
records=[]
for id in sorted(cat):
 if id in physical: status='TOY_PHYSICAL_OR_DERIVED_PATH_NOT_VALIDATED'
 elif id in OUTCOMES:status='FUTURE_TARGET_MEASUREMENT_ONLY'
 elif id in linked:status='STRUCTURAL_HYPOTHESIS_NO_NUMERIC_EFFECT'
 else:status='NOT_CONNECTED_TO_Q112_IN_DECLARED_GRAPH'
 if id in PRESTART:input_kind='SOURCE_ATTESTED_PRESTART_OR_UNKNOWN'
 elif id in FORECAST:input_kind='DERIVED_WITH_PARTIAL_OR_MISSING_FORMULA'
 elif id in ACTIONS:input_kind='PREDECLARED_ACTION_NOT_ACTUAL_EVENT'
 elif id in POLICIES:input_kind='PREDECLARED_TRIGGER_POLICY_NOT_ACTUAL_CORRECTION'
 else:input_kind='POSTSTART_LABEL_NOT_PRESTART_INPUT'
 if id in OUTCOMES:next_step='Define and preregister reproducible poststart measurement; do not use as input'
 elif id in linked and id not in physical:next_step='Define physical/statistical law and independent evidence before numerical scoring'
 elif id in physical:next_step='Bench-test the existing approximation against repeated real observations'
 else:next_step='Editorially identify justified directed dependencies and evidence; do not fabricate link to reach 112'
 records.append({'id':id,'name':cat[id]['name'],'role_input_contract':input_kind,
  'v7_graph_relation_status':status,'reaches_final_Q112_in_declarative_graph':id in linked,
  'physical_numeric_path_toy_only':id in physical,'empirical_effect_on_Q_validated':False,
  'next_step':next_step})
counts={k:sum(r['v7_graph_relation_status']==k for r in records) for k in sorted({r['v7_graph_relation_status'] for r in records})}
assert len(records)==112 and len(linked)==50 and len(unlinked)==62
r={'schema':'riz112/stage7/112-gap-ledger/v1','case_count':112,'status_counts':counts,
   'rationale':'No forced path insertion for coverage; 112 cases must be documented but future labels are never predictors',
   'cases':records,'user_mandate':'Give every case a useful justified role in final predictive system without fake numeric effects',
   'next_gate':'Specify/measure missing physical or statistical relations and preregister Q before collecting real trials'}
(OUT/'GAPS_112_V7.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'cases':len(records),'status_counts':counts,'A_checks':original['feasibility']['counts'],
  'B_checks':scenarios['B_couvercle_fuyant']['feasibility']['counts'],
  'C_checks':scenarios['C_chaleur_faible']['feasibility']['counts']},ensure_ascii=False,indent=2))
