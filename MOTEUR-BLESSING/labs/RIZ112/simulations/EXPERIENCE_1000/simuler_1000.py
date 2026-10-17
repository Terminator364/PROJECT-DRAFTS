#!/usr/bin/env python3
"""Reproducible 1000-scenario synthetic experiment using ORIGINAL H3 + Step20 physics.
The Q* threshold 85 is a modeling assumption; IC_DEMO is not a real calibrated probability.
No post-T0 features; no fabricated real rice trials; no self-certification of causal truth.
"""
from __future__ import annotations
import argparse,copy,csv,hashlib,json,math,random,statistics,sys
from pathlib import Path
LAB=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(LAB/'step20'))
sys.path.insert(0,str(LAB/'step14'))
from physical_influence_envelope import calculate, validate_semantic_twins, FIELDS
from anticipatory_physics_h3 import evaluate_h3

SEED=20261017
DRAW_SEED=20261017
RANGES={
 '001':(120.0,240.0),'033':(1.0,1.9),'035':(160.0,435.0),
 '036':(0.0,24.0),'037':(12.0,40.0),'038':(12.0,38.0),
 '041':(280.0,900.0),'042':(0.35,0.82),'047':(12.0,38.0)}
KEYS=list(RANGES)
METRICS=['energy_margin_for_target_J','water_for_absorption_target_g','max_water_before_unmodeled_loss_g','thermal_ceiling_on_evaporation_g']


def latin_hypercube(n:int,seed:int=SEED)->list[dict]:
    if not 1<=n<=10000:raise ValueError('1 to 10000 scenarios')
    rng=random.Random(seed)
    columns={}
    for k,(lo,hi) in RANGES.items():
        v=[lo+(hi-lo)*(i+rng.random())/n for i in range(n)]
        rng.shuffle(v)
        columns[k]=v
    return [{k:columns[k][i] for k in KEYS} for i in range(n)]


def case_packet(original,values):
    packet=copy.deepcopy(original)
    for ident,v in values.items():
        f,u=FIELDS[ident]
        row=packet['case_inputs'][ident]
        primitive=packet['prestart']['inputs'][f]
        row['value']=round(v,10)
        primitive['value']=round(v,10)
        # Retain H3's required *within-simulation* roles (e.g. rice mass OBSERVED).
        # Synthetic provenance and the source_class label prohibit treating these as real field observations.
        row['source']='SIMULATED_LATIN_HYPERCUBE_NOT_A_REAL_MEASUREMENT'
        primitive['source']='SIMULATED_LATIN_HYPERCUBE_NOT_A_REAL_MEASUREMENT'
    validate_semantic_twins(packet)
    return packet


def summarise(rows: list[dict])->dict:
    accepted=[x for x in rows if x['h3_status']=='DEMO_ASSUMED_MECHANISMS_NOT_REAL_Q']
    high=[x for x in accepted if x['ic_demo_percent']>=85]
    physically_possible=[x for x in rows if x['idealized_energy_feasible'] and x['preloss_water_feasible']]
    both=[x for x in high if x['idealized_energy_feasible'] and x['preloss_water_feasible']]
    def record(g):
        return {'scenarios':len(g),'rate_percent_of_1000':round(100*len(g)/len(rows),2)}
    deciles=[]
    if accepted:
        for k in range(0,10):
            x=[r for r in accepted if k*10<=r['ic_demo_percent']<(k+1)*10] if k<9 else [r for r in accepted if r['ic_demo_percent']>=90]
            deciles.append({'ic_demo_percent_band':f'{10*k}–{min(100,10*(k+1))}', 'count':len(x)})
    best=sorted(accepted,key=lambda x:(-x['ic_demo_percent'],x['scenario_id']))[:5]
    return {'schema':'riz112/synthetic1000/report/v1','seed':SEED,'h3_common_random_seed':DRAW_SEED,
      'count':len(rows),'design':'9D Latin hypercube, independent random permutations, all 9 semantic twins in sync',
      'simulation_only':True,'source_class':'SYNTHETIC_REHEARSAL_NOT_REAL_OBSERVATION','quality_threshold_of_H3_proxy_Q_star':85,
      'high_ic_demo_threshold_percent':85,
      'actual_Q_observations':0,'scientific_ic_percent':None,'user_Q_formula_approved':False,
      'counts':{'h3_model_computed':record(accepted), 'h3_demo_IC_at_least_85_percent':record(high),
        'idealized_energy_water_both_feasible':record(physically_possible),
        'high_demo_IC_and_idealized_physical_feasibility':record(both),
        'h3_abstentions_or_errors':record([r for r in rows if r not in accepted])},
      'ic_demo_distribution':deciles,
      'ic_demo_percent_min':min((r['ic_demo_percent'] for r in accepted),default=None),
      'ic_demo_percent_median':statistics.median([r['ic_demo_percent'] for r in accepted]) if accepted else None,
      'ic_demo_percent_max':max((r['ic_demo_percent'] for r in accepted),default=None),
      'examples_highest_ic_demo':best,
      'limitations':['The ranges are proposed synthetic uncertainty design, not identified empirical ranges.',
        'H3 Q* is a previously-defined surrogate; >=85 Q* is NOT >=85 real rice Q.',
        'H3 draws sampled per scenario are neither real trials nor independent rice outcomes.',
        'Idealized thermodynamic budgets are not proof of acceptable rice or safe food.',
        'LHS identifies parameter combinations and structural responsiveness, NOT causal Q influences nor calibrated probabilities.',
        'Remaining 103 rubric roles (including targets) retain the original packet values/status; only 9 physical twins vary.',
        'Any numerical success region is model-relative and must not be stated as empirical advice.']}


def simulate(n=1000,draws=200,seed=SEED):
    if type(draws)!=int or not 100<=draws<=20000:raise ValueError('draws >=100')
    base=json.loads((LAB/'step6/examples/A_couvercle_ajuste_112.json').read_text(encoding='utf8'))
    assumptions=json.loads((LAB/'step20/ASSUMPTIONS_SYNTHETIQUES_NON_CALIBREES.json').read_text(encoding='utf8'))
    vals=latin_hypercube(n,seed)
    rows=[]
    for i,param in enumerate(vals,1):
        packet=case_packet(base,param)
        p=calculate(packet,assumptions)['physical_account']
        h=evaluate_h3(packet,draws=draws,seed=DRAW_SEED)
        ic=h.get('baseline_ic_demo_percent',h.get('ic_demo_percent'))
        r={'scenario_id':f'SYN_{i:04d}',**{FIELDS[k][0]:round(v,8) for k,v in param.items()},
           'h3_status':h['status'],'ic_demo_percent':ic,'scientific_ic_percent':None,
           'idealized_energy_feasible':p['energy_target_feasible_in_idealized_budget'],
           'preloss_water_feasible':p['water_target_mass_feasible_before_losses'],
           'energy_margin_J':p['energy_margin_for_target_J'],
           'water_margin_before_losses_g':round(p['planned_total_water_g']-p['water_for_absorption_target_g'],8),
           'thermal_ceiling_evap_g_NOT_PREDICTION':p['thermal_ceiling_on_evaporation_g']}
        rows.append(r)
    return rows,summarise(rows)


def targeted_counterfactuals(rows,draws=200):
    """Post-hoc teaching contrasts, NOT out-of-sample or true causal Q evidence."""
    computed=[r for r in rows if r['h3_status']=='DEMO_ASSUMED_MECHANISMS_NOT_REAL_Q']
    anchor=sorted(computed,key=lambda x:(-x['ic_demo_percent'],x['scenario_id']))[0]
    base=json.loads((LAB/'step6/examples/A_couvercle_ajuste_112.json').read_text(encoding='utf8'))
    assumptions=json.loads((LAB/'step20/ASSUMPTIONS_SYNTHETIQUES_NON_CALIBREES.json').read_text(encoding='utf8'))
    anchor_params={k:anchor[FIELDS[k][0]] for k in KEYS}
    anchor_packet=case_packet(base,anchor_params)
    anchor_phys=calculate(anchor_packet,assumptions)['physical_account']
    results=[]
    for key in KEYS:
        original=anchor_params[key]
        for fraction in (-0.15,0.15):
            low,high=RANGES[key]
            # Keep all counterfactuals inside the declaration envelope.
            v=max(low+1e-6,min(high-1e-6,original*(1+fraction)))
            changed=case_packet(base,{**anchor_params,key:v})
            physics=calculate(changed,assumptions)['physical_account']
            h=evaluate_h3(changed,draws=draws,seed=DRAW_SEED)
            ic=h.get('baseline_ic_demo_percent',h.get('ic_demo_percent'))
            results.append({'anchor_id':anchor['scenario_id'],'case':key,'field':FIELDS[key][0],
                'requested_relative_change':fraction,'actual_before':original,'actual_after':v,
                'h3_status':h['status'],'anchor_IC_DEMO_percent':anchor['ic_demo_percent'],
                'counterfactual_IC_DEMO_percent':ic,
                'delta_IC_DEMO_percentage_points':round(ic-anchor['ic_demo_percent'],3) if ic is not None else None,
                'delta_energy_margin_J':round(physics['energy_margin_for_target_J']-anchor_phys['energy_margin_for_target_J'],6),
                'delta_water_margin_g':round((physics['planned_total_water_g']-physics['water_for_absorption_target_g']) - anchor['water_margin_before_losses_g'],6),
                'scientific_IC_delta_percent':None,'real_Q_effect_proven':False})
    return {'schema':'riz112/synthetic1000/posthoc-counterfactuals/v1','selected_anchor_after_simulation':True,
        'selection_bias_notice':'The anchor was selected for highest synthetic IC; do not interpret as out-of-sample or universal optimum.',
        'common_random_draws':draws,'anchor':anchor,'number_of_contrasts':len(results),'contrasts':results,
        'scientific_ic_percent':None,'validated_empirical_effects':0}

def persist(rows,report,outdir):
    outdir.mkdir(parents=True,exist_ok=True)
    csv_file=outdir/'SCENARIOS_1000_SYNTHETIQUES.csv';tmp=csv_file.with_suffix('.tmp')
    with tmp.open('w',encoding='utf8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    tmp.replace(csv_file)
    sha=hashlib.sha256(csv_file.read_bytes()).hexdigest()
    report['csv_sha256']=sha
    report['csv_rows']=len(rows)
    (outdir/'RAPPORT_1000.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
    return sha

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--n',type=int,default=1000);parser.add_argument('--draws',type=int,default=200);parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args();rows,report=simulate(a.n,a.draws);persist(rows,report,a.output)
    cf=targeted_counterfactuals(rows,a.draws)
    (a.output/'CONTREFACTUELS_18.json').write_text(json.dumps(cf,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps({'n':len(rows),'counts':report['counts'],'demo_median':report['ic_demo_percent_median'],'csv_sha256':report['csv_sha256'],'science_ic':None},ensure_ascii=False))
