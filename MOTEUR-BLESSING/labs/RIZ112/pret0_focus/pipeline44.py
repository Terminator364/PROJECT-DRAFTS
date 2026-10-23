#!/usr/bin/env python3
"""RIZ112 strict pre-T0 entrypoint; trace 44/44 before legacy Step9 Q* proxy.

All resource gates are feasibility checks, not invented additive Q bonuses.
No post-T0 observations can enter via bridge44; scientific IC stays null.
"""
from pathlib import Path
import json
import sys
from bridge44 import evaluate44

ROOT=Path(__file__).resolve().parents[1]
BOOLEAN_GATES=('013','017','019','020','021','022','023')

def run44(packet, contract=None, n_draws=200, seed=20261023, simulator=None):
    trace=evaluate44(packet)
    r=trace['routes']
    issues=[]
    if type(r['002']['output']) in (float,int) and r['002']['output']<0:
        issues.append('002: potable-water supply below planned dose')
    if type(r['008']['output']) in (float,int) and r['008']['output']<0:
        issues.append('008: vessel volume below simplified resource requirement')
    if type(r['005']['output']) in (float,int) and r['005']['output']<=0:
        issues.append('005: planned rinse requires water resource')
    for rid in ('006','016'):
        item=r[rid]['output']
        if isinstance(item,tuple) and item[2] is False:
            issues.append(rid+': source and burner incompatible')
    for rid in BOOLEAN_GATES:
        if r[rid]['output'] is False:
            issues.append(rid+': planned action lacks required capability')
    envelope={
      'schema':'riz112/pret0/complete-44-pipeline/v1',
      'preparation_id':packet['prestart'].get('preparation_id'),
      'prestart_routed':44,
      'prestart_evaluated':trace['evaluated_count'],
      'trace':trace,'prestart_gate_issues':issues,
      'scientific_ic_percent':None,
      'legacy_demo_ic_is_not_44_calibrated_quality_probability':True}
    if issues:
        return {**envelope,'status':'ABSTAIN_PRET0_CONSTRAINT',
                'ic_demo_percent':None,'legacy_simulation':None}
    if simulator is None:
        sys.path.insert(0,str(ROOT/'step9'))
        from ic_simulation_v1 import simulate, CONTRACT
        simulator=simulate
        if contract is None:
            contract=json.loads(CONTRACT.read_text(encoding='utf8'))
    outcome=simulator(packet,contract,n_draws=n_draws,seed=seed)
    return {**envelope,'status':'LEGACY_QSTAR_PROXY_WITH_44_INPUT_AUDIT',
            'ic_demo_percent':outcome.get('ic_demo_percent'),
            'legacy_simulation':outcome}

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('packet',type=Path)
    ap.add_argument('--draws',type=int,default=200)
    ap.add_argument('--seed',type=int,default=20261023)
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    result=run44(json.loads(args.packet.read_text(encoding='utf8')),
                 n_draws=args.draws,seed=args.seed)
    payload=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output:args.output.write_text(payload,encoding='utf8')
    else:print(payload,end='')
