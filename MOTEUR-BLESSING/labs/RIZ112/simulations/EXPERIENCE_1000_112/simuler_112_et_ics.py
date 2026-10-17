#!/usr/bin/env python3
"""RIZ112: 1000 x 112 rubric dossiers, exploratory IC for every row.

Controlled SYNTHETIC experiment; an IC_SIM_PROXY cannot be treated as calibrated
P(real Q>=85). 14 post-start labels remain NOT_OBSERVED. Historical H3 abstains
are preserved next to exploratory numeric proxy results; no artificial zero fill.
"""
import csv, json, random, math, hashlib, argparse, sys, copy, collections, statistics
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'simulations'/'EXPERIENCE_1000'))
from simuler_1000 import case_packet, FIELDS
sys.path.insert(0,str(ROOT/'step9'))
from ic_simulation_v1 import (physical_analyze, vals_from_core, proxy_scores, sample_packet, CONTRACT)

SEED = 20261017
RUBRICS=[f'{i:03d}' for i in range(1,113)]
NUMERIC_SPEC={
 '002':(180,650),'003':(0,8),'004':(0,18),'005':(300,1600),'007':(.65,1),'008':(850,2600),
 '009':(14,26),'011':(1.2,5),'014':(.65,1.20),'018':(.45,.99),'025':(4.5,9),
 '028':(30,540),'029':(0,.20),'030':(.18,.92),'031':(0,.04),'032':(.08,.20),
 '034':(8,21),'039':(15,34),'040':(0,1800),'045':(1.5,8.5),
}
CATEGORICAL_SPEC={
 '006':['electricity','gas','charcoal'],
 '010':['aluminium','steel','copper'],
 '012':['clean_flat','slightly_warped','worn'],
 '015':['narrow_vent','vented','unvented'],
 '016':['electric_hotplate','gas_burner','charcoal_stove'],
 '024':['long_white_hypothesis','medium_white_hypothesis','short_white_hypothesis'],
 '026':['unprocessed','parboiled','polished'],
 '027':['lot_A_synthetic','lot_B_synthetic','lot_C_synthetic']}
BOOLEAN_SPEC={'013','017','019','020','021','022','023'}
COUPLES={k:v[0] for k,v in FIELDS.items()}
BRIDGE={'014':'lid_multiplier','030':'surface_starch_index','034':'hot_time_needed_min','045':'evap_reference_g_per_min'}
PRET0_CASES=[f'{i:03d}' for i in range(1,49) if i not in (43,44,46,48)]
ACTION_IDS=[f'{i:03d}' for i in range(49,86)]
POLICY_IDS=[f'{i:03d}' for i in range(86,99)]
TARGET_IDS=[f'{i:03d}' for i in range(99,113)]
DERIVED_IDS=['043','044','046','048']


def rounded(value):return round(value,7) if isinstance(value,float) else value


def make_roles(original, historic_row, ledger, index):
    rng=random.Random(SEED*10_000+index)
    values={}; states={}
    # First 9 cells: EXACT original 1000 Latin hypercube inputs; no altered baseline.
    for k,f in COUPLES.items(): values[k]=float(historic_row[f]);states[k]='H3_CASE_INPUT_SYNTHETIC'
    for ident in PRET0_CASES:
        if ident in values:continue
        src=original['case_inputs'][ident]
        if ident=='002': # stock is one coherent resource rather than an additional dose
            v=float(values['035'])*rng.uniform(.78,1.65)
        elif ident=='005':v=rng.uniform(300,1600)
        elif ident=='008':
            content=values['001']*rng.uniform(.9,1.5)+values['035']+values['036']
            v=max(850,min(2600,content*rng.uniform(1.12,2.8)))
        elif ident in NUMERIC_SPEC:v=rng.uniform(*NUMERIC_SPEC[ident])
        elif ident in CATEGORICAL_SPEC:v=CATEGORICAL_SPEC[ident][(index+rng.randrange(3))%3]
        elif ident in BOOLEAN_SPEC:v=rng.random()<(.83 if ident in ('019','020','023') else .65)
        else:raise ValueError('Unspecified pre-T0 case '+ident)
        values[ident]=rounded(v);states[ident]='SYNTHETIC_PRE_T0_ASSUMPTION'
    # Keep setup consistent: an absent lid cannot be well adjusted.
    if values['013'] is False:values['014']=0.65
    values['016']={'electricity':'electric_hotplate','gas':'gas_burner','charcoal':'charcoal_stove'}[values['006']]
    values['017']=bool(values['017']);values['018']=rounded(values['018'])
    # Plans are predeclared only. A plan's status is not evidence it was executed.
    for ident in ACTION_IDS:
        status='PLANNED' if rng.random()<(.82 if ident in ('049','050','053','059','060','065','068','073','074','075','076','080','081','082') else .63) else 'NOT_PLANNED'
        if ident in ('055','056','057','058') and values.get('054')=='NOT_PLANNED':status='NOT_PLANNED'
        if ident=='061' and values['003']<.2:status='NOT_PLANNED'
        if ident=='062' and values['004']<.2:status='NOT_PLANNED'
        if ident=='064' and not values['013']:status='NOT_PLANNED'
        values[ident]=status;states[ident]='SYNTHETIC_PRE_T0_PLAN'
    # Explicit correction contingency DECLARED or UNDEFINED, never observed trigger.
    for ident in POLICY_IDS:
        values[ident]='DEFINED' if rng.random()<.58 else 'UNDEFINED';states[ident]='PREDECLARED_CONDITIONAL_POLICY'
    # Derivatives are calculated below once, not independently sampled.
    for ident in DERIVED_IDS:states[ident]='THEORETICAL_DERIVED_FROM_PRET0'
    # Targets cannot be used before T0. They remain explicitly unobserved.
    for ident in TARGET_IDS:
        values[ident]='NOT_OBSERVED_POST_T0';states[ident]='OUTCOME_LABEL_UNOBSERVED'
    return values,states


def model_packet(base,values):
    packet=case_packet(base,{k:float(values[k]) for k in COUPLES})
    for ident in PRET0_CASES:
        if ident in COUPLES:continue
        row=packet['case_inputs'][ident]
        row['value']=values[ident]
        row['source']='SYNTHETIC_DESIGN_NOT_REAL_MEASUREMENT'
        row['state']='ASSUMPTION'
        if ident in BRIDGE:
            p=packet['prestart']['inputs'][BRIDGE[ident]]
            p['value']=values[ident];p['source']='SYNTHETIC_PRET0_BRIDGE_'+ident
    packet['prestart']['inputs']['rinse_removal_fraction']['value']=round(random.Random(SEED+int(values['001']*100)).uniform(.25,.65),8) if values['054']=='PLANNED' else 0.0
    packet['prestart']['inputs']['rinse_removal_fraction']['source']='SYNTHETIC_RINSE_PLAN_ASSUMPTION'
    packet['prestart']['inputs']['lid_multiplier']['value']=values['014'] if values['013'] else .65
    packet['prestart']['inputs']['lid_multiplier']['source']='SYNTHETIC_LID_COUPLING'
    for ident in ACTION_IDS:
        row=packet['action_plans'][ident]
        row['status']=values[ident];row['source']='SYNTHETIC_PRESTART_PLAN_NOT_EXECUTED'
    for ident in POLICY_IDS:
        row=packet['correction_policies'][ident]
        if values[ident]=='UNDEFINED':
            row['status']='UNDEFINED';row['trigger']=None;row['planned_response']=None
        else:
            row['status']='DEFINED'
            row['trigger']=row.get('trigger') or ('hypothetical_'+ident+'_condition')
            row['planned_response']=row.get('planned_response') or ('reassess_plan_for_'+ident)
        row['source']='SYNTHETIC_CONDITIONAL_POLICY_NOT_TRIGGERED'
    return packet


def exploratory_ic(packet,draws,seed,contract):
    # Same ORIGINAL Step9 four-dimensional Q* formula, but by deliberate
    # counterfactual override of the H3 gate for analysis. This is NOT an H3 IC.
    rng=random.Random(seed);n=0;qs=[];last=None
    for _ in range(draws):
        item=sample_packet(packet['prestart'],rng,contract['uncertainty_distribution'])
        nodes=vals_from_core(physical_analyze(item))
        _,q=proxy_scores(nodes,item,contract['proxy_scales'])
        qs.append(q);n+=q>=85
        last=nodes
    return round(100*n/draws,2),last


def create(n=1000,draws=200):
    old=list(csv.DictReader((ROOT/'simulations/EXPERIENCE_1000/results/SCENARIOS_1000_SYNTHETIQUES.csv').open(encoding='utf8',newline='')))
    assert len(old)==1000 and n==1000
    base=json.loads((ROOT/'step6/examples/A_couvercle_ajuste_112.json').read_text(encoding='utf8'))
    ledger=json.loads((ROOT/'step26/REGISTRE_TRANSVERSAL_112.json').read_text(encoding='utf8'))
    contract=json.loads(CONTRACT.read_text(encoding='utf8'))
    rows=[];packet_hashes=[]
    for i,history in enumerate(old,1):
        vals,states=make_roles(base,history,ledger,i)
        packet=model_packet(base,vals)
        ic,_=exploratory_ic(packet,draws,SEED,contract)
        # Derived pre-T0 forecasts use the nominal packet, not the last random draw.
        nodes=vals_from_core(physical_analyze(packet['prestart']))
        # Extract explicit pre-T0 *forecasts*, not post-T0 measurements.
        vals['043']=rounded(nodes['T_boiling'])
        vals['044']=rounded(nodes['F_hot'])
        vals['046']=rounded(nodes['E_evap'])
        vals['048']=rounded(nodes['W_after']-nodes['W_target'])
        assert set(vals)==set(RUBRICS)
        for k in RUBRICS:
            assert vals[k] is not None
        h3=float(history['ic_demo_percent']) if history['ic_demo_percent'] else None
        packet_h=hashlib.sha256(json.dumps(vals,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf8')).hexdigest()
        packet_hashes.append(packet_h)
        entry={'scenario_id':history['scenario_id'],**{f'R{k}':vals[k] for k in RUBRICS},
               'IC_EXPLORATOIRE_PROXY_PCT':ic,
               'IC_H3_ORIGINAL_PCT':h3,
               'H3_ETAT':history['h3_status'],
               'IC_SCIENTIFIQUE_REEL_PCT':None,
               'IC_NOUVEAU_TYPE':'Q_STAR_PHYSIQUE_SANS_PORTE_H3',
               'IC_ANCIEN_TYPE':'H3_QSTAR_ORIGINAL' if h3 is not None else 'H3_ABSTENTION',
               'STATUT_CIBLE_REELLE':'AUCUN_Q_REEL_OBSERVE',
               'SHA256_DOSSIER_112':packet_h}
        rows.append(entry)
        if i%200==0:print('SIMULATION_REPRODUCED',i,flush=True)
    return rows,ledger,contract


def write(rows,ledger,contract,out):
    out.mkdir(parents=True,exist_ok=True)
    p=out/'RIZ112_1000_SCENARIOS_112_RUBRIQUES_1000_IC.csv'
    with p.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=';')
        w.writeheader();w.writerows(rows)
    records={}
    for x in ledger['rows']:
        k=x['rubric'];values={str(r['R'+k]) for r in rows}
        records[k]={'name':x['canonical_name'],'role_group':x['role_group'],'proof':x['evidence_category'],
                    'distinct_values':len(values),'examples':sorted(values)[:6],
                    'role_is_preT0_or_forecast':x['role_group']!='target_contract',
                    'enters_IC_proxy_directly':k in list(COUPLES)+list(BRIDGE)+['054'],
                    'confirmed_effect_on_real_Q':False}
    allvals=[r['IC_EXPLORATOIRE_PROXY_PCT'] for r in rows];orig=[r['IC_H3_ORIGINAL_PCT'] for r in rows if r['IC_H3_ORIGINAL_PCT'] is not None]
    report={'schema':'riz112/synthetic1000x112/contract/v1','simulation':True,'seed':SEED,'draws_per_scenario':200,'rows':len(rows),
     'columns_112':['R'+k for k in RUBRICS],'distinct_preT0_or_derived_columns':sum(records[k]['distinct_values']>1 for k in RUBRICS[:98]),
     'outcome_columns_unobserved':14,'rubric_state_audit':records,
     'IC_exploratoire':{'all_1000_have_numeric_score':all(type(x) in (int,float) for x in allvals),'min':min(allvals),'max':max(allvals),'median':statistics.median(allvals),'count_ge_85':sum(x>=85 for x in allvals), 'count_gt_0':sum(x>0 for x in allvals)},
     'H3_original':{'evaluated':len(orig),'abstained':1000-len(orig),'max':max(orig),'count_ge_85':sum(x>=85 for x in orig)},
     'provenance':{'baseline_csv':'simulations/EXPERIENCE_1000/results/SCENARIOS_1000_SYNTHETIQUES.csv','old_H3_engine':'step14/anticipatory_physics_h3.py','new_proxy':'step9/ic_simulation_v1.py original proxy_scores+sample_packet+reference step4 physical_analyze','original_seed':SEED},
     'disclaimer':'IC_EXPLORATOIRE_PROXY_PCT is an assumed Q* threshold crossing Monte Carlo percentage, not actual success probability. For 310 H3 abstained the original H3 remains null. No 112 independent causal effects. 14 targets not observed. Some pre-T0 options only descriptive and have zero declared direct effect in Q*.'}
    report['csv_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
    p2=out/'RAPPORT_1000x112.json';p2.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    return report,p

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--draws',type=int,default=200);args=ap.parse_args()
    if args.draws!=200:raise ValueError('Locked MC draws=200 for audit')
    rows,ledger,contract=create(draws=args.draws)
    r,p=write(rows,ledger,contract,args.out)
    print(json.dumps({'count':len(rows),'distinct_preT0_forecasts':r['distinct_preT0_or_derived_columns'],'IC':r['IC_exploratoire'],'H3':r['H3_original'],'sha256':r['csv_sha256']},ensure_ascii=False))
