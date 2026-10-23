#!/usr/bin/env python3
"""Explain one 44-input pre-T0 world: ONE global IC and 44 conditional IC probes.

Core computation delegated to canonical ic44_v3.simulate. This does not assign
44 independent probabilities, nor alter original inputs or manufacture effects.
Use from a reproducible working copy of the V3.1 archive (same folder as
ic44_v3.py, bridge44.py, ic44.py and alternatives.py).
"""
from __future__ import annotations
import csv, json, argparse, copy
from pathlib import Path
from bridge44 import PRESTART
from ic44 import perturb_packet
from ic44_v3 import simulate
from alternatives import ALT

def changed_value(old, alternative, rid):
    if old != alternative:
        return alternative
    if type(old) is bool:
        return not old
    if type(old) in (float, int):
        return float(old)*1.17 if old else .1
    options={
        '006':['gas','electricity','charcoal'],
        '010':['aluminium','steel','copper','ceramic'],
        '012':['clean_flat','slightly_warped','worn'],
        '015':['unvented','narrow_vent','vented'],
        '016':['gas_burner','electric_hotplate','charcoal_stove'],
        '024':['long_white_hypothesis','medium_white_hypothesis','short_white_hypothesis'],
        '026':['polished','parboiled','unprocessed'],
        '027':['lot_A_synthetic','lot_B_synthetic','lot_C_synthetic']}
    if rid not in options:
        raise ValueError('no alternative distinct from observed: '+rid)
    return next(v for v in options[rid] if v!=old)

def diagnose(packet, alternatives=ALT, *, draws=128, seed=20261023):
    """Return 1 global IC and 44 conditional what-if ICs, with common MC seed."""
    if set(packet.get('case_inputs',{}))!=set(PRESTART):
        raise ValueError('exactly 44 prestart fields required')
    if set(alternatives)!=set(PRESTART):
        raise ValueError('alternatives must cover exactly 44 fields')
    base=simulate(packet,draws=draws,seed=seed)
    if base['IC_model_percent'] is None:
        return {'status':'ABSTAIN','IC_global':None,'per_parameter':[]}
    detail=[]
    for rid in PRESTART:
        before=packet['case_inputs'][rid]['value']
        alternative=changed_value(before,alternatives[rid],rid)
        trial=simulate(perturb_packet(packet,rid,alternative),draws=draws,seed=seed)
        if trial['IC_model_percent'] is None:
            raise ValueError('counterfactual became invalid: '+rid)
        detail.append({
            'parameter_id':rid,'before':before,'alternative':alternative,
            'IC_global_before_percent':base['IC_model_percent'],
            'IC_global_if_parameter_changed_percent':trial['IC_model_percent'],
            'delta_IC_percentage_points':round(trial['IC_model_percent']-base['IC_model_percent'],3),
            'Qstar_nominal_before':base['quality_Qstar'],
            'Qstar_nominal_after':trial['quality_Qstar'],
            'MC_common_random_numbers':True,
            'meaning':'conditional difference in scenario IC; NOT a standalone factor probability'})
    assert len(detail)==44
    return {
      'schema':'riz112/pret0/1-global-IC-plus-44-conditional-effects/v1',
      'status':'SYNTHETIC_NOT_CALIBRATED',
      'scenario':packet.get('prestart',{}).get('preparation_id'),
      'parameters':44,'IC_global_percent':base['IC_model_percent'],
      'Qstar_nominal':base['quality_Qstar'],
      'conditional_IC_values':44,'effect_nonzero_count':
          sum(abs(x['delta_IC_percentage_points'])>1e-9 for x in detail),
      'effect_zero_count':
          sum(abs(x['delta_IC_percentage_points'])<=1e-9 for x in detail),
      'per_parameter':detail,'scientific_IC':None}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--packet',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--seed',type=int,default=20261023)
    parser.add_argument('--draws',type=int,default=128)
    args=parser.parse_args()
    packet=json.loads(args.packet.read_text(encoding='utf-8'))
    report=diagnose(packet,draws=args.draws,seed=args.seed)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('ONE_GLOBAL_IC',report['IC_global_percent'],
          'PARAMETER_IMPACT_ROWS',len(report['per_parameter']),
          'NONZERO',report.get('effect_nonzero_count'))

if __name__=='__main__':main()
