#!/usr/bin/env python3
"""RIZ112→MATRICE: deterministic temporal-proof prototype, not a sports prediction model.

Five pre-kickoff snapshots; recorded sources must have been available at each
snapshot cutoff. UNKNOWN is not zero. Post-match outcomes never enter inputs.
No football forecast, scoring coefficient, or API dependency is produced.
"""
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

WINDOWS=("J-6","J-4","J-3","H-9","H-0")
SCHEMA="moteur-riz112-to-matrice/prematch-proof/v1"

class TemporalIntegrityError(ValueError):
    pass


def parse_instant(value, field):
    if not isinstance(value,str):
        raise TemporalIntegrityError(field+": ISO date with explicit timezone required")
    try:
        d=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError as e:
        raise TemporalIntegrityError(field+": invalid timestamp") from e
    if d.tzinfo is None or d.utcoffset() is None:
        raise TemporalIntegrityError(field+": naive timezone prohibited")
    return d.astimezone(timezone.utc)


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)


def stable_sha(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def verify_timeline(bundle):
    if not isinstance(bundle,dict) or bundle.get('schema')!=SCHEMA:
        raise TemporalIntegrityError('Invalid timeline schema')
    if bundle.get('source_class')!='SYNTHETIC_PREMATCH_METHOD_TEST':
        raise TemporalIntegrityError('This prototype accepts only synthetic methodology examples')
    if not isinstance(bundle.get('fixture_id'),str) or not bundle['fixture_id'].strip():
        raise TemporalIntegrityError('Stable synthetic fixture identifier required')
    if 'outcome' in bundle or 'label' in bundle or 'postmatch' in bundle:
        raise TemporalIntegrityError('Post-match outcome cannot enter prematch packet')
    kickoff=parse_instant(bundle.get('kickoff_at_utc'),'kickoff_at_utc')
    snapshots=bundle.get('snapshots')
    if not isinstance(snapshots,list) or len(snapshots)!=5:
        raise TemporalIntegrityError('Require exactly five frozen horizon snapshots')
    if [x.get('window') for x in snapshots if isinstance(x,dict)]!=list(WINDOWS):
        raise TemporalIntegrityError('Horizon sequence must be J-6,J-4,J-3,H-9,H-0')
    prev_cutoff=None;last_facts={};reports=[]
    for i,snap in enumerate(snapshots):
        if not isinstance(snap,dict):raise TemporalIntegrityError('Malformed snapshot')
        if 'outcome' in snap or 'postmatch' in snap or 'label' in snap:
            raise TemporalIntegrityError('Post-match label leakage')
        cutoff=parse_instant(snap.get('snapshot_cutoff_at_utc'),'snapshot_cutoff_at_utc')
        if cutoff>=kickoff or (prev_cutoff is not None and cutoff<=prev_cutoff):
            raise TemporalIntegrityError('Cutoff order, or kickoff boundary violated')
        sources=snap.get('facts')
        if not isinstance(sources,list):raise TemporalIntegrityError('Fact collection required')
        seen={};unknown=0
        for fact in sources:
            if not isinstance(fact,dict):raise TemporalIntegrityError('Invalid fact')
            if fact.get('information_scope')!='PRE_MATCH':
                raise TemporalIntegrityError('Only PRE_MATCH predictors admissible')
            key=fact.get('field')
            if not isinstance(key,str) or not key.strip():
                raise TemporalIntegrityError('Fact key required')
            if key in seen:raise TemporalIntegrityError('Duplicate semantic fact '+key)
            state=fact.get('state')
            if state not in ('CONFIRMED','PROVISIONAL','UNKNOWN'):
                raise TemporalIntegrityError('Invalid source state')
            value=fact.get('value')
            if (state=='UNKNOWN')!=(value is None):
                raise TemporalIntegrityError('UNKNOWN requires null, known requires non-null')
            if not isinstance(fact.get('source_id'),str) or not fact['source_id'].strip():
                raise TemporalIntegrityError('Source identifier absent')
            if not isinstance(fact.get('unit'),str) or not fact['unit'].strip():
                raise TemporalIntegrityError('Explicit units or categorical domain required')
            observed=parse_instant(fact.get('observed_at_utc'),'observed_at_utc')
            available=parse_instant(fact.get('available_at_utc'),'available_at_utc')
            ingested=parse_instant(fact.get('ingested_at_utc'),'ingested_at_utc')
            if observed>available or available>ingested or ingested>cutoff:
                raise TemporalIntegrityError('Source did not exist in information set at snapshot '+snap['window'])
            if key in last_facts:
                previous=last_facts[key]
                if (previous['value'],previous['state'])!=(value,state) and available<=prev_cutoff:
                    raise TemporalIntegrityError('Changed fact without new time-admissible evidence '+key)
            seen[key]={'value':value,'state':state,'available_at':available}
            unknown+=state=='UNKNOWN'
        reports.append({'window':snap['window'],'snapshot_cutoff_at_utc':snap['snapshot_cutoff_at_utc'],
                        'known_facts':len(seen)-unknown,'unknown_facts':unknown,
                        'snapshot_sha256':stable_sha(snap),
                        'hours_before_kickoff':round((kickoff-cutoff).total_seconds()/3600,4)})
        last_facts=seen;prev_cutoff=cutoff
    return {'schema':'moteur-riz112-to-matrice/prematch-proof-receipt/v1',
            'status':'VALID_SYNTHETIC_PREMATCH_INFORMATION_SETS_ONLY',
            'fixture_id':bundle['fixture_id'],'windows':reports,
            'frozen_pre_match_bundle_sha256':stable_sha(bundle),
            'post_match_predictions_or_labels_used':False,
            'predicted_match_probability':None,
            'actual_match_observations':0,
            'scientific_calibration':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--infile',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    payload=json.loads(a.infile.read_text(encoding='utf8'))
    result=verify_timeline(payload)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('PREMATCH_TEMPORAL_PROOF_PASS',len(result['windows']))
