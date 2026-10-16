#!/usr/bin/env python3
"""RIZ112 stage10: fail-closed toy-IC on ANY changed/unfrozen quality target.

This is a technical target contract gate, not empirical rice calibration. No
unvalidated factor, policy or action is given fabricated numerical Q effect.
"""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'step9'))
from ic_simulation_v1 import simulate

CONTRACT=Path(__file__).with_name('GATE_V10.json')
def digest(x):
 return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def audited_simulate(packet, contract=None, draws=3000, seed=20261016):
 if contract is None:contract=json.loads(CONTRACT.read_text(encoding='utf8'))
 if not isinstance(contract,dict) or contract.get('schema')!='riz112/strict-demo-target-v10':
  raise ValueError('Unknown V10 target-gate contract')
 if contract.get('scientific_approval') is not False:raise ValueError('Cannot mark unvalidated quality as approved')
 expected=contract.get('demo_quality_target_sha256')
 if not isinstance(expected,str) or len(expected)!=64:raise ValueError('Missing quality target digest')
 t=packet.get('target_contract',{})
 if not isinstance(t,dict):return {'status':'ABSTAIN_TARGET_INVALID','ic_demo_percent':None,'scientific_ic_percent':None}
 actual=digest(t)
 if actual!=expected or len(t)!=14 or any(v.get('status')!='DRAFT' for v in t.values()):
  return {'schema':'riz112/step10/guarded-demo-IC/v1','status':'ABSTAIN_TARGET_CONTRACT_CHANGED',
          'ic_demo_percent':None,'scientific_ic_percent':None,
          'reason':'One or more of 14 future-quality definitions differ from the frozen demonstrator. A new explicit target version and model evaluation are required.',
          'target_fingerprint_expected':expected,'target_fingerprint_actual':actual,
          'target_cases_checked':len(t),'outcome_label_values_consumed':0}
 ic_contract=json.loads((ROOT/'step9/DEMONSTRATION_CONTRACT.json').read_text(encoding='utf8'))
 r=simulate(packet,ic_contract,draws,seed)
 r['schema']='riz112/step10/guarded-demo-IC/v1'
 r['target_integrity']={'frozen_target_cases_checked':14,'digest_sha256':actual,
                       'scientific_approval':False,'future_labels_as_predictors':0,
                       'quality_target_only_demo':True}
 return r

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('packet',type=Path);p.add_argument('--draws',type=int,default=3000)
 args=p.parse_args();packet=json.loads(args.packet.read_text(encoding='utf8'))
 print(json.dumps(audited_simulate(packet,draws=args.draws),indent=2,ensure_ascii=False))
