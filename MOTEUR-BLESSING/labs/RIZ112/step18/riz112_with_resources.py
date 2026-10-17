#!/usr/bin/env python3
"""RIZ112 Step18 integration: original unified engine plus explicit resource constraints.
Do not replace or re-weight the validated H3 synthetic demonstration.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'step16'))
from riz112_unified import run
from resource_feasibility import evaluate_resources,perturb_resource,ResourceContractError

def run_with_resources(packet, *, lab_root=None, assumptions=None, require_h3=False):
    original=run(packet,lab_root=lab_root,require_h3=require_h3)
    resources=evaluate_resources(packet,assumptions)
    sensitivity={id:perturb_resource(packet,assumptions,id) for id in ('002','005','008')}
    return {**original,'schema':'riz112/unified-pre-T0/step18-v1',
       'step18_resource_constraints':resources,
       'step18_counterfactuals':sensitivity,
       'scientific_ic_percent':None,
       'effect_promotion_status':'NONE_CALIBRATED__ALL_STEP18_IMPACTS_ON_INTERMEDIATE_DIAGNOSTICS_ONLY',
       'limitations':[original['message'],resources['limits']]}

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--packet',type=Path,required=True);p.add_argument('--lab-root',type=Path,required=True)
    p.add_argument('--assumptions',type=Path,required=True);p.add_argument('--output',type=Path)
    a=p.parse_args(argv)
    packet=json.loads(a.packet.read_text('utf-8'));assumptions=json.loads(a.assumptions.read_text('utf-8'))
    out=run_with_resources(packet,lab_root=a.lab_root,assumptions=assumptions,require_h3=True)
    txt=json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    if a.output:a.output.write_text(txt,encoding='utf8')
    else:print(txt)
    return 0
if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,TypeError,KeyError) as e:print('STEP18 FAIL-CLOSED: '+str(e),file=sys.stderr);sys.exit(2)
