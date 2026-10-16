#!/usr/bin/env python3
"""MB-1 V4: typed gate contracts and fail-closed fixture audit.

These are proposal-level technical interfaces, not independently verified facts.
Each of 24 GATE requirements is a distinct evidence obligation. All records
remain quarantined, even if a user supplies 24 apparently valid entries.
Never emits an approved scoring decision.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import json
from pathlib import Path

from evidence_vault_v1 import audit as vault_audit
from requirements_plan_v3 import ROOT, build_plan

# One explicit, source-vetted *measurement design* per governance requirement.
# A required field describes what would need proof, NOT an observed fact.
GATE_SPECS = {
    'FIXTURE_ID': [
        ('fixture_organizer_id', 'identifier', 'official organizer fixture ID valid at cutoff'),
        ('season_and_round_id', 'identifier', 'season edition and round from a dated organizer release'),
        ('canonical_home_away_ids', 'pair_of_identifiers', 'stable home/away IDs; aliases audited'),
        ('fixture_status_asof', 'enum', 'status valid at cutoff; cancel/postpone handled as GATE'),
        ('venue_timezone_iana', 'iana_timezone', 'zone identity from dated stadium information'),
        ('kickoff_utc_crosscheck', 'utc_instant', 'kickoff confirmed from independent published schedules'),
    ],
    'DATA_QUALITY': [
        ('archive_publication_capture', 'timestamp_pair', 'original publication and independent archive capture'),
        ('raw_original_artifact', 'sha256_bytes', 'immutable raw primary artifact and byte hash'),
        ('upstream_source_independence', 'lineage_graph', 'different publishers, not copied syndication'),
        ('time_conversion_trace', 'utc_transformation', 'source zone, raw local clock and UTC conversion'),
        ('definition_revision', 'versioned_definition', 'version/date/statistical numerator and denominator definitions'),
        ('correction_conflict_ledger', 'append_only_ledger', 'conflicting corrections must retain all versions'),
    ],
    'MODEL_DOMAIN': [
        ('competition_format_asof', 'enum', 'league/cup and tournament rules as of cutoff'),
        ('opponent_population', 'dataset_partition', 'strength level and population inclusion before fixture'),
        ('engine_source_digest', 'source_sha256', 'immutable model code/config digest'),
        ('xg_admissible_domain', 'numeric_domain', 'training-derived admissible xG scope; undefined if untrained'),
        ('missingness_status', 'missing_value_policy', 'UNKNOWN distinct from measured zero and absent artifacts'),
        ('chronological_oos_calibration', 'evaluation_report', 'real chronological OOS evidence required for any promotion'),
    ],
    'PLAY_TIME_RULES': [
        ('regulation_time_rule', 'competition_rule', 'regulation-time definition includes stoppage time'),
        ('leg_structure', 'competition_rule', 'one match regulation goals, not aggregate over legs'),
        ('stoppage_policy', 'competition_rule', 'stoppage included; no time additions miscounted'),
        ('competition_interruptions_asof', 'dated_notice', 'pre-match suspensions/venue bans and fixture viability'),
        ('extra_time_separation', 'competition_rule', 'extra time and penalties strictly excluded from goal total'),
        ('disciplinary_rule_context', 'dated_rule', 'disciplinary rules documented; never treated as goal count'),
    ],
}
SCHEMA = 'MOTEUR_MB1_V4_GATE_READINESS_NOT_SCIENTIFIC_APPROVAL'


def build_contracts(root: Path = ROOT) -> dict:
    plan = build_plan(root)
    by_id = {r['id']:r for r in plan['entries']}
    specs = {}
    for world, contracts in GATE_SPECS.items():
        if len(contracts)!=6:
            raise ValueError('gate has not exactly six documented obligations')
        for index, (field, data_type, proof) in enumerate(contracts, 1):
            sid = f'{world}::R{index:02d}'
            entry = by_id.get(sid)
            if not entry or entry['role']!='GATE':
                raise ValueError(f'wrong GATE contract identity: {sid}')
            specs[sid] = {
                'id':sid, 'field':field, 'type':data_type, 'semantics_to_verify':proof,
                'source_lane':entry['source_lane'],
                'required_evidence':'ORIGINAL_BYTES_SHA256_AND_INDEPENDENT_POINT_IN_TIME_CAPTURE',
                'value_status':'UNKNOWN_NOT_OBSERVED',
                'effect_weight':None,
            }
    gate_ids = {x['id'] for x in plan['entries'] if x['role']=='GATE'}
    if set(specs)!=gate_ids or len(specs)!=24:
        raise ValueError('uncovered/unexpected GATE obligation')
    return {'schema':'MOTEUR_MB1_V4_TYPED_GATE_CONTRACTS','source_version':'V1.1.2+MB1V3',
            'canonical_worlds':62,'subparameter_proposals':372,
            'governance_contracts':24, 'contracts':dict(sorted(specs.items())),
            'validation_status':'MEASUREMENT_DESIGN_ONLY',
            'PIT_independently_authenticated':False, 'scoring_authorized':False}


def _records(vault: Path) -> list[dict]:
    out=[]
    for path in sorted((vault/'records').glob('*.json')):
        obj = json.loads(path.read_text(encoding='utf-8'))
        out.append(obj['evidence'])
    return out


def gate_readiness(vault: Path, fixture_id: str, root: Path = ROOT) -> dict:
    """Read original bytes via V3 vault audit, then count obligations conservatively.

    A locally populated vault can NEVER establish PIT provenance. This is an
    engineering completeness check only. A match without vetted provenance
    must never receive a predictive IC through this routine.
    """
    contracts=build_contracts(root)['contracts']
    registry=build_plan(root)
    report=vault_audit(vault,registry)
    errors=[]
    if report['records_invalid']:
        errors.append('VAULT_CORRUPT_OR_UNVERIFIED_RECORDS')
    records=[] if report['records_invalid'] else [r for r in _records(vault) if r['fixture_id']==fixture_id]
    # Single fixture/cutoff identity. Two records with different kickoff or
    # freeze refer to different point-in-time snapshots and cannot mix.
    cutoffs={(r['freeze_utc'],r['kickoff_utc']) for r in records}
    if len(cutoffs)>1:
        errors.append('INCONSISTENT_FIXTURE_FREEZE_OR_KICKOFF')
    gate_records=defaultdict(list)
    for r in records:
        sid=r.get('subparameter_id')
        if sid in contracts:
            gate_records[sid].append(r)
    duplicate_ids=sorted(x for x,items in gate_records.items() if len(items)>1)
    if duplicate_ids:
        errors.append('CONFLICTING_OR_DUPLICATED_GATE_RECORDS')
    missing=sorted(set(contracts)-set(gate_records))
    # Check evidence is at least chronologically self-consistent and was not
    # altered in the vault. Even a perfect result here is UNAUTHENTICATED.
    complete=not (errors or missing)
    return {'schema':SCHEMA, 'fixture_id':fixture_id,
        'expected_gate_evidence_records':24,
        'present_gate_obligations':len(gate_records),
        'missing_gate_obligations':missing,'duplicate_gate_obligations':duplicate_ids,
        'vault_record_count_for_fixture':len(records),
        'claims_structurally_complete':complete,
        'errors':errors,
        'source_time_claims_authenticated_independently':False,
        'governance_status':'QUARANTINED_NOT_CLEARED' if records else 'BLOCKED_MISSING_EVIDENCE',
        'scoring_authorized':False,'model_promotion_allowed':False,
        'decision':'DO_NOT_ISSUE_VALIDATED_IC',
        'next_required':'INDEPENDENT_POINT_IN_TIME_AUTHENTICATION_AND_OOS_CALIBRATION'}


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--vault',type=Path)
    p.add_argument('--fixture-id')
    p.add_argument('--contracts',action='store_true')
    args=p.parse_args()
    if args.contracts:
        data=build_contracts(args.root)
    else:
        if not args.vault or not args.fixture_id:
            p.error('provide --vault and --fixture-id, or --contracts')
        data=gate_readiness(args.vault,args.fixture_id,args.root)
    print(json.dumps(data,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
