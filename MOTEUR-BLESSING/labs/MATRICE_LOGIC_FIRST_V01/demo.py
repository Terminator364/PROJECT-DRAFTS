from pathlib import Path
import json
from logic_engine import analyze, compare
ROOT=Path(__file__).resolve().parent
for name in ['open_pressing_counter','compact_defense','insufficient_data']:
    case=json.loads((ROOT/'examples'/f'{name}.json').read_text(encoding='utf-8'))
    result=analyze(case)
    print('\nCAS',name,'|',result['logical_issue'],'| IC =',result['IC_over15_percent'])
    for side in ('A','B'):
        print('  ',side,':',', '.join(result['teams'][side]['enabled_primary_routes']) or '(aucun chemin entièrement confirmé)')
case=json.loads((ROOT/'examples'/'open_pressing_counter.json').read_text(encoding='utf-8'))
flip=compare(case,'B.ATTACK_BUILDUP.BALL_SECURITY_PRESSURE','HIGH')
print('\nCONTREFACTUEL: B devient plus fiable sous pression')
print('Changements:',flip['changed_rule_statuses'])
print('\nSTATUT : moteur logique de recherche, pas de prédiction d’IC calibrée.')