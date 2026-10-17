#!/usr/bin/env python3
"""Strict pre-calibration completeness/evidence gate. No fitted weights/IC.
Accepts facts only, never creates or invents trial records.
"""
from __future__ import annotations
from pathlib import Path
import json,sys,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'step22'))
from trial_registry import TARGETS,TrialError,digest,moment,verify_chain

class GateError(ValueError):pass

def inspect_registry(envelopes,priority_contract,quality_protocol,*,min_independent_real_trials=12):
    # Sample threshold is an operational *gate*, not proof that 12 is statistically sufficient.
    if min_independent_real_trials<2 or type(min_independent_real_trials)!=int:raise GateError('Invalid operational threshold')
    if envelopes:verify_chain(envelopes)
    by_trial={}
    for e in envelopes:
      x=e['payload'];key=x.get('experiment_id')
      if not key:raise GateError('Missing trial id')
      record=by_trial.setdefault(key,{'pre':[],'post':[]})
      if x.get('schema','').endswith('/prestart-registration/v1'):record['pre'].append(x)
      elif x.get('schema','').endswith('/poststart-observation/v1'):record['post'].append(x)
      else:raise GateError('Unrecognized trial artifact')
    eligible=[];rejected={}
    for key,row in by_trial.items():
      reasons=[]
      if len(row['pre'])!=1:reasons.append('EXACTLY_ONE_PRESTART_REQUIRED')
      if len(row['post'])!=1:reasons.append('EXACTLY_ONE_POSTSTART_REQUIRED')
      if not reasons:
        a,b=row['pre'][0],row['post'][0]
        if a['source_class']!='REAL_OBSERVATION' or b['source_class']!='REAL_OBSERVATION':reasons.append('SYNTHETIC_NOT_EMPIRICAL')
        if a['packet_sha256']!=b['parent_packet_sha256']:reasons.append('PACKET_MISMATCH')
        if b['missing_target_ids'] or set(b['measurements'])!=set(TARGETS):reasons.append('INCOMPLETE_OUTCOMES')
        if moment(a['registered_at_utc'])>moment(a['freeze_utc']):reasons.append('POSTFREEZE_PREDICTION')
        if moment(b['recorded_at_utc'])<moment(a['start_utc']):reasons.append('TIME_LEAK')
      if reasons:rejected[key]=reasons
      else:eligible.append(key)
    weight_ok=priority_contract.get('numerical_weights') is not None and priority_contract.get('Q_score_formula') is not None
    approval=bool(quality_protocol.get('approved_by_user')) and bool(quality_protocol.get('Q_score_formula')) and weight_ok
    if approval and any(not quality_protocol['target_rubrics'][x].get('measurement_method_finalized') for x in TARGETS):approval=False
    if not approval:blocks=['Q_SCORING_NOT_PREREGISTERED_OR_USER_APPROVED']
    else:blocks=[]
    if len(eligible)<min_independent_real_trials:blocks.append('INSUFFICIENT_VERIFIABLE_REAL_TRIALS')
    blocks.append('CALIBRATION_AND_OUT_OF_SAMPLE_VALIDATION_NOT_RUN')
    return {'schema':'riz112/step23/empirical-readiness-gate/v1','eligible_real_paired_trials':len(eligible),
      'eligible_ids':eligible,'ineligible_trials':rejected,
      'preregistered_Q_approved':approval,'operational_minimum_not_statistical_guarantee':min_independent_real_trials,
      'calibration_allowed_now':False,'scientific_ic_percent':None,'blocking_reasons':blocks,
      'status':'STOP_UNTIL_REAL_MEASUREMENTS_AND_CALIBRATION','note':'This gate cannot certify calibration, only prerequisites. Held-out validation still mandatory.'}

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--priority',type=Path,required=True);p.add_argument('--quality',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 args=p.parse_args()
 obj=inspect_registry([],json.loads(args.priority.read_text(encoding='utf8')),json.loads(args.quality.read_text(encoding='utf8')))
 args.out.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
