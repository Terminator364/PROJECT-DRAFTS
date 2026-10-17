#!/usr/bin/env python3
"""Run 100 H2 packets through H3 without poststart observations; write reproducible reports."""
import copy,json,random,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step14'))
from anticipatory_physics_h3 import evaluate_h3

fixture=ROOT/'step13/H2_100_SCENARIOS_112.jsonl'
source=[json.loads(s) for s in fixture.read_text(encoding='utf8').splitlines() if s.strip()]
assert len(source)==100
rng=random.Random(20261017)
results=[];n_numeric=0;n_change=0
for i,row in enumerate(source):
    p=row['source_packet_112'];preset=row['nested_subparameters_pre_T0']
    # Four explicit PRE-T0 assumptions added: no future information.
    attrs={'source_uptime':round(rng.uniform(.75,1),4),
           'regulation_duty':round(rng.uniform(.78,1),4),
           'ambient_C':round(rng.uniform(12,36),2),
           'ambient_UA_W_per_K':round(rng.uniform(0,1.6),4),
           'grain_length_mm':round(rng.uniform(4.5,8.5),3),
           'reference_length_mm':6.,'diffusion_ratio':round(rng.uniform(.75,1.3),3),
           'grain_aspect_ratio':3.,'reference_aspect_ratio':3.}
    common={k:preset[k] for k in ('material','heat_path','wall_mm','diameter_cm','water_g','lid_present','rice_profile')}
    common['water_policy']=preset['conditional_water_policy']
    common.update({'draws':150,'seed':20261017+i})
    try:
        out=evaluate_h3(p,**common,**attrs)
        status=out['status']; ic=out.get('baseline_ic_demo_percent')
        if ic is not None:n_numeric+=1
        if out.get('policy_delta_percentage_points',0)!=0:n_change+=1
        results.append({'id':row['id'],'status':status,'assumptions':attrs,'base_packet_roles':len(p['case_inputs'])+len(p['action_plans'])+len(p['correction_policies'])+len(p['target_contract']),
                        'ic_demo_percent':ic,'ic_demo_with_policy_percent':out.get('policy_ic_demo_percent'),
                        'policy_delta_pp':out.get('policy_delta_percentage_points'),
                        'energy_W':out.get('energy_W'),'geometry':out.get('geometry'),
                        'scientific_ic_percent':None,'model_warnings':out.get('warning',[])})
    except Exception as e:
        results.append({'id':row['id'],'status':'MODEL_ERROR','error':str(e),'scientific_ic_percent':None})
# Four controlled single-variable ablations on a fixed packet and identical MC draws.
p=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text())
base_args={'material':'copper','draws':3000,'seed':44}
variations={'baseline':{},'source_uptime_0_6':{'source_uptime':.6},
 'regulation_duty_0_5':{'regulation_duty':.5},
 'ambient_UA_1':{'ambient_UA_W_per_K':1,'ambient_C':24},
 'grain_length_9':{'grain_length_mm':9},
 'grain_length_4':{'grain_length_mm':4},
 'water_180':{'water_g':180},
 'water_180_policy':{'water_g':180,'water_policy':{'trigger_shortfall_g':5,'dose_g':65,'adherence_probability':.75}}}
ablations={}
for key,extra in variations.items():
    r=evaluate_h3(p,**base_args,**extra)
    ablations[key]={'status':r['status'],'baseline_ic_demo_percent':r.get('baseline_ic_demo_percent'),
                    'with_policy_ic_demo_percent':r.get('policy_ic_demo_percent'),
                    'energy_W':r.get('energy_W'), 'geometry':r.get('geometry'),
                    'scientific_ic_percent':None}
root=ROOT/'step14'
(root/'H3_100_RESULTS.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in results),encoding='utf8')
(root/'H3_ABLATIONS.json').write_text(json.dumps(ablations,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
# Keep the 26 formerly pending cases: four new assumed numeric paths and 22 still open.
pending=json.loads((ROOT/'step13/H1_26_PENDING_MECHANISMS.json').read_text())
new={'006','025','039','069'}
for q in pending['cases']:
    q['H3_state']='EXECUTABLE_HYPOTHETICAL_QUANT_PATH__NOT_VALIDATED' if q['case'] in new else q['H1_state']
    q['H3_numeric_path_added']=q['case'] in new
ledger={'schema':'riz112/h3/gaps/v1','named_gap_count':26,
        'new_hypothetical_numeric_paths':sorted(new),'remaining_no_new_numeric_path':22,
        'empirically_validated_new_effects':0,'cases':pending['cases']}
(root/'H3_26_CASES_LEDGER.json').write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
stats={'schema':'riz112/h3/population/v1','source_fixture':'H2_100_SCENARIOS_112.jsonl',
 'scenarios':len(results),'numeric_demo_count':n_numeric,'policy_changed_demo_count':n_change,
 'counts_by_status':{status:sum(x['status']==status for x in results) for status in sorted(set(x['status'] for x in results))},
 'new_mechanistic_root_paths':['006','025','039','069'],
 'evidence_level':'MECHANISTIC_DEMO_ASSUMPTIONS_NOT_REAL_RICE_PROBABILITY',
 'real_observations':0,'scientific_ic_percent':None,
 'model_errors':[{'id':r['id'],'error':r['error']} for r in results if r['status']=='MODEL_ERROR']}
(root/'H3_POPULATION_REPORT.json').write_text(json.dumps(stats,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print(json.dumps({'stats':stats,'ablations':ablations},ensure_ascii=False,indent=2))
