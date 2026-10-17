from __future__ import annotations
import json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step13'))
from hierarchical_engine import evaluate,registry
p=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text())
catalogue=json.loads((ROOT/'reference/step4/CATALOGUE_112_ROLES_ETAPE4.json').read_text())
HERE=Path(__file__).parent
cases=[
  ('A_cuivre_couvercle',dict(material='copper',diameter_cm=18,wall_mm=2)),
  ('B_ceramique_couvercle',dict(material='ceramic_rated',diameter_cm=18,wall_mm=2)),
  ('C_cuivre_sans_couvercle',dict(material='copper',diameter_cm=18,wall_mm=2,lid_present=False)),
  ('D_cuivre_moins_eau',dict(material='copper',diameter_cm=18,wall_mm=2,water_g=180)),
  ('E_bois_contact_direct_non_adapte',dict(material='wood_unrated',diameter_cm=18,wall_mm=2)),
  ('F_bois_avec_insert_metal_hypothetique',dict(material='wood_unrated',heat_path='indirect_metal_insert',diameter_cm=18,wall_mm=2)),
]
allresults={k:evaluate(p,seed=3,draws=500,**opts) for k,opts in cases}
allresults={'schema':'riz112/hierarchy-scenarios/h1','source_rubric_count':112,'draws':500,'seed':3,
            'scenarios':allresults,'scientific_ic':None,'measured_trails':0,
            'warning':'THERMAL INTERFACE ASSUMED; Q*_DEMO NOT REAL RICE QUALITY. WOOD DIRECT PATH UNSAFE.'}
(HERE/'H1_SCENARIOS.json').write_text(json.dumps(allresults,ensure_ascii=False,indent=2)+'\n')
reg=registry(catalogue)
(HERE/'H1_HIERARCHIE_112.json').write_text(json.dumps({'schema':'riz112/112-hierarchical-scope/h1',
   'coverage':'112 rubrics have structured children; only nominated mechanisms executable in H1',
   'empirically_validated_effect_count':0,'rubrics':reg},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'rubrics':len(reg),'scenarios':{k:{'status':v['status'],'ic_demo':v['ic_demo_percent'],'eta':v.get('thermal_path',{}).get('effective_eta')} for k,v in allresults['scenarios'].items()}},ensure_ascii=False,indent=2))
