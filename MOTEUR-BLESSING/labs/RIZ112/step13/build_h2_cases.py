#!/usr/bin/env python3
"""Deterministic 100 full 112-rubric packets with nested pre-T0 conditions and outcomes."""
from __future__ import annotations
import json,random,copy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step13'))
from hierarchical_engine import _set
from prospective_branches import evaluate_branches
SEED=20261017;N=100
r=random.Random(SEED)
base=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text())
parent=Path(__file__).parent
out_packets=[];out_results=[]
for i in range(N):
 p=copy.deepcopy(base)
 p['prestart']['preparation_id']=f'H2_SYNTH_{i+1:03d}'
 _set(p,'001',round(r.uniform(115,265),1),'rice_mass_g')
 _set(p,'041',round(r.uniform(360,840),1),'power_W')
 material=r.choice(['copper','iron','ceramic_rated','wood_unrated'])
 heat_path='indirect_metal_insert' if material=='wood_unrated' else 'direct'
 diameter=round(r.uniform(14,26),2);wall=round(r.uniform(1,5),2)
 water=round(r.uniform(160,540),1)
 # Case 002 is total predeclared resource, not an infinite supply.
 stock=round(water+r.uniform(0,140),1)
 _set(p,'002',stock)
 rice={'water_capacity_g_per_g':round(r.uniform(.8,2.0),2),
       'hot_time_needed_min':round(r.uniform(8,22),2),
       'surface_starch_index':round(r.uniform(.05,.95),3),
       'rinse_removal_fraction':round(r.uniform(.1,.7),3)}
 policy={'trigger_shortfall_g':round(r.uniform(0,30),1),
         'dose_g':round(r.uniform(10,125),1),
         'adherence_probability':round(r.uniform(.3,.95),2)}
 kwargs={'material':material,'heat_path':heat_path,'diameter_cm':diameter,'wall_mm':wall,
         'lid_present':r.choice([True,False]),'water_g':water,
         'rice_profile':rice,'conditional_water_policy':policy,'draws':120,'seed':SEED+i}
 report=evaluate_branches(p,**kwargs)
 out_packets.append({'id':p['prestart']['preparation_id'],'source_packet_112':p,
     'nested_subparameters_pre_T0':kwargs,'target_contract':'FIXED_STAGE9_QSTAR_85'})
 out_results.append({'id':p['prestart']['preparation_id'],
   'status':report['status'],'baseline_ic_demo_percent':report['baseline_ic_demo_percent'],
   'conditional_plan_ic_demo_percent':report['conditional_plan_ic_demo_percent'],
   'delta_pp':report['conditional_plan_delta_percentage_points'],
   'anticipated_events':report['forecast_conditional_events'],
   'policy_exec_events':report['hypothetical_policy_executions'],
   'avg_shortfall_g':report['expected_water_shortfall_g'],
   'active_parents':report['active_parent_cases']})
for name,records in [('H2_100_SCENARIOS_112.jsonl',out_packets),('H2_100_RESULTS.jsonl',out_results)]:
 (parent/name).write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in records),encoding='utf8')
changes=sum(a['delta_pp']!=0 for a in out_results)
summary={'schema':'riz112/hierarchical-100-summary/h2','generated':N,'all_packets_contain_112_roles':all(len(x['source_packet_112']['case_inputs'])==44 and len(x['source_packet_112']['action_plans'])==37 and len(x['source_packet_112']['correction_policies'])==13 and len(x['source_packet_112']['target_contract'])==14 for x in out_packets),
 'derived_forecast_roles_not_user_inputs':4,'total_role_contract':112,'seed':SEED,'draws_each':120,'accepted_safe_process_scenarios':N,'conditional_plan_changes_demo_ic':changes,
 'same_demo_ic_despite_variation':N-changes,
 'mean_baseline_ic_demo_percent':round(sum(x['baseline_ic_demo_percent'] for x in out_results)/N,2),
 'mean_conditional_ic_demo_percent':round(sum(x['conditional_plan_ic_demo_percent'] for x in out_results)/N,2),
 'sample_first_5':out_results[:5],
 'warning':'Synthetic QSTAR ONLY; not empirically calibrated, not food safety certificate; 112 paths NOT all quantitatively modeled'}
(parent/'H2_POPULATION_REPORT.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
