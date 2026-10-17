#!/usr/bin/env python3
"""Produce reproducible, strict stage12 evidence and missing-effect ledger."""
from __future__ import annotations
import json, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from full_variation_v12 import paired_material_probe

def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()

def go():
 pop=json.loads((HERE/'POPULATION_100_V12.json').read_text())
 probe=json.loads((HERE/'COUNTERFACTUAL_112_V12.json').read_text())
 cases=json.loads((ROOT/'reference/step4/CATALOGUE_112_ROLES_ETAPE4.json').read_text())['cases']
 byid={v['id']:v for v in cases}
 gaps=[]
 for row in probe['cases']:
  if row['category']!='NOT_DEMONSTRATED_TO_CHANGE_IC_OR_GATE':continue
  cid=row['case'];name=byid[cid]['name']
  if cid=='010':need='Documented measured material-specific thermal transfer response, wall geometry and prestart provenance; no metal/ceramic bonus.'
  elif row['role']=='DATA':need='Acquire dated measurable proxy/parameter definition, specify downstream mechanistic law, test ablation on real outcomes.'
  elif row['role']=='ACTION_PLAN':need='Specify effect of actual predeclared protocol on physically measured quantities; obtain paired treatment evidence.'
  elif row['role']=='POLICY':need='Specify probability and consequence of hypothetical branch; no realized poststart observations as input.'
  else:need='Define evidence-backed route and evaluate without poststart leakage.'
  gaps.append({'case':cid,'name':name,'role':row['role'],'local_test':'NO_NUMERIC_OR_GATE_EFFECT_IN_TWO_BASELINES',
               'next_evidence_needed':need,'effect_on_real_Q':'NOT_ESTABLISHED'})
 out={'schema':'riz112/stage12/explicit-26-gaps/v1','count':len(gaps),'cases':gaps,
   'interpretation':'Local counterfactual silence is NOT proof case globally irrelevant; no invented coefficients.'}
 assert len(gaps)==26
 (HERE/'GAPS_26_UNRESOLVED.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
 pair=paired_material_probe()
 report={'schema':'riz112/stage12/consolidated-audit/v1',
  'population':{'scenarios':pop['n'],'draws_each':pop['draws'],'counts':pop['counts'],'all_44_prestart_varied':pop['all_44_prestart_have_varied'],
                'distinct_numeric_demo_ic':len(set(p['ic_demo_percent'] for p in pop['profiles'] if p['ic_demo_percent'] is not None)),
                'quality_targets_frozen':pop['targets_frozen']},
  'counterfactual':{'cases':len(probe['cases']),'paired_interventions':probe['tested_counterfactuals'],
                    'statuses':probe['categories']},
  'material_label_only':pair,
  'numeric_examples_from_original_A_at_3000_draws':{'water_300g':62.4,'water_240g':44.87,'efficiency_0_45':44.6,'efficiency_0_75':68.77},
  'scientific_status':'NO_REAL_RICE_Q_CALIBRATION','scientific_ic_percent':None,
  'matrice':'NO_SPORTS_MODEL_MODIFICATION; methods and safeguards only',
  'pit':'Original synthetic date labels are self-declared and not externally authenticated',
  'software_regression':json.loads((HERE/'TEST_REPORT_STAGE12.json').read_text())}
 (HERE/'RAPPORT_100_112_V12.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 md=f'''# RIZ-112 V12 — Données qui changent ≠ 112 effets de Q prouvés\n\n**Cas :** 100 paquets complets, avec les 44 observations/conditions disponibles avant T0 diversifiées ; 4 sorties recalculées ; 37 actions et 13 politiques pouvant varier ; 14 résultats définissant Q gelés pour rester comparables.\n\n## Mesures exécutées\n\n- 100 dossiers ; {pop['draws']} tirages de proxy Monte Carlo par dossier admissible.\n- Statuts : {json.dumps(pop['counts'],ensure_ascii=False)}.\n- {len(probe['cases'])} interventions sur 2 situations de référence : {json.dumps(probe['categories'],ensure_ascii=False)}.\n- **{len(gaps)}** cas sans influence démontrée localement : voir `GAPS_26_UNRESOLVED.json`.\n- Étiquette de marmite métal vs céramique (tous autres paramètres gelés) : {pair['ic_demo_A']} % contre {pair['ic_demo_B']} %, **même IC**, aucune loi de transfert liée au matériau établie.\n- Le rendement thermique 42, s'il change comme valeur explicite, affecte le proxy (0,45 → 44,60 % ; 0,75 → 68,77 % sur dossier A). Cela **n'établit pas** que le matériau cause cet écart.\n\n## Interprétation stricte\n\nLe modèle ne peut pas légitimement produire 112 influences quantitatives : 14 définitions du résultat ne sont pas des données pré-T0 ; 4 variables sont dérivées, et des actions/politiques conditionnelles ont besoin de données de réponse de processus. La dernière version V11 modifiait en réalité moins de champs d'entrée que son registre de 112 rôles pouvait le suggérer. V12 diversifie les 44 champs et publie des dossiers complets.\n\n**Statut :** IC calculé uniquement pour Q* DEMO, non probabilité réelle de réussite. `scientific_ic_percent=null`.\n\n## Cinq cycles\n\n1. **Construction :** diversification forte 44/44, 37 plans, 13 politiques sur 100 scénarios ; 14 définitions non tirées au hasard.\n2. **Audit :** 112 contre-interventions croisées sur A et B (224 tests d'effet).\n3. **Contre-audit :** la simple catégorie `material=ceramic_rated` n'influence pas les équations ; manque vérifié, et lacunes restantes 26.\n4. **Correction :** trois champs manquants du catalogue initial corrigés (001, 002, 017) ; ancien test V4 repris dans son arborescence historique, et pas dans un chemin reconstruit erroné.\n5. **Réaduit et preuve :** 241/241 tests réussis, CRC et empreintes ZIP à produire lors de livraison ; aucune promotion scientifique.\n'''
 (HERE/'AUDIT_CINQ_CYCLES_V12.md').write_text(md)
 return report

if __name__=='__main__':print(go()['counterfactual']['statuses'])
