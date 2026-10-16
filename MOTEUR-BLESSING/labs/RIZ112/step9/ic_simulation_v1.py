#!/usr/bin/env python3
"""RIZ112 Step9: explicit assumed probability of a FOUR-DIMENSION proxy, never empirical P(Q>=85).

Absolutely NO 112 arbitrary coefficients. Existing physics and 112-case gates reused.
The MC scenario distribution + proxy metric are visible, changeable and UNVALIDATED.
This does not estimate real cooking success probability until real labels and calibration.
"""
from __future__ import annotations
import copy, hashlib, json, math, random, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'reference'/'step4'))
from riz112 import analyze as physical_analyze
sys.path.insert(0,str(ROOT/'step8'))
from functional_routes import analyze8
sys.path.insert(0,str(ROOT/'step6'))
from engine112 import analyze112

CONTRACT=Path(__file__).with_name('DEMONSTRATION_CONTRACT.json')
class SimulationError(ValueError):pass

def clamp(x, a, b):return min(b,max(a,x))

def vals_from_core(out):
    n={r['node']:r['value'] for r in out['graph_trace']}
    if n['W_target']<=0:raise SimulationError('target hydration cannot be zero')
    return n

def proxy_scores(n,packet,thresholds):
    mass=packet['inputs']['rice_mass_g']['value']
    # Four explicit, purely illustrative monotonic scores; no additive points.
    scores={
     'hydration_101':clamp(n['W_absorb']/n['W_target'],0,1),
     'thermal_103_proxy':clamp(n['F_hot'],0,1),
     'free_water_105':clamp(1-n['W_free']/(mass*thresholds['free_water_scale_g_per_g']),0,1),
     'starch_102_UNVALIDATED':clamp(1-n['S_residual']/thresholds['surface_starch_scale'],0,1)
    }
    return scores,100*min(scores.values())

def draw_factors(rng, distribution):
    shared=rng.gauss(0,1)
    factors={}
    for key, cfg in distribution.items():
        if not isinstance(cfg,dict) or set(cfg)!={'relative_sigma','shared_latent_loading'}:
            raise SimulationError('invalid distribution schema for '+key)
        sd,loading=cfg['relative_sigma'],cfg['shared_latent_loading']
        if type(sd) not in (float,int) or not 0<=sd<=1 or type(loading) not in (float,int) or not -1<=loading<=1:
            raise SimulationError('invalid relative sigma/loading')
        z=loading*shared+math.sqrt(1-loading*loading)*rng.gauss(0,1)
        factors[key]=max(.05,1+sd*z)
    return factors

def sample_packet(pre, rng, distribution):
    pkt=copy.deepcopy(pre)
    f=draw_factors(rng,distribution)
    for key,multiplier in f.items():
        row=pkt['inputs'][key]
        value=row['value']*multiplier
        if key in {'transfer_efficiency','rinse_removal_fraction'}:value=clamp(value,0,1)
        if key=='water_retained_g':value=max(0,value)
        row['value']=value
    return pkt

def fingerprint(packet, contract):
    return hashlib.sha256(json.dumps({'packet':packet,'contract':contract},sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()).hexdigest()

def simulate(packet, contract, n_draws=3000, seed=20261016):
    if isinstance(n_draws,bool) or type(n_draws)!=int or not 100<=n_draws<=20000:raise SimulationError('n_draws must be 100..20000')
    if isinstance(seed,bool) or type(seed)!=int or seed<0:raise SimulationError('seed must be nonnegative integer')
    if not isinstance(contract,dict) or contract.get('schema')!='riz112/ic-assumption-demonstrator/v1':raise SimulationError('contract schema')
    thresholds=contract.get('proxy_scales');dist=contract.get('uncertainty_distribution')
    if not isinstance(thresholds,dict) or set(thresholds)!={'free_water_scale_g_per_g','surface_starch_scale'} or not all(type(v) in (float,int) and v>0 for v in thresholds.values()):
        raise SimulationError('proxy scales invalid')
    permitted={'transfer_efficiency','evap_reference_g_per_min','lid_multiplier','water_capacity_g_per_g','hot_time_needed_min','water_retained_g','power_W','rinse_removal_fraction'}
    if not isinstance(dist,dict) or set(dist)!=permitted:raise SimulationError('distribution must declare each of eight uncertain drivers')
    if contract.get('threshold_q_demo')!=85 or contract.get('approved_for_empirical_success') is not False:
        raise SimulationError('explicit unapproved 85 demonstration contract required')
    pre=packet['prestart']
    # Run original exact V8 and 112-case admissibility, never suppress a contradiction.
    stage8=analyze8(packet)
    stage6=analyze112(packet)
    if stage8['hard_conflicts'] or stage6['graph']['contradictions']:
        return {'schema':'riz112/step9/ic-simulation/v1','preparation_id':pre['preparation_id'],
                'status':'ABSTAIN_PRESTART_CONTRADICTION','ic_demo_percent':None,
                'scientific_ic_percent':None,'conflicts':stage8['hard_conflicts']+stage6['graph']['contradictions'],
                'coverage':{'cases_visited':112,'d014_routes_visited':62}}
    baseline=physical_analyze(pre)
    baseline_nodes=vals_from_core(baseline)
    baseline_scores,baseline_Q=proxy_scores(baseline_nodes,pre,thresholds)
    rng=random.Random(seed);successes=0;qs=[]
    sums={k:0 for k in baseline_scores}
    for _ in range(n_draws):
        item=sample_packet(pre,rng,dist)
        result=physical_analyze(item)
        scores,Q=proxy_scores(vals_from_core(result),item,thresholds)
        qs.append(Q)
        successes+=(Q>=contract['threshold_q_demo'])
        for k,v in scores.items():sums[k]+=v
    qs.sort()
    frac=successes/n_draws
    # Wilson interval expresses Monte Carlo sampling variation ONLY (not model error).
    z=1.96;den=1+z*z/n_draws
    centre=(frac+z*z/(2*n_draws))/den
    half=z*math.sqrt(frac*(1-frac)/n_draws+z*z/(4*n_draws*n_draws))/den
    def nearest(p):return round(qs[round(p*(n_draws-1))],3)
    return {'schema':'riz112/step9/ic-simulation/v1','preparation_id':pre['preparation_id'],
            'status':'DEMONSTRATION_ASSUMPTIONS_ONLY_NOT_REAL_Q',
            'target_real':'Q >= 85: moelleux / grains separes',
            'target_simulated':'Q_DEMO* >= 85 (min of four disclosed proxy scores)',
            'ic_demo_percent':round(frac*100,2),
            'mc_95_percent_interval_for_demo_ONLY':[round(100*max(0,centre-half),2),round(100*min(1,centre+half),2)],
            'scientific_ic_percent':None,'real_Q_probability_percent':None,
            'draws':n_draws,'seed':seed,
            'baseline_q_demo':round(baseline_Q,3),'baseline_dimensions_demo':{k:round(v*100,3) for k,v in baseline_scores.items()},
            'simulated_Q_demo_p05_p50_p95':[nearest(.05),nearest(.50),nearest(.95)],
            'avg_simulated_dimensions_demo':{k:round(100*v/n_draws,3) for k,v in sums.items()},
            'coverage':{'cases_visited':112,'d014_routes_visited':62,'physical_numeric_cases':stage6['case_execution']['physical_stage4_count'],
                        'derived_numeric_cases':['043','048'],'quality_proxy_cases':['101','102','103','105'],
                        'other_target_cases_not_quantified':['099','100','104','106','107','108','109','110','111','112'],
                        'nonquantified_contexts_used_as_guards_or_uncertainty':True,'poststart_consumed':0},
            'evidence':{'real_labeled_preparations':0,'independent_prestart_attestation':False,'user_approved_quality_rubric':False,
                        'calibrated':False,'raw_packet_and_contract_sha256':fingerprint(packet,contract)},
            'simulator':{'aggregation':'minimum of four proxy dimensions, not sum of 112 scores',
                         'distribution_parameters':dist,'proxy_scales':thresholds,
                         'four_dimension_quality_substitute_is_NOT_actual_Q':True},
            'warning':'Numerical IC is probability of an ASSUMED proxy under an ASSUMED distribution. It cannot be interpreted as probability of truly successful rice. Do not transfer these numbers/coefficients to MATRICE.'}

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('packet',type=Path);p.add_argument('--contract',type=Path,default=CONTRACT)
 p.add_argument('--draws',type=int,default=3000);p.add_argument('--seed',type=int,default=20261016);p.add_argument('-o','--output',type=Path)
 a=p.parse_args();d=json.loads(a.packet.read_text(encoding='utf8'));c=json.loads(a.contract.read_text(encoding='utf8'))
 out=json.dumps(simulate(d,c,a.draws,a.seed),ensure_ascii=False,indent=2)+'\n'
 if a.output:a.output.write_text(out,encoding='utf8')
 else:print(out,end='')
if __name__=='__main__':main()
