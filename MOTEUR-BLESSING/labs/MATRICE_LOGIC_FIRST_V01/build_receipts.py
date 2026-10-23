from pathlib import Path
import sys, json, subprocess, hashlib, csv
from logic_engine import CANONICAL_WORLDS, FIELD_TO_ALIAS, FIELDS, RULES
ROOT=Path(__file__).resolve().parent
r=subprocess.run([sys.executable,'-m','unittest','-v','test_logic_engine.py'],cwd=ROOT,text=True,capture_output=True)
count=r.stderr.count(' ... ok')
if r.returncode != 0 or count != 22:
    print(r.stdout+r.stderr)
    raise SystemExit('Unit tests not exactly 22/22 PASS')
cov=[]
for id in CANONICAL_WORLDS:
    child=sorted(k for k in FIELD_TO_ALIAS if k.startswith(id+'.'))
    cov.append({'parent_world':id, 'mapped_L3_child_ids':child,
                'mapped_children':len(child),
                'status':'SOME_LOGIC_RULES_CONNECTED' if child else 'DOCUMENTARY_NOT_YET_CONNECTED',
                'sporting_effect_numeric_calibrated':False})
assert len(cov)==62 and sum(x['mapped_children'] for x in cov)==14
(ROOT/'COUVERTURE_62_MONDES.json').write_text(json.dumps({
    'schema':'matrice/r8/logical-engine-world-coverage/v1',
    'canonical_parent_world_count':62,
    'documentary_candidate_child_count_per_verified_R8_checkpoint':355,
    'connected_child_ids_count':14,
    'unconnected_documentary_child_ids_count':341,
    'connected_parent_world_count':14,
    'not_yet_connected_parent_world_count':48,
    'number_of_independent_numeric_IC_model_coefficients_added':0,
    'catalogue_scope':'Compact 62-world roster and 14 mapped L3 child IDs; not a reconstruction of all 355 archival contracts',
    'worlds':cov},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=sorted(x for x in ROOT.rglob('*') if x.is_file() and not x.name.startswith('AUDIT_RECETTE') and '__pycache__' not in x.parts)
manifest={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in files}
receipt={'date':'2026-10-23','schema':'matrice/r8/logic-engine-v0.1-audit-receipt',
         'original_MATRICE_R8_worlds':62,'original_documentary_L3_children':355,
         'active_child_ids_wired':14,'logic_rules':7,'teams_evaluated':2,'logic_rule_evaluations_per_match':14,
         'independent_numeric_probabilities_or_scoring_coefficients_added':0,
         'unit_tests_passed':count,'unit_tests_total':22,
         'three_demo_cases_all_synthetic':True,
         'no_live_or_future_target_fact_consumed':True,
         'numeric_IC_over15':None,
         'outputs':{}}
for name in ('open','compact','unknown'):
    output=ROOT/'output'/f'{name}_match_result.json'
    d=json.loads(output.read_text())
    n={'open':'open','compact':'compact','unknown':'unknown'}[name]
    audit=json.loads((ROOT/'output'/f'{n}_contrafacts'/'receipt.json').read_text())
    receipt['outputs'][name]={'issue':d['logical_issue'], 'facts':d['input_fact_count'],
                               'alternative_state_tests':audit['tested_alternative_configurations'],
                               'same_match_IC':None}
receipt['sha256_by_file']=manifest
(ROOT/'AUDIT_RECETTE.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'tests':count,'catalogue_worlds':62,'mapped_children':14,'logic_evals':14,'demo_cases':receipt['outputs']},ensure_ascii=False,indent=2))