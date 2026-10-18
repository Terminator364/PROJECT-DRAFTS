#!/usr/bin/env python3
"""New conditional sample: 1000 H3-valid simulated plans, 112 rubric slots per plan.
Neither post-T0 targets nor derived roles are fabricated, nor inferred real Q.
This selects only valid scenarios from 9-D physical hypothesis set; selection bias explicit.
"""
from pathlib import Path
import sys, json, hashlib, csv, copy, datetime, zipfile, collections, math
ROOT=Path(__file__).resolve().parent/'RIZ112_CAHIER_MERE'
OUT=Path('/mnt/data/RIZ112_1000_SCENARIOS_112_RUBRIQUES_1000_IC_DEMO')
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'simulations/EXPERIENCE_1000'))
from simuler_1000 import latin_hypercube, case_packet, FIELDS, KEYS, RANGES, evaluate_h3, calculate
packet=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text(encoding='utf8'))
assumptions=json.loads((ROOT/'step20/ASSUMPTIONS_SYNTHETIQUES_NON_CALIBREES.json').read_text(encoding='utf8'))
registry=json.loads((ROOT/'step26/REGISTRE_TRANSVERSAL_112.json').read_text(encoding='utf8'))
name_by_id={r['rubric']:r['canonical_name'] for r in registry['rows']}
allids=[f'{i:03}' for i in range(1,113)]
assert len(name_by_id)==112
# Explicitly vary sampleable PRESTART physical primitives. Other rubrics remain in
# their original declared status; their role is reported and NEVER falsely perturbed.
CANDIDATES=1900
SEED=20261018
N=1000
DRAWS=200
candidates=latin_hypercube(CANDIDATES,SEED)
csvrows=[]
jsonlines=[]
fail=collections.Counter();accepted=0;attempted=0
for candidate_no,values in enumerate(candidates,1):
    if accepted==N: break
    attempt=case_packet(packet,values)
    phys=calculate(attempt,assumptions)['physical_account']
    h=evaluate_h3(attempt,draws=DRAWS,seed=20261017)
    attempted+=1
    if h['status']!='DEMO_ASSUMED_MECHANISMS_NOT_REAL_Q':
        fail[h['status']]+=1
        continue
    ic=h['baseline_ic_demo_percent']
    assert isinstance(ic,(int,float)) and math.isfinite(ic) and 0<=ic<=100
    accepted+=1
    sid=f'SYN_VALID_{accepted:04d}'
    record={}
    for k in allids:
        if k in attempt['case_inputs']:
            v=attempt['case_inputs'][k];slot={'role':name_by_id[k],'group':'case_inputs','state':v['state'],'value':v['value'],'unit':v['unit'],'synthetic':True}
        elif k in attempt['action_plans']:
            v=attempt['action_plans'][k];slot={'role':name_by_id[k],'group':'action_plans','state':v['status'],'value':None,'unit':None,'synthetic':True}
        elif k in attempt['correction_policies']:
            v=attempt['correction_policies'][k];slot={'role':name_by_id[k],'group':'correction_policies','state':v['status'],'value':None,'unit':None,'synthetic':True}
        elif k in attempt['target_contract']:
            # No post-T0 measurements or labels; these are OUTPUT schemas, not predictors.
            v=attempt['target_contract'][k];slot={'role':name_by_id[k],'group':'post_T0_target','state':'TARGET_PROTOCOL_DRAFT_NO_MEASUREMENT','value':None,'unit':None,'synthetic':True}
        else:
            assert k in {'043','044','046','048'}
            slot={'role':name_by_id[k],'group':'derived_role','state':'DERIVED_INTERNAL_NOT_INDEPENDENT_INPUT','value':None,'unit':None,'synthetic':True}
        record[k]=slot
    assert len(record)==112
    assert all(record[k]['value'] is None for k in [f'{x:03}' for x in range(99,113)])
    for k in KEYS:
        assert record[k]['value']==round(values[k],10)
    row={'scenario_id':sid,'candidate_sequence':candidate_no,'ic_demo_percent':ic,'scientific_ic_percent':None,'Q_real':None,
      'h3_status':h['status'],'energy_ideal_feasible':phys['energy_target_feasible_in_idealized_budget'],
      'water_preloss_feasible':phys['water_target_mass_feasible_before_losses'],
      'rubrics':record,'source_class':'SYNTHETIC_REHEARSAL_NOT_REAL_OBSERVATION',
      'varied_primitive_ids':KEYS}
    jsonlines.append(json.dumps(row,ensure_ascii=False,separators=(',',':'),allow_nan=False))
    scalar={k:(f"{record[k]['value']}" if record[k]['value'] is not None else record[k]['state']) for k in allids}
    csvrows.append({'scenario_id':sid,'candidate_sequence':candidate_no,'IC_DEMO_%':ic,'IC_SCIENTIFIQUE_%':'NON_CALIBRE',
                    'Q_REEL':'NON_MESURE','h3_status':h['status'],
                    'energie_ideale_faisable':phys['energy_target_feasible_in_idealized_budget'],
                    'eau_avant_pertes_faisable':phys['water_target_mass_feasible_before_losses'], **scalar})
assert accepted==N, f'Accepted {accepted}, candidates {CANDIDATES}, fail {fail}'
file=OUT/'1000_SCENARIOS_112_RUBRIQUES_DETAIL.jsonl';file.write_text('\n'.join(jsonlines)+'\n',encoding='utf8')
file=OUT/'1000_SCENARIOS_112_COLONNES_1000_IC_DEMO.csv'
with file.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(csvrows[0]));w.writeheader();w.writerows(csvrows)
meta={'schema':'riz112/synthetic1000-valid-112/1','scenario_count':N,'numeric_IC_DEMO_count':N,'real_Q_IC_count':0,
 'original_1000_recorded_baseline':{'count':1000,'numeric':690,'abstained':310,'status':'preserved in older archive'},
 'seed':SEED,'h3_seed':20261017,'draws_per_scenario':DRAWS,'candidate_count':CANDIDATES,
 'candidate_count_examined':attempted,'rejected_candidates_before_reaching_1000':sum(fail.values()),
 'rejection_reasons':dict(fail),'reject_sampling_conditioned_on_H3_eligibility':True,
 'design':'1900 point nine-dimensional Latin hypercube, first 1000 eligible for H3; do not estimate unconditional rates from conditional sample',
 'rubrics_per_scenario':112,'explicit_packet_records':108,'derived_internal_roles':4,
 'actually_perturbed_rubrics':KEYS,'perturbed_rubric_count':len(KEYS),
 'constant_unknown_or_predeclared_rubrics':103,'postT0_output_ids':[f'{i:03}' for i in range(99,113)],
 'scientific_ic_percent':None,'quality_threshold_applies_only_to_Q_star_proxy':85,
 'one_per_scenario':'One IC_DEMO from 200 synthetic draws per scenario; not an empirical probability',
 'warning':['Full 112 rubric columns do NOT mean 112 distinct or independently varied features',
            '14 postT0 output rubric values are deliberately null; no future leakage',
            'Conditional rejection of non-calculable scenarios induces selection bias',
            'No numerical weights for Q real were authorized',
            'This is NOT validation for MATRICE sports, only a transferable method'],
 'source_archive':'RIZ112_METHODOLOGIE_MATRICE_1000_SCENARIOS_2026-10-17.zip',
 'source_code':'generer_1000_ic112.py',
 'columns':len(csvrows[0]),'numeric_ic_summary':{'min':min(r['ic_demo_percent'] for r in csvrows) if False else min(r['IC_DEMO_%'] for r in csvrows),
    'max':max(r['IC_DEMO_%'] for r in csvrows),
    'n_at_least_85':sum(r['IC_DEMO_%']>=85 for r in csvrows)},
 'files':{}}
manifest={k:{'name':name_by_id[k], 'category': ('PHYSICAL_TWIN_VARIED' if k in KEYS else 'POST_T0_OUTCOME_NOT_OBSERVED' if 99<=int(k)<=112 else 'DERIVED_INTERNAL_NONINDEPENDENT' if k in ['043','044','046','048'] else 'PRET0_NOT_VARIED'), 'actually_varied':k in KEYS} for k in allids}
(OUT/'CATALOGUE_112_RUBRIQUES.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(OUT/'GUIDE_DE_LECTURE.md').write_text('''# RIZ112 — 1 000 scénarios calculables à 112 rubriques chacun\n\nLivraison de **1 000 lignes et 1 000 IC_DEMO numériques** issus du modèle H3 fictif, avec les **112 rubriques** explicitées (108 enregistrements et 4 rôles dérivés). Le CSV contient **120 colonnes** : huit colonnes de métadonnées et 112 rubriques. La version JSONL contient chaque sous-paramètre, son état et sa provenance synthétique.\n\n## Ce qui varie réellement\nLes neuf rubriques physiques **001,033,035,036,037,038,041,042,047** sont variées via un plan Latin hypercube. Les 103 autres rubriques sont conservées à leur statut/valeur d'origine, **pas simulées artificiellement pour faire croire à 112 effets**. Les sorties 099–112 n'ont aucune valeur post-cuisson et les rôles dérivés 043/044/046/048 ne sont pas des causes exogènes.\n\n## Pourquoi cette version possède 1 000 IC\nLe lot original de 1 000 comportait 690 IC et 310 abstentions. Pour construire **1 000 cas calculables**, le programme a généré 1 900 candidats pré-T0 et conservé les 1 000 premiers compatibles avec H3. Les refus restent comptés dans le manifeste, pas convertis en probabilités zéro. **Ce sous-échantillonnage est conditionnel et biaisé vers les cas calculables** : il ne faut pas estimer une fréquence de réussite universelle.\n\n**IC_DEMO = proportion de 200 tirages Q* fictifs ≥ 85**, et non la probabilité empirique du riz réussi. `IC_SCIENTIFIQUE_% = NON_CALIBRE`. Aucune donnée de cuisson réelle. Pour MATRICE, on ne transpose que les méthodes (dossiers pré-match, abstention, perturbations cohérentes, documentation des sources).\n\nFichiers : `1000_SCENARIOS_112_COLONNES_1000_IC_DEMO.csv` (Excel), `1000_SCENARIOS_112_RUBRIQUES_DETAIL.jsonl` (intégral), `CATALOGUE_112_RUBRIQUES.json`, `RAPPORT_VERIFICATION.json`, `generer_1000_ic112.py`.\n''',encoding='utf8')
(OUT/'generer_1000_ic112.py').write_bytes(Path(__file__).read_bytes())
for p in list(OUT.iterdir()):
 if p.is_file():meta['files'][p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(OUT/'RAPPORT_VERIFICATION.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('DONE',json.dumps({'attempted':attempted,'reject':dict(fail),'numericIC':accepted,'columns':len(csvrows[0]),'ic_stats':meta['numeric_ic_summary']},ensure_ascii=False))
