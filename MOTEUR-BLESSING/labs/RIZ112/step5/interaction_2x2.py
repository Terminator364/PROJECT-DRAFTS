#!/usr/bin/env python3
"""Contrefactuels 2x2 pré-T0 : interaction mécanistique, pas score de réussite."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'reference'/'step4'))
from riz112 import analyze, INPUT_SPECS  # type: ignore


def contrast(packet:dict, factor_a:str, low_a:float, high_a:float,
             factor_b:str, low_b:float, high_b:float, measured_node='W_shortfall') -> dict:
    if factor_a == factor_b or any(f not in INPUT_SPECS for f in (factor_a,factor_b)):
        raise ValueError('deux paramètres pré-T0 distincts et connus requis')
    if not all(isinstance(v,(int,float)) and type(v) is not bool for v in (low_a,high_a,low_b,high_b)):
        raise ValueError('valeurs numériques requises')
    scenarios={}
    for first,a in [('L',low_a),('H',high_a)]:
        for second,b in [('L',low_b),('H',high_b)]:
            p=copy.deepcopy(packet)
            p['inputs'][factor_a]['value']=a
            p['inputs'][factor_b]['value']=b
            out=analyze(p)
            nodes={n['node']:n['value'] for n in out['graph_trace']}
            if measured_node not in nodes: raise ValueError('nœud absent')
            scenarios[first+second]=nodes[measured_node]
    diff=scenarios['HH']-scenarios['HL']-scenarios['LH']+scenarios['LL']
    return {'factors':[factor_a,factor_b], 'measured_mechanism':measured_node,
            'scenario_outputs':scenarios, 'factorial_interaction_contrast':round(diff,6),
            'interpretation':'Nonadditivity within simplified graph; not causal effect nor success IC',
            'calibrated_IC_percent':None, 'outcome_data_used':False}

if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]/'reference'/'step4'/'exemples'/'A_couvercle_ajuste.json'
    d=json.loads(p.read_text(encoding='utf8'))
    print(json.dumps(contrast(d,'lid_multiplier',0.3,1.4,'power_W',180,900),ensure_ascii=False,indent=2))
