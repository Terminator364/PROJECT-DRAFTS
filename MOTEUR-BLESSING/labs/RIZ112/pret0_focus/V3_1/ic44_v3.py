#!/usr/bin/env python3
"""MOTEUR RIZ112 v3: pre-T0 44-parameter mechanistic synthetic experiment.

Strictly a hypothetical laboratory for MATRICE methodology. Neither the declared
quality rubric Q* nor Monte-Carlo exceedance probability IC* is empirically
calibrated. Nothing observed after T0 is ever used as an input.

Qstar = explicitly described weighted quality rubric (0..100) with hard critical
caps. ICstar = empirical Monte Carlo frequency P_model(Qstar>=85 | inputs T0,
pre-declared uncertainty distribution). It is NOT the old V2 product of 7 sigmoid
channels and it is NOT the real-world probability of a good cooking result.
"""
from __future__ import annotations
import copy, math, random, hashlib, json, statistics
from dataclasses import dataclass
from typing import Any
from ic44 import run as physical_v2, perturb_packet, ModelError
from bridge44 import PRESTART, TWINS, when, BridgeError

SCHEMA='riz112/pret0/IC44_v3/v1'
WEIGHTS={'hydration':0.27,'thermal':0.21,'separation':0.15,'integrity':0.13,
         'hygiene':0.11,'flavour':0.08,'service':0.05}
assert math.isclose(sum(WEIGHTS.values()),1)
UNCERTAINTY_ASSUMPTIONS={
  'water_dosing_cv_with_measuring_tools':0.035,
  'water_dosing_cv_without_tools':0.11,
  'heating_power_cv':0.10,
  'thermal_efficiency_cv':0.13,
  'evaporation_cv':0.19,
  'rice_water_capacity_cv':0.12,
  'gelatinization_time_cv':0.11,
  'retained_water_cv':0.18,
  'surface_starch_cv':0.12,
  'ambient_celsius_sd':1.8,
  'temperature_water_celsius_sd':1.2,
  'temperature_rice_celsius_sd':1.2,
  'salt_mass_cv':0.08,
  'fat_mass_cv':0.07,
  'rice_damage_variation_sd':0.008,
  'additional_quality_epistemic_sd_points':2.5,
}

def clamp(x,lo=0.,hi=1.):return min(hi,max(lo,x))
def ramp_good_above(x,low,good):
    return clamp((x-low)/max(1e-8,good-low))
def ramp_good_below(x,good,high):
    return clamp((high-x)/max(1e-8,high-good))
def good_window(x,bad_low,good_low,good_high,bad_high):
    return min(ramp_good_above(x,bad_low,good_low),ramp_good_below(x,good_high,bad_high))

def grade_physics(physical,inputs,*,stochastic_grade_delta=0.0):
    m=physical['mechanisms'];v=inputs
    # Target windows are POLICY HYPOTHESES, not fitted lab limits or recommendations.
    channels={
        'hydration':good_window(m['hydration_ratio_proxy'],.55,.90,1.08,1.19),
        'thermal':good_window(m['hot_progress_proxy'],.38,.86,1.28,2.10),
        'separation':ramp_good_below(m['stickiness_proxy'],.19,.75),
        'integrity':ramp_good_above(m['structure_integrity_proxy']-m['burnt_proxy']-.25*max(0.,m['pan_occupancy_proxy']-.72),.49,.86),
        'hygiene':ramp_good_above(m['hygiene_proxy'],.72,.96),
        'flavour':clamp(math.exp(-abs(m['salt_planned_g']-v['001']*.011)/max(.7,v['001']*.013)) +m['fat_planned_g']/max(1.,v['001'])*2.),
        'service':ramp_good_above(m['planned_serving_temp_proxy_C'],45.,110.),
    }
    # A planned contamination risk or substantial undercooking cannot be erased
    # by attractive service or flavour; hard caps encode non-compensatory rules.
    critical_caps={}
    if m['hydration_ratio_proxy']<.70:critical_caps['insufficient_hydration']=60.
    if m['hot_progress_proxy']<.62:critical_caps['undercooking']=60.
    if m['hot_progress_proxy']>2.0:critical_caps['overcooking']=72.
    if m['hygiene_proxy']<.78:critical_caps['hygiene']=59.
    if m['burnt_proxy']>.28:critical_caps['burnt']=67.
    if m['pan_occupancy_proxy']>1.0:critical_caps['overflow']=66.
    if m['feasibility_proxy']<.55:critical_caps['plan_feasibility']=64.
    raw=100.*sum(WEIGHTS[k]*v for k,v in channels.items())
    cap=min(critical_caps.values(),default=100.)
    q=clamp(raw+stochastic_grade_delta,0,cap)
    return {'Qstar':round(q,6),'Q_unrestricted':round(raw,6),
            'channels':{k:round(100*c,5) for k,c in channels.items()},
            'critical_caps':critical_caps,
            'physically_modelled_risks':{
                'hydration_ratio':round(m['hydration_ratio_proxy'],5),
                'thermal_progress':round(m['hot_progress_proxy'],5),
                'starch_stickiness':round(m['stickiness_proxy'],5),
                'hygiene_proxy':round(m['hygiene_proxy'],5),
                'burn_proxy':round(m['burnt_proxy'],5),
                'feasibility_proxy':round(m['feasibility_proxy'],5),
            }}

def packet_values(packet):return {rid:packet['case_inputs'][rid]['value'] for rid in PRESTART}

def validate_preT0(packet):
    # Old model's routing performs exact 44 input check, timestamp freeze,
    # semantic twins and missing-value handling. Do not accept future outcomes.
    result=physical_v2(packet)
    if result['IC_DEMO_PCT'] is None:return result
    for rid,v in packet_values(packet).items():
        if v is None:raise BridgeError('unknown preT0 input '+rid)
    return result

def _nominal_if_power_operates(base_packet):
    # R007 is reliability (probability of operation), not an extra permanent
    # derating of the heater when it works. The V2 physical core uses R007 as
    # derating, so set it to 1 ONLY inside this CONDITIONAL physical world.
    packet=copy.deepcopy(base_packet)
    packet['case_inputs']['007']['value']=1.0
    return physical_v2(packet)

def _mc_draw(base_packet, rng):
    """Future unobserved quantities are SAMPLED from assumptions frozen at T0.
    They are simulation internals, not actual readings or pre-T0 observations.
    """
    packet=copy.deepcopy(base_packet)
    vals=packet_values(packet)
    U=UNCERTAINTY_ASSUMPTIONS
    # All variation factors below are hypothetical. Stable regulated heating and
    # measuring tools reduce dispersion; this is a declared scenario-dependent
    # hypothesis, never chosen based on desired IC outputs.
    heat_scale=0.63 if (vals['017'] and vals['018']>=.90 and vals['007']>=.95) else 1.0
    rice_scale=0.75 if (vals['019'] and vals['020'] and vals['027'] in ('lot_A_synthetic','lot_B_synthetic','lot_C_synthetic')) else 1.0
    def modify(rid,value):
        packet['case_inputs'][rid]['value']=value
        if rid in TWINS:packet['prestart']['inputs'][TWINS[rid]]['value']=value
    def perturb_multiplier(rid,cv,minv=.001,maxv=None):
        v=vals[rid]
        sampled=v*math.exp(rng.gauss(-.5*cv*cv,cv))
        modify(rid,max(minv,min(maxv,sampled)) if maxv is not None else max(minv,sampled))
    dose_cv=U['water_dosing_cv_with_measuring_tools'] if vals['019'] and vals['020'] else U['water_dosing_cv_without_tools']
    perturb_multiplier('035',dose_cv,minv=.1)
    perturb_multiplier('041',U['heating_power_cv']*heat_scale,minv=10.)
    perturb_multiplier('042',U['thermal_efficiency_cv']*heat_scale,minv=.05,maxv=.99)
    perturb_multiplier('045',U['evaporation_cv']*heat_scale,minv=.01)
    perturb_multiplier('033',U['rice_water_capacity_cv']*rice_scale,minv=.1)
    perturb_multiplier('034',U['gelatinization_time_cv']*rice_scale,minv=1.)
    perturb_multiplier('036',U['retained_water_cv'],minv=0.)
    perturb_multiplier('030',U['surface_starch_cv'],minv=.001,maxv=1.)
    perturb_multiplier('003',U['salt_mass_cv'],minv=0.)
    perturb_multiplier('004',U['fat_mass_cv'],minv=0.)
    for rid,k in [('037','temperature_water_celsius_sd'),('038','temperature_rice_celsius_sd'),('039','ambient_celsius_sd')]:
        modify(rid,max(-20.,min(120.,vals[rid]+rng.gauss(0,U[k]))))
    modify('029',clamp(vals['029']+rng.gauss(0,U['rice_damage_variation_sd'])))
    # Whether the declared source actually functions when needed is an
    # inherently unpredictable post-T0 event. Draw it, do not observe it.
    operating=rng.random()<vals['007']
    modify('007',1.0) # when it operates it works at nominal rate
    return packet,operating

def _wilson(k,n,z=1.96):
    p=k/n; zz=z*z; d=1+zz/n
    mid=(p+zz/(2*n))/d
    half=z*math.sqrt(p*(1-p)/n+zz/(4*n*n))/d
    return [round(100*max(0,mid-half),3),round(100*min(1,mid+half),3)]

def simulate(packet,*,draws=256,seed=20261023,threshold=85.0):
    if type(draws) is not int or not 32<=draws<=10000:raise ValueError('draws 32..10000')
    if type(seed) is not int or seed<0:raise ValueError('seed nonnegative int')
    if threshold!=85:raise ValueError('user contract threshold Q*>=85')
    contract_validation=validate_preT0(packet)
    if contract_validation['IC_DEMO_PCT'] is None:
        return {'schema':SCHEMA,'status':'ABSTAIN_UNKNOWN_PRET0',
                'missing':contract_validation.get('missing',[]),'quality_Qstar':None,
                'IC_model_percent':None,'IC_scientific_percent':None}
    values=packet_values(packet)
    baseline=_nominal_if_power_operates(packet)
    basegrade=grade_physics(baseline,values)
    rng=random.Random(seed)
    nsuccess=0; samples=[]
    for i in range(draws):
        draw,energy_ok=_mc_draw(packet,rng)
        if not energy_ok:
            q=0.0 # no heat, treated as failed preparation for this experiment
        else:
            physics=physical_v2(draw)
            q=grade_physics(physics,packet_values(draw),stochastic_grade_delta=rng.gauss(0,UNCERTAINTY_ASSUMPTIONS['additional_quality_epistemic_sd_points']))['Qstar']
        samples.append(q)
        if q>=threshold:nsuccess+=1
    samples.sort()
    return {'schema':SCHEMA,'status':'SYNTHETIC_NOT_CALIBRATED',
            'prestart_variable_count':44,'preparation_id':packet.get('prestart',{}).get('preparation_id'),
            'quality_Qstar':basegrade['Qstar'],
            'quality_Qstar_interpretation':'Nominal grade CONDITIONAL on source operating; source failure risk remains in the MC distribution',
            'nominal_channels':basegrade['channels'],
            'critical_caps_nominal':basegrade['critical_caps'],
            'nominal_proxies':basegrade['physically_modelled_risks'],
            'IC_model_percent':round(100*nsuccess/draws,3),
            'MC_successes':nsuccess,'MC_draws':draws,'MC_seed':seed,
            'MC_mean_Qstar_including_outages':round(statistics.mean(samples),3),
            'MC_Wilson_95_sampling_only':_wilson(nsuccess,draws),
            'Qstar_samples_p10_p50_p90':[round(samples[round(p*(draws-1))],2) for p in (.1,.5,.9)],
            'IC_scientific_percent':None,'real_cooking_trials':0,
            'threshold_model_Qstar':threshold,
            'legacy_V2_IC_discarded_as_probability':True,
            'uncertainty_model':'DECLARED_SYNTHETIC_ASSUMPTIONS',
            'probability_description':'Frequency inside an uncalibrated synthetic simulator, never observed real-world success.'}

def counterfactual(packet,rid,value,*,draws=256,seed=20261023):
    baseline=simulate(packet,draws=draws,seed=seed)
    altered=simulate(perturb_packet(packet,rid,value),draws=draws,seed=seed)
    return {'parameter':rid,'delta_Qstar':None if baseline['quality_Qstar'] is None else
           round(altered['quality_Qstar']-baseline['quality_Qstar'],4),
           'delta_IC_model_pp':None if baseline['IC_model_percent'] is None else
           round(altered['IC_model_percent']-baseline['IC_model_percent'],3),
           'baseline':baseline['IC_model_percent'],'new':altered['IC_model_percent'],
           'common_random_numbers':True}
