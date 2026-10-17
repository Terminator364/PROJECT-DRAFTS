#!/usr/bin/env python3
"""Append-only pre-T0/after-T0 paired experiment records; NO calibration.

Explicitly separates simulations from real observations, without fabricating trials.
All records must be signed off on input source; no implicit zero for missing data.
"""
from __future__ import annotations
import json,hashlib,math,datetime,os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'step16'))
from riz112_unified import verify_packet,moment
TARGETS=tuple(f'{i:03d}' for i in range(99,113))
class TrialError(ValueError):pass

def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(x):return hashlib.sha256(canonical(x).encode('utf8')).hexdigest()
def preflight(packet,*,experiment_id, source_class, registered_at_utc,source_identifier):
  verified=verify_packet(packet)
  if source_class not in ('SYNTHETIC_REHEARSAL','REAL_OBSERVATION'):
    raise TrialError('Evidence class must be explicit')
  if not isinstance(experiment_id,str) or not experiment_id.strip() or '/' in experiment_id or '\\' in experiment_id:
    raise TrialError('Invalid trial ID')
  if not source_identifier or not isinstance(source_identifier,str):raise TrialError('Source identifier mandatory')
  if not isinstance(registered_at_utc,str):raise TrialError('Registration timestamp missing')
  at=moment(registered_at_utc);freeze=moment(packet['prestart']['freeze_utc']);T0=moment(packet['prestart']['start_utc'])
  if at>freeze: raise TrialError('Prediction registration must precede freeze')
  if source_class=='REAL_OBSERVATION':
    for s in packet['prestart']['inputs'].values():
      if isinstance(s,dict) and ('hypothese_de_demonstration' in str(s.get('source','')) or 'dossier_initial_de_demonstration' in str(s.get('source',''))):
        raise TrialError('Synthetic packet cannot be presented as a real rice trial')
  return {'schema':'riz112/step22/prestart-registration/v1','experiment_id':experiment_id,
    'source_class':source_class,'source_identifier':source_identifier,
    'registered_at_utc':registered_at_utc,'freeze_utc':packet['prestart']['freeze_utc'],
    'start_utc':packet['prestart']['start_utc'],'packet_sha256':digest(packet),
    'prestart_validated':True,'real_quality_label':None,'Q_score':None,'scientific_IC_percent':None,
    'no_post_T0_leakage':True,'not_calibrated':True}

def outcome_draft(registry,*,observed_at_utc, observations, observer_id, source_identifier):
    if not observer_id or not source_identifier: raise TrialError('Provenance/observer required')
    if moment(observed_at_utc)<moment(registry['start_utc']):raise TrialError('Cannot observe outcome before start')
    if not isinstance(observations,dict) or any(x not in TARGETS for x in observations):raise TrialError('Unrecognized output rubric')
    results={}
    for key,row in observations.items():
      if not isinstance(row,dict) or set(row)!={'status','observation','unit','observed_at_utc','source'}:
        raise TrialError('Exact observation schema required')
      if row['status'] not in ('MEASURED','NOT_MEASURED'):
        raise TrialError('No implicit status')
      if (row['status']=='NOT_MEASURED') != (row['observation'] is None):
        raise TrialError('Unmeasured must have null; measured must have explicit value')
      if row['status']=='MEASURED':
        if not row['unit'] or not row['source'] or isinstance(row['observation'],bool):raise TrialError('No provenance/unit/boolean as measurement')
        if isinstance(row['observation'],float) and not math.isfinite(row['observation']):raise TrialError('Nonfinite observation')
      t=moment(row['observed_at_utc'])
      if t<moment(registry['start_utc']) or t>moment(observed_at_utc):raise TrialError('Temporal leakage in observed record')
      results[key]=row
    return {'schema':'riz112/step22/poststart-observation/v1',
       'experiment_id':registry['experiment_id'],'parent_packet_sha256':registry['packet_sha256'],
       'source_class':registry['source_class'],
       'observer_id':observer_id,'source_identifier':source_identifier,'recorded_at_utc':observed_at_utc,
       'measurements':results,'missing_target_ids':[x for x in TARGETS if x not in results or results[x]['status']=='NOT_MEASURED'],
       'Q_score':None,'scientific_IC_percent':None,'scoring_approved':False,
       'caution':'Draft observation, not a scored outcome; never input measurements to pre-T0 predictor'}

def append_envelope(path,record):
    """Single-writer, exclusive file-lock append; protect against truncated chains.

    Not a trusted timestamp/signature. Multi-process participants must all use this
    writer; cloud sync may still conflict and must be reconciled explicitly.
    """
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if not isinstance(record,dict) or 'schema' not in record:raise TrialError('Record schema required')
    lock=path.with_suffix(path.suffix+'.lock')
    try:fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError as ex:raise TrialError('Concurrent writer detected; retry only after reconciliation') from ex
    try:
        os.close(fd)
        lines=[]
        if path.exists():
            for ln in path.read_text(encoding='utf8').splitlines():
                x=json.loads(ln);lines.append(x)
            verify_chain(lines)
        if any(x['record_sha256']==digest(record) for x in lines):raise TrialError('Duplicate record')
        prev=lines[-1]['envelope_sha256'] if lines else 'GENESIS'
        envelope={'sequence':len(lines)+1,'previous_digest':prev,'payload':record,'record_sha256':digest(record)}
        envelope['envelope_sha256']=hashlib.sha256((prev+'\n'+canonical(envelope)).encode('utf8')).hexdigest()
        with path.open('a',encoding='utf8',newline='\n') as f:
            f.write(canonical(envelope)+'\n');f.flush();os.fsync(f.fileno())
        return envelope
    finally:
        try:lock.unlink()
        except FileNotFoundError:pass

def verify_chain(lines):
    prev='GENESIS'
    for ix,x in enumerate(lines,1):
      if x['sequence']!=ix or x['previous_digest']!=prev or x['record_sha256']!=digest(x['payload']):raise TrialError('Chain identity failure')
      chk=hashlib.sha256((prev+'\n'+canonical({k:v for k,v in x.items() if k!='envelope_sha256'})).encode('utf8')).hexdigest()
      if x['envelope_sha256']!=chk:raise TrialError('Chain tampered')
      prev=chk
    return prev
