#!/usr/bin/env python3
"""RIZ-112: 1000 complete 112-role synthetic rice dossiers, 1000 H3 DEMO ICs.
The 14 post-T0 targets stay unobserved. All ICs are synthetic, NEVER scientific.
The original Step14 H3 and Step20 physics are reused and not modified.
"""
from __future__ import annotations
import argparse,copy,csv,hashlib,json,math,random,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
LAB=(ROOT/'RIZ112_CAHIER_MERE' if (ROOT/'RIZ112_CAHIER_MERE').is_dir()
     else ROOT.parent/'RIZ112_RUN_112'/'RIZ112_CAHIER_MERE')
sys.path.insert(0,str(LAB/'simulations/EXPERIENCE_1000'))
sys.path.insert(0,str(LAB/'step16'))
sys.path.insert(0,str(LAB/'step20'))
from simuler_1000 import latin_hypercube,case_packet,FIELDS
from riz112_unified import verify_packet
from physical_influence_envelope import calculate,validate_semantic_twins
from anticipatory_physics_h3 import evaluate_h3
SEED=20261017
TARGETS=set(f'{i:03d}' for i in range(99,113))
DERIVED={'043','044','046','048'}
ORIGINAL=json.loads((LAB/'step6/examples/A_couvercle_ajuste_112.json').read_text(encoding='utf8'))
ASSUMPTIONS=json.loads((LAB/'step20/ASSUMPTIONS_SYNTHETIQUES_NON_CALIBREES.json').read_text(encoding='utf8'))
LEDGER=json.loads((LAB/'step26/REGISTRE_TRANSVERSAL_112.json').read_text(encoding='utf8'))
IDS=[f'{i:03d}' for i in range(1,113)]
assert len(LEDGER['rows'])==112 and [r['rubric'] for r in LEDGER['rows']]==IDS

# Intervention assumptions are explicit synthetic ranges, not physical truth.
EXTRAS={
 '002':(355.0,600.0),'003':(0.0,3.0),'004':(0.0,8.0),'005':(600.0,1800.0),
 '008':(1350.0,2400.0),'009':(16.0,23.0),'011':(1.3,3.9),
 '025':(5.3,7.2),'028':(0.0,180.0),'029':(0.0,0.22),
 '030':(0.25,0.8),'031':(0.0,0.08),'032':(0.08,0.16),
 '034':(9.0,15.0),'039':(17.0,34.0),'045':(2.5,6.0),
 '007':(0.65,1.0),'018':(0.55,0.95)
}
BOOL_IDS=('013','019','020','021','022','023')
MATERIALS=('copper','iron','metal')
POSSIBLE_ACTIONS=('056','061','062','071','084')
STATUS_DEPENDENT_ACTIONS=('064','070','080')

def sampled_extras(n,seed):
    """Separate LHS for each varied pre-T0 scalar, deterministic permutations."""
    rng=random.Random(seed+211)
    cols={}
    for key,(lo,hi) in EXTRAS.items():
        values=[lo+(hi-lo)*(i+rng.random())/n for i in range(n)]
        rng.shuffle(values); cols[key]=values
    return [{k:cols[k][i] for k in EXTRAS} for i in range(n)]

def update_case(packet,key,value):
    row=packet['case_inputs'][key]
    row.update(value=value,state='ASSUMPTION',source='SYNTHETIC_SCENARIO_DECLARED_NOT_ACTUAL_MEASUREMENT')
    match={'014':'lid_multiplier','030':'surface_starch_index','034':'hot_time_needed_min','039':None,
           '045':'evap_reference_g_per_min'}
    if key in match and match[key] is not None:
        primitive=packet['prestart']['inputs'][match[key]]
        primitive.update(value=value,source='SYNTHETIC_SCENARIO_DECLARED_NOT_ACTUAL_MEASUREMENT')

def build_packet(i,phys,ext):
    rng=random.Random(SEED*101+i*3433)
    packet=case_packet(ORIGINAL,phys)
    # The previously observed 310 abstentions are water_g > a fixed 350ml stock.
    # Here the synthetic stock is sampled and REQUIRED to exceed the proposed water.
    stock=max(ext['002'],phys['035']+12.0+rng.uniform(0,45))
    extra={**ext,'002':stock}
    for k,v in extra.items():update_case(packet,k,round(v,8))
    # Vary equipment presence and categorical heat path without inventing physical predictions.
    material=MATERIALS[i%len(MATERIALS)]
    update_case(packet,'010',material)
    lid=rng.random()<0.82
    update_case(packet,'013',lid)
    update_case(packet,'014',1.0 if lid else 2.2)
    for k in ('019','020','021','022','023'):
        # Resource gates are mandatory for the baseline chain of planned actions.
        # Keep them available rather than generate an infeasible counterfactual.
        update_case(packet,k,True)
    # Optional action declarations: intent/pre-T0 status, not proof of later execution.
    for action in POSSIBLE_ACTIONS:
        if action in ('061','062'):
            planned=extra['003' if action=='061' else '004']>1.0
        else:planned=rng.random()<0.7
        packet['action_plans'][action]['status']='PLANNED' if planned else 'NOT_PLANNED'
        packet['action_plans'][action]['source']='SYNTHETIC_OPTIONAL_ACTION_STATUS'
    if not lid:
        for action in STATUS_DEPENDENT_ACTIONS:
            packet['action_plans'][action]['status']='NOT_PLANNED'
            packet['action_plans'][action]['source']='SYNTHETIC_NO_LID_RESOURCE_CONSTRAINT'
    packet['prestart']['preparation_id']=f'SYN112_{i:04d}'
    # Baseline asserts strict pre-T0, exactly 108 explicit + 4 derived roles.
    assert verify_packet(packet)['logical_total_rubrics']==112
    validate_semantic_twins(packet)
    # Material and geometry options match explicit scenario fields.
    h3_opts={'material':material,'diameter_cm':extra['009'],'wall_mm':extra['011'],
             'lid_present':lid,'source_uptime':extra['007'],'regulation_duty':.75+.25*rng.random(),
             'ambient_C':extra['039'],'grain_length_mm':extra['025'],
             'diffusion_ratio':rng.uniform(.9,1.1),'draws':200,'seed':SEED}
    return packet,h3_opts

def rubric_value(packet,key,physical):
    if key in DERIVED:
        if key=='048':return round(physical['planned_total_water_g']-physical['water_for_absorption_target_g'],6)
        return 'PREVISION_NON_ESTIMEE'
    if key in TARGETS:return 'SORTIE_POST_T0_NON_OBSERVEE'
    for group in ('case_inputs','action_plans','correction_policies'):
        if key in packet[group]:
            x=packet[group][key]
            if group=='case_inputs':return x['value'] if x['value'] is not None else 'INCONNU_PRE_T0'
            if group=='action_plans':return x['status']
            return x['status'] + (':'+x['trigger'] if x.get('trigger') else '')
    raise ValueError('Unmapped role '+key)

def run(n=1000,draws=200):
    if not 1<=n<=1000:raise ValueError('Only 1..1000 scenarios supported')
    if not 100<=draws<=2000:raise ValueError('100..2000 simulation draws')
    physicals=latin_hypercube(n,SEED+11)
    extras=sampled_extras(n,SEED+11)
    out=[];audit=[];failed=[]
    for i,(physical,ext) in enumerate(zip(physicals,extras),1):
        packet,options=build_packet(i,physical,ext);options['draws']=draws
        phys=calculate(packet,ASSUMPTIONS)['physical_account']
        h=evaluate_h3(packet,**options)
        score=h.get('baseline_ic_demo_percent',h.get('ic_demo_percent'))
        if score is None or not isinstance(score,(int,float)) or not math.isfinite(score):
            failed.append({'id':i,'status':h['status'],'reason':h.get('reason')})
        row={'scenario_id':f'SYN112_{i:04d}','IC_DEMO_pct':score,
             'H3_status':h['status'],'scientific_IC_pct':None,
             'energy_feasible_idealized':phys['energy_target_feasible_in_idealized_budget'],
             'water_feasible_before_losses':phys['water_target_mass_feasible_before_losses'],
             'water_stock_synthetic_ml':packet['case_inputs']['002']['value'],
             'water_added_g':packet['case_inputs']['035']['value'],
             'material_assumed':options['material'],
             'source_uptime_assumed':round(options['source_uptime'],6),
             'regulation_duty_assumed':round(options['regulation_duty'],6),
             'rubric_count':112}
        row.update({f'R{k}':rubric_value(packet,k,phys) for k in IDS})
        assert len([x for x in row if x.startswith('R') and len(x)==4])==112
        out.append(row)
        audit.append({'scenario_id':row['scenario_id'],'source_class':'SYNTHETIC_REHEARSAL_NOT_REAL_OBSERVATION',
            'h3_opts':options,'energy_margin_J':phys['energy_margin_for_target_J'],
            'water_margin_before_losses_g':round(phys['planned_total_water_g']-phys['water_for_absorption_target_g'],6),
            'source_status':'SYNTHETIC','user_quality_formula_approved':False,'scientific_IC_pct':None})
    return out,audit,failed

def save(rows,audit,failed,dest):
    dest.mkdir(parents=True,exist_ok=True)
    csvfile=dest/'RIZ112_1000_SCENARIOS_112_RUBRIQUES_IC_DEMO.csv'
    with csvfile.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (dest/'AUDIT_1000_SCENARIOS.jsonl').write_text(''.join(json.dumps(a,ensure_ascii=False,allow_nan=False)+'\n' for a in audit),encoding='utf8')
    columns=[{'id':x['rubric'],'name':x['canonical_name'],'category':x['evidence_category'],
               'varying_in_1000':len({str(row[f'R{x["rubric"]}']) for row in rows})>1,
               'used_in_H3_proxy_directly':x['rubric'] in ('001','007','009','010','011','013','014','025','030','033','034','035','036','037','038','039','041','042','045','047'),
               'post_T0_output_never_a_predictor':x['rubric'] in TARGETS} for x in LEDGER['rows']]
    catalog={'schema':'riz112/simulated112/columns/v1','source':'step26 evidence ledger','columns':columns,'note':'112 roles != 112 independent continuously valued causal variables; 14 output columns deliberately unmeasured'}
    (dest/'DICTIONNAIRE_112_VARIABLES.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    score=[r for r in rows if r['IC_DEMO_pct'] is not None]
    report={'schema':'riz112/simulated112/1000/v1','requested_scenarios':len(rows),'rows_with_112_roles':len(rows),
        'scored_IC_DEMO':len(score),'abstentions':len(failed),'failed_examples':failed[:5],
        'score_threshold_percent':85,'scores_ge_85':sum(r['IC_DEMO_pct']>=85 for r in score),
        'max_IC_DEMO_pct':max((r['IC_DEMO_pct'] for r in score),default=None),
        'median_IC_DEMO_pct':sorted((r['IC_DEMO_pct'] for r in score))[len(score)//2] if score else None,
        'nominal_model':'ORIGINAL_H3_QSTAR_DEMO_200_DRAWS_AND_STEP20_THEORETICAL_ENERGY_WATER',
        'roles_present':112,'roles_varying_in_matrix':sum(x['varying_in_1000'] for x in columns),
        'roles_constant_in_matrix':sum(not x['varying_in_1000'] for x in columns),
        'post_T0_outputs_included_as_empty_labels':14,
        'real_trials':0,'user_approved_real_Q_formula':False,'scientific_IC_pct':None,
        'source_class':'SYNTHETIC_REHEARSAL_NOT_REAL_OBSERVATION',
        'sampling':'LHS 9 physical primitives; correlated prestart stock >= planned water; other synthetic assumptions, equipment, optional action plans. It does NOT infer causal effects for all 112 roles.',
        'critical_limit':'1000 H3 DEMO scores are NOT 1000 scientifically calibrated cooking probabilities, actions are plans not actual executions, postT0 labels are unobserved.'}
    report['csv_sha256']=hashlib.sha256(csvfile.read_bytes()).hexdigest()
    (dest/'RAPPORT_1000_IC_112.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    return report
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--n',type=int,default=1000);parser.add_argument('--draws',type=int,default=200);parser.add_argument('--dest',type=Path,default=ROOT);a=parser.parse_args()
    r,au,f=run(a.n,a.draws);report=save(r,au,f,a.dest);print(json.dumps(report,ensure_ascii=False))
