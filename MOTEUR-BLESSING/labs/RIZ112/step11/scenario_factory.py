"""RIZ-112 Scenario Factory, demonstrator: 112 case roles, independent synthetic scenarios.

DO NOT use as a model of real rice quality or sporting probabilities.
A material without a documented heat model triggers a visible abstention.
"""
from __future__ import annotations
import copy, json, random, sys, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step10'))
from ic_integrity_v10 import audited_simulate
sys.path.insert(0,str(ROOT/'step6'))
from engine112 import PRESTART, FORECAST, ACTIONS, POLICIES, OUTCOMES, DRIVER, analyze112

SOURCE=ROOT/'step6/examples/A_couvercle_ajuste_112.json'
UNSUPPORTED={'wood_unrated'}

def _set(p,case,value):
    row=p['case_inputs'][case]
    row.update(state='ASSUMPTION',value=value,source='GENERATED_SYNTHETIC_NOT_MEASURED')
    if case in DRIVER:
        raw=p['prestart']['inputs'][DRIVER[case]]
        raw['value']=value;raw['source']='GENERATED_SYNTHETIC_NOT_MEASURED'

def _make(seed:int, index:int, overrides:dict|None=None):
    if type(seed)!=int or seed<0 or type(index)!=int or index<0: raise ValueError('seed/index')
    rng=random.Random(seed+index*1000003)
    p=json.loads(SOURCE.read_text(encoding='utf8'))
    p['prestart']['preparation_id']=f'SYNTH_{seed}_{index:03}'
    # No material-to-efficiency mapping is invented. Material remains a declared context.
    vessel=rng.choice(['metal','ceramic_rated','wood_unrated'])
    lid=rng.choice([True,False]); mass=rng.choice([90,130,160,220,290]);water=rng.choice([110,160,230,300,380,500]);power=rng.choice([280,400,550,700,950]);
    heating=rng.choice([12,16,22,28,34]);stock=rng.choice([180,350,700,1200]);potcap=rng.choice([550,1000,1700,2300]);
    if overrides:
        allowed={'vessel','lid','mass_g','water_g','power_w','heating_min','stock_g','pot_capacity_ml'}
        if set(overrides)-allowed:raise ValueError('unknown override')
        vessel=overrides.get('vessel',vessel);lid=overrides.get('lid',lid);mass=overrides.get('mass_g',mass);
        water=overrides.get('water_g',water);power=overrides.get('power_w',power);
        heating=overrides.get('heating_min',heating);stock=overrides.get('stock_g',stock);potcap=overrides.get('pot_capacity_ml',potcap)
    if vessel not in {'metal','ceramic_rated','wood_unrated'} or type(lid)!=bool:raise ValueError('material or lid')
    for name,value in [('mass_g',mass),('water_g',water),('power_w',power),('heating_min',heating),('stock_g',stock),('pot_capacity_ml',potcap)]:
        if type(value) not in (int,float) or value<0:raise ValueError('invalid '+name)
    if mass<=0 or power<=0 or heating<=0:raise ValueError('positive physical driver')
    vals={ '001':mass,'002':stock,'008':potcap,'010':vessel,'013':lid,
           '014':1.0 if lid else 2.2,'035':water,'041':power,'047':heating,
           '007':round(rng.uniform(.6,1),3),'009':rng.choice([15.,18.,22.,26.]),
           '011':rng.choice([1.,2.,3.,4.]),'016':rng.choice(['gas_stove','electric_stove']),
           '017':rng.choice([True,False]), '030':round(rng.uniform(.2,.8),3),
           '032':round(rng.uniform(.08,.15),3),'033':round(rng.uniform(1.2,1.5),3),
           '034':rng.choice([10.,12.,15.]),'036':rng.choice([0.,4.,8.,15.]),
           '037':rng.choice([18.,22.,26.,32.]),'038':rng.choice([18.,22.,27.]),
           '042':round(rng.uniform(.45,.75),3),'045':rng.choice([2.5,4.,5.5]),
           '024':rng.choice(['long_white_hypothesis','parboiled_hypothesis'])}
    for k,v in vals.items():_set(p,k,v)
    p['case_inputs']['006'].update(state='ASSUMPTION',value='available_power',source='GENERATED_SYNTHETIC_NOT_MEASURED')
    for case in ACTIONS:
        r=p['action_plans'][case]
        # Scenario plans vary, without claiming actual cooking steps were performed.
        if rng.random()<.16:r['status']='NOT_PLANNED'
        r['source']='GENERATED_SYNTHETIC_PLAN_NOT_EXECUTED'
    if not lid:
        for k in ['064','070','080']:
            p['action_plans'][k]['status']='NOT_PLANNED'
    for case in POLICIES:
        row=p['correction_policies'][case]
        if rng.random()<.35:row.update(status='UNDEFINED',trigger=None,planned_response=None)
        row['source']='GENERATED_SYNTHETIC_POLICY_NOT_ACTUAL'
    # Immutable quality targets: future events are NEVER sampled into prestart features.
    assert len(p['case_inputs'])==44 and len(p['action_plans'])==37 and len(p['correction_policies'])==13 and len(p['target_contract'])==14
    return p, {'material':vessel,'lid':lid,'rice_g':mass,'water_g':water,'power_W':power,'heat_min':heating,'water_stock_g':stock,'pot_capacity_ml':potcap}

def evaluate(p,scenario,draws=300,seed=20261017):
    assert len(PRESTART)+len(FORECAST)+len(ACTIONS)+len(POLICIES)+len(OUTCOMES)==112
    # Strict unsupported-material block (no invented heat transfer for wood).
    if scenario['material'] in UNSUPPORTED:
        return {'status':'ABSTAIN_UNSUPPORTED_VESSEL','ic_demo_percent':None,'scientific_ic_percent':None,
                'reason':'No valid heat-transfer / direct-heating compatibility model for wooden vessel',
                'cases_in_scenario':112,'poststart_consumed':0}
    core=analyze112(p)
    if core['graph']['contradictions']:
        return {'status':'ABSTAIN_CONTRADICTION','ic_demo_percent':None,'scientific_ic_percent':None,
                'conflicts':core['graph']['contradictions'],'cases_in_scenario':112,'poststart_consumed':0}
    r=audited_simulate(p,draws=draws,seed=seed)
    r['cases_in_scenario']=112
    return r

def run(seed=20261017,count=8,draws=300):
    if type(count)!=int or not 1<=count<=100:raise ValueError('count')
    output=[]
    for i in range(count):
        p,s=_make(seed,i)
        r=evaluate(p,s,draws=draws,seed=seed)
        output.append({'name':p['prestart']['preparation_id'],'scenario':s,'status':r['status'],
                       'ic_demo_percent':r['ic_demo_percent'], 'scientific_ic_percent':r['scientific_ic_percent'],
                       'reason':r.get('reason'), 'conflicts':r.get('conflicts'), 'packet':p})
    return {'schema':'riz112/random-prestart-factory/v1','seed':seed,'count':count,'draws':draws,
            'target_frozen':True,'poststart_input_used':0,'numeric_ic_is_assumption_only':True,'scenario_count':len(output),
            'scenarios':output}

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--seed',type=int,default=20261017);a.add_argument('--count',type=int,default=8);a.add_argument('--draws',type=int,default=300);a.add_argument('--out',type=Path)
    q=a.parse_args();out=json.dumps(run(q.seed,q.count,q.draws),indent=2,ensure_ascii=False)+'\n'
    if q.out:q.out.write_text(out,encoding='utf-8')
    else:print(out)
