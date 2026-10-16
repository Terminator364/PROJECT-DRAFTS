#!/usr/bin/env python3
"""Run three existing prestart fixtures and adverse counterfactuals; avoid real outcome labels."""
from pathlib import Path
import copy,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from ic_simulation_v1 import simulate

def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def main():
 c=json.loads((HERE/'DEMONSTRATION_CONTRACT.json').read_text())
 names=['A_couvercle_ajuste','B_couvercle_fuyant','C_chaleur_faible']
 results=[]
 for name in names:
  p=json.loads((ROOT/'step6'/'examples'/(name+'_112.json')).read_text())
  r=simulate(p,c,3000,20261016);write(HERE/(name+'_IC_DEMO.json'),r)
  results.append({'case':name,'ic_demo_percent':r['ic_demo_percent'], 'scientific_ic_percent':None,
    'Q_demo_p50':r['simulated_Q_demo_p05_p50_p95'][1],
    'CI_MC_only':r['mc_95_percent_interval_for_demo_ONLY']})
  if name==names[0]:
   p_water=copy.deepcopy(p);p_water['prestart']['inputs']['water_added_g']['value']-=60;p_water['case_inputs']['035']['value']-=60
   q=simulate(p_water,c,3000,20261016)
   write(HERE/'TEST_SENSIBILITE_MOINS_EAU.json',q)
   c_stress=copy.deepcopy(c);c_stress['proxy_scales']['free_water_scale_g_per_g']=0.9
   q2=simulate(p,c_stress,3000,20261016)
   write(HERE/'TEST_SENSIBILITE_CRITERE.json',q2)
 table={'baseline':results,'counterfactual_A_minus_60g':q['ic_demo_percent'],
        'A_modified_scoring_rubric':q2['ic_demo_percent'],
        'interpretation':'These are NOT observed rice probabilities, only simulated hypothetical proxy events.'}
 write(HERE/'COMPARAISON_SCENARIOS_ET_SENSIBILITE.json',table)
 print(json.dumps(table,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
