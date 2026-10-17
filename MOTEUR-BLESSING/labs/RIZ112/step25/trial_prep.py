#!/usr/bin/env python3
"""Prepare (never fake) empty rice trial collection documents and readiness receipt."""
from __future__ import annotations
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'step23'))
from evidence_gate import inspect_registry
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'step22'))
from trial_registry import TARGETS, preflight, TrialError

class PrepError(ValueError):pass

def build_empty_template(q_contract):
    if q_contract.get('status')!='PROPOSAL_NOT_APPROVED' or q_contract.get('approved_by_user') is not False:
        raise PrepError('Unexpected quality protocol approval')
    return {'schema':'riz112/step25/empty-paired-collection-template/v1',
      'status':'EMPTY_USER_FILLABLE_TEMPLATE_NOT_EVIDENCE',
      'experiment_id':None,'source_class':None,
      'prestart':{'packet_file_path':None,'packet_sha256':None,'registration_utc':None,
          'freeze_utc':None,'T0_utc':None,'predicted_quality_probability':None,
          'observer_or_source_id':None,'equipment_id':None},
      'poststart':{'observer_id':None,'measurement_utc':None,'source_identifier':None,
         'measurements':{i:{'status':'NOT_MEASURED','observation':None,'unit':None,
             'observed_at_utc':None,'source':None} for i in TARGETS}},
      'Q_formula_approved':False,'Q_score':None,'success_label':None,
      'scientific_ic_percent':None,'real_rice_trial_count':0,
      'instructions':['Do not fill a value based on the model instead of a measurement.',
                      'Freeze genuine raw inputs before starting heat/T0; timestamps must be real.',
                      'Observe separately only after T0 and record actual missingness, never zero.',
                      'Get explicit quality scoring protocol approval before assigning Q.',
                      'Food safety requires a separate validated check; score does not certify safety.']}

def check_template(obj):
    if obj.get('schema')!='riz112/step25/empty-paired-collection-template/v1':raise PrepError('Wrong schema')
    if obj.get('status')!='EMPTY_USER_FILLABLE_TEMPLATE_NOT_EVIDENCE':raise PrepError('Not an empty template')
    if obj.get('scientific_ic_percent') is not None or obj.get('Q_score') is not None or obj.get('success_label') is not None:
        raise PrepError('Fake quality claims')
    if obj.get('source_class') is not None or obj.get('experiment_id') is not None:raise PrepError('No trial exists')
    if obj.get('poststart',{}).get('measurements',{}).keys()!=set(TARGETS):raise PrepError('Missing outcome rubric')
    if any(x['status']!='NOT_MEASURED' or x['observation'] is not None or x['observed_at_utc'] is not None
           for x in obj['poststart']['measurements'].values()):raise PrepError('Template must not contain fabricated observations')
    return True

def dry_run_gate(priority,quality_draft):
    return inspect_registry([],priority,quality_draft)

def check_synthetic_rejected(packet):
    # Prevent labeling the existing artificial A packet as a real trial.
    try:
        preflight(packet,experiment_id='ACTUAL_RICE_001',source_class='REAL_OBSERVATION',
           registered_at_utc=packet['prestart']['freeze_utc'],source_identifier='SYNTHETIC_PACKET_FOR_NEGATIVE_TEST')
    except TrialError:
        return {'synthetic_pretending_real_rejected':True,'legitimate_real_trials_detected':0}
    raise PrepError('Synthetic packet was accepted as a real observation')

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--proposal',type=Path,required=True);ap.add_argument('--priority',type=Path,required=True)
 ap.add_argument('--quality-draft',type=Path,required=True);ap.add_argument('--synthetic-packet',type=Path,required=True)
 ap.add_argument('--out-template',type=Path,required=True);ap.add_argument('--out-check',type=Path,required=True);a=ap.parse_args()
 proposal=json.loads(a.proposal.read_text(encoding='utf8'))
 template=build_empty_template(proposal);check_template(template)
 receipt={'schema':'riz112/step25/dry-run-readiness/v1',
   'quality_contract_status':proposal['status'],
   'synthetic_negative_control':check_synthetic_rejected(json.loads(a.synthetic_packet.read_text(encoding='utf8'))),
   'empirical_gate':dry_run_gate(json.loads(a.priority.read_text(encoding='utf8')),json.loads(a.quality_draft.read_text(encoding='utf8'))),
   'no_real_trial_created':True,'Q_score':None,'scientific_ic_percent':None}
 a.out_template.write_text(json.dumps(template,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 a.out_check.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
