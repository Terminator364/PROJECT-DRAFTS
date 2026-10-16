#!/usr/bin/env python3
"""RIZ-112 / étape 5 : preuve temporelle, séparation X/y, qualité et abstention.

Zéro prétention : ceci NE valide ni labels, ni physique du riz, ni modèles.
Aucun champ de qualité post-cuisson ne peut devenir une variable pré-T0.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any
import sys

ROOT4 = Path(__file__).resolve().parents[1] / "reference" / "step4"
sys.path.insert(0, str(ROOT4))
from riz112 import analyze, utc, InvalidPacket  # type: ignore

QUALITY_DIMS = ("tenderness", "grain_separation", "uniformity", "grain_integrity", "free_water", "burning")
LABEL_FIELDS = {"quality_score_100", "outcome", "observed_at_utc", "future_measurements", "success", "measured_texture"}
FEATURE_NODES = ("W_shortfall", "W_free", "F_hot", "S_residual", "E_evap")
HEX = set('0123456789abcdef')

class StudyError(ValueError): pass

def canonical_sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()

def sha256_ok(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= HEX

def require_object_exact(obj, required, label):
    if not isinstance(obj, dict) or set(obj) != set(required):
        raise StudyError(f'{label}: contrat exact requis {sorted(required)}')

def check_quality_protocol(protocol: dict) -> dict:
    required = {'schema', 'id', 'status', 'target', 'outcome_threshold_q_100', 'start_boundary',
                'measurement_dimensions', 'approved_weights', 'score_aggregation_formula',
                'inter_observer_agreement_protocol', 'approved_by_user',
                'registered_before_first_real_trial', 'scientific_status'}
    require_object_exact(protocol, required, 'protocole')
    if protocol['schema'] != 'riz112/quality_protocol/v1' or protocol['outcome_threshold_q_100'] != 85:
        raise StudyError('seuil/format qualité changé sans décision')
    if not isinstance(protocol['id'], str) or not protocol['id'].strip():
        raise StudyError('identifiant qualité manquant')
    dims = protocol['measurement_dimensions']
    if not isinstance(dims, list) or tuple(x.get('id') for x in dims) != QUALITY_DIMS:
        raise StudyError('dimensions qualité altérées ou incomplètes')
    for x in dims:
        if set(x) != {'id','definition','measurement_method','scale','weight','veto_threshold'}:
            raise StudyError('métadonnées dimensions non conformes')
    if protocol['status'] == 'DRAFT_NOT_APPROVED':
        if any([protocol['approved_by_user'], protocol['registered_before_first_real_trial'],
                protocol['score_aggregation_formula'], protocol['approved_weights'] is not None,
                any(x['weight'] is not None for x in dims)]):
            raise StudyError('barème de projet déclaré approuvé sans protocole')
        return {'approved':False,'protocol_hash':canonical_sha(protocol),'status':'DRAFT_NOT_APPROVED'}
    # Future changes require a formal independently verified registry, not user JSON claims.
    raise StudyError('approbation de protocole non implémentée : registre indépendant requis')

def prestart_feature_record(packet: dict) -> dict:
    if any(key in packet for key in LABEL_FIELDS):
        raise StudyError('fuite de valeur post-cuisson dans le paquet pré-T0')
    try: result = analyze(packet)
    except InvalidPacket as e: raise StudyError(f'entrée étape4 invalide: {e}') from e
    nodes = {n['node']:n for n in result['graph_trace']}
    return {
        'preparation_id':packet['preparation_id'],
        'prestart_packet_sha256':canonical_sha(packet),
        'frozen_utc':utc(packet['freeze_utc'], 'freeze_utc').isoformat(),
        'start_utc':utc(packet['start_utc'], 'start_utc').isoformat(),
        'mechanism_features':{k:nodes[k]['value'] for k in FEATURE_NODES},
        'feature_lineage':{k:{'equation':nodes[k]['formula'],'depends_on':nodes[k]['dependencies'],'cases':nodes[k]['cases']} for k in FEATURE_NODES},
        'outcomes_used_for_inference':[],
        'input_data_independently_timestamped':False,
        'real_physical_model_validated':False,
        'probability_percent':None,
        'decision':'ABSTAIN_NON_CALIBRE'
    }

def assess_trial(trial: dict, protocol: dict) -> dict:
    """Separate predictor snapshot and future label; all supplied provenance is *declared*."""
    p = check_quality_protocol(protocol)
    require_object_exact(trial, {'trial_id','prestart','prestart_capture_utc','poststart','poststart_capture_utc','dataset_role','synthetic'},'trial')
    if not isinstance(trial['trial_id'],str) or not trial['trial_id'].strip():
        raise StudyError('trial_id manquant')
    if type(trial['synthetic']) is not bool or trial['dataset_role'] not in ('CANDIDATE','TRAIN','CALIBRATION','HOLDOUT'):
        raise StudyError('rôle/déclaration synthétique invalide')
    input_rec = prestart_feature_record(trial['prestart'])
    snap=utc(trial['prestart_capture_utc'],'prestart_capture_utc')
    freeze=utc(trial['prestart']['freeze_utc'],'freeze_utc')
    start=utc(trial['prestart']['start_utc'],'start_utc')
    if not snap <= freeze < start:
        raise StudyError('capture pré-T0 déclarée trop tardive')
    outcome=trial['poststart']
    require_object_exact(outcome, {'preparation_id','observed_at_utc','protocol_id','dimensions','quality_score_100','evidence_sha256','provenance_status'},'outcome')
    if outcome['preparation_id'] != trial['prestart']['preparation_id'] or outcome['protocol_id'] != protocol['id']:
        raise StudyError('identité préparation ou version qualité incompatible')
    measured=utc(outcome['observed_at_utc'],'observed_at_utc')
    stored=utc(trial['poststart_capture_utc'],'poststart_capture_utc')
    if not start < measured <= stored:
        raise StudyError('étiquette impossible avant la préparation ou capture incohérente')
    dims=outcome['dimensions']
    if not isinstance(dims,dict) or set(dims)!=set(QUALITY_DIMS):
        raise StudyError('six critères qualités requis, inconnus acceptés comme null')
    for x in dims.values():
        if x is not None and (type(x) not in (int,float) or not math.isfinite(x)):
            raise StudyError('dimension invalide / NaN interdit')
    q=outcome['quality_score_100']
    if q is not None and (type(q) not in (int,float) or not math.isfinite(q) or not 0<=q<=100):
        raise StudyError('Q hors plage 0-100')
    if q is not None and not p['approved']:
        raise StudyError('Q numérique interdit avant accord sur barème')
    if not sha256_ok(outcome['evidence_sha256']):
        raise StudyError('empreinte d’archive poststart invalide')
    if outcome['provenance_status'] not in ('SELF_DECLARED', 'REQUIRES_EXTERNAL_VERIFICATION'):
        raise StudyError('une attestation indépendante ne peut pas être certifiée via JSON déclaratif')
    reasons=['QUALITY_PROTOCOL_NOT_APPROVED','INDEPENDENT_CAPTURE_NOT_VERIFIED','PHYSICAL_MODEL_NOT_VALIDATED']
    if trial['synthetic']: reasons.append('SYNTHETIC_TRIAL')
    return {'trial_id':trial['trial_id'],'status':'QUARANTINE','reasons':reasons,
            'feature_record':input_rec,'declared_measured_dimensions':dims,
            'real_quality_label':None,'IC_percent':None,
            'prediction_available':False,'training_eligible':False,
            'outcome_timestamp_used_as_feature':False}

def audit_dataset(trials: list, protocol: dict) -> dict:
    check_quality_protocol(protocol)
    if not isinstance(trials,list): raise StudyError('jeu non liste')
    ids, hashes, out = set(),set(),[]
    for trial in trials:
        r=assess_trial(trial,protocol)
        if trial['trial_id'] in ids or r['feature_record']['prestart_packet_sha256'] in hashes:
            raise StudyError('essai/préparation doublonnée (risque fuite train/holdout)')
        ids.add(trial['trial_id']); hashes.add(r['feature_record']['prestart_packet_sha256'])
        out.append(r)
    return {'trials_checked':len(trials),'trials_for_training':0,'trials_quarantined':len(out),
            'quality_protocol_status':'DRAFT_NOT_APPROVED','calibrated_predictions':0,
            'IC_percent':None,'status':'ABSTAIN_NO_REAL_APPROVED_LABELS','per_trial':out}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--packet',type=Path)
    ap.add_argument('--protocol',type=Path,default=Path(__file__).with_name('qualite_contrat_v1.json'))
    ap.add_argument('--trials',type=Path)
    args=ap.parse_args()
    pr=json.loads(args.protocol.read_text(encoding='utf8'))
    if args.trials:
        answer=audit_dataset(json.loads(args.trials.read_text(encoding='utf8')),pr)
    elif args.packet:
        check_quality_protocol(pr)
        answer=prestart_feature_record(json.loads(args.packet.read_text(encoding='utf8')))
    else: ap.error('requis --packet ou --trials')
    print(json.dumps(answer,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
