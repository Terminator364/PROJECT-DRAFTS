#!/usr/bin/env python3
"""MOTEUR BLESSING — Contract « formule du riz » / completeness audit.

Audits genuine engine packets and outputs. No claim of calibration. No arbitrary
numeric weight or 62x additive bonus is introduced. The result distinguishes
62 named worlds from 62 world participation in the actual mathematical engine.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

EXPECTED_WORLD_ROLES = {'PREDICTOR_CANDIDATE': 55, 'GATE': 4,
                        'PRIOR': 1, 'OUTPUT_ONLY': 2}
ALLOWED_ENGINE_STATUSES = {
    'REFERENCE_ONLY_NO_SPORTS_TRAINING', 'RESEARCH_FITTED_NOT_VALIDATED',
    'NO_ADMISSIBLE_PREMATCH_PRIOR'
}


class ContractError(ValueError):
    pass


def _catalog_rows(catalog):
    if isinstance(catalog, dict):
        rows = catalog.get('parameters')
    else:
        rows = catalog
    if not isinstance(rows, list) or len(rows) != 62:
        raise ContractError('Expected canonical catalogue with exactly 62 worlds')
    ids = [r.get('id') for r in rows]
    if not all(isinstance(k, str) and k for k in ids) or len(set(ids)) != 62:
        raise ContractError('Invalid or duplicate world IDs')
    roles = Counter(r.get('role') for r in rows)
    if dict(roles) != EXPECTED_WORLD_ROLES:
        raise ContractError('World-role governance mismatch')
    return rows


def audit(packet, engine, catalog, *, claimed_independent_PIT=False,
          claimed_chronological_validation=False):
    """Never promotes user-entered compliance claims to genuine independent proof.

    The two claimed_* arguments only signal that such assertions need evidence;
    they cannot activate a sports-qualified score. A separate independent proof
    verifier and a locked OOS validation protocol are prerequisites in the future.
    """
    rows = _catalog_rows(catalog)
    if not isinstance(packet, dict) or not isinstance(engine, dict):
        raise ContractError('packet and engine output must be JSON objects')
    supplied = packet.get('parameters')
    if not isinstance(supplied, dict):
        raise ContractError('parameters must be a world object')
    expected_ids = {r['id'] for r in rows}
    if set(supplied) != expected_ids:
        raise ContractError('World IDs do not exactly match frozen canonical catalogue')
    if engine.get('status') not in ALLOWED_ENGINE_STATUSES:
        raise ContractError('Unknown engine result status')
    fixture = packet.get('fixture')
    if not isinstance(fixture, dict) or fixture.get('id') != engine.get('fixture_id'):
        raise ContractError('Engine output and packet fixture differ')
    model_hash = engine.get('model_sha256')
    trained = (engine['status'] == 'RESEARCH_FITTED_NOT_VALIDATED'
               and isinstance(model_hash, str) and len(model_hash) == 64)
    if engine['status'] == 'REFERENCE_ONLY_NO_SPORTS_TRAINING' and model_hash:
        raise ContractError('Reference status cannot simultaneously claim a fitted model')
    if engine.get('module_count', 62) != 62:
        raise ContractError('Engine did not enumerate all worlds')
    expected_fields = sum(len(r.get('inputs', [])) for r in rows)
    expected_formulas = sum(len(r.get('formulas', {})) for r in rows)
    worlds = []
    all_supplied_inputs = 0
    for r in rows:
        value = supplied[r['id']]
        if not isinstance(value, dict):
            raise ContractError('World %s is not an input object' % r['id'])
        known_fields = {e['name'] for e in r.get('inputs', [])}
        if not set(value).issubset(known_fields):
            raise ContractError('World %s contains fields not in original recipe' % r['id'])
        all_supplied_inputs += len(value)
        worlds.append({
            'id': r['id'], 'role': r['role'],
            'expected_inputs': len(known_fields), 'supplied_inputs': len(value),
            'candidate_formulas': len(r.get('formulas', {})),
            'audit_status': ('INPUTS_PROVIDED_PENDING_PROVENANCE' if value
                             else 'DECLARED_ONLY_NO_OBSERVATION'),
            'why_it_matters': (
                'prediction candidate, only model-trained effects can affect IC'
                if r['role'] == 'PREDICTOR_CANDIDATE' else
                'governs admissibility and proof, not an independent goal effect'
                if r['role'] == 'GATE' else
                'baseline/prior controls numeric starting point'
                if r['role'] == 'PRIOR' else
                'derived diagnostic/output must not be weighted as an independent goal cause')
        })
    mechanisms = engine.get('mechanism_audit_first_scenario', [])
    if not isinstance(mechanisms, list):
        raise ContractError('Mechanism audit must be a list')
    actually_computed = sum(m.get('status') == 'COMPUTED_CANDIDATE_NOT_VALIDATED'
                            for m in mechanisms if isinstance(m, dict))
    if engine.get('mechanisms_computed_first_scenario', actually_computed) != actually_computed:
        raise ContractError('Mechanism count contradicts audit trail')
    reference = engine.get('reference_ic_percent')
    raw_ic = engine.get('ic_percent')
    if raw_ic is not None and (not isinstance(raw_ic, (int, float))
                               or isinstance(raw_ic, bool) or not 0 <= raw_ic <= 100):
        raise ContractError('Malformed engine percentage')
    status = ('ABSTAIN_RICE_FORMULA_NOT_INTEGRATED' if not trained
              else 'RESEARCH_CONDITIONAL_UNVALIDATED')
    # Never claim external scientific certification from supplied JSON assertions.
    return {
        'schema': 'moteur-blessing/rice-integrity-audit/v1',
        'fixture_id': fixture['id'],
        'status': status,
        'full_match_specific_ic_percent': None,
        'separate_baseline_percent': reference if engine['status'] != 'NO_ADMISSIBLE_PREMATCH_PRIOR' else None,
        'raw_engine_percentage_preserved_for_audit_only': raw_ic,
        'engine_status_original': engine['status'],
        'all_62_ids_named': True,
        'all_62_roles_processed_in_audit': True,
        'input_worlds_observed': sum(bool(supplied[r['id']]) for r in rows),
        'input_fields_observed': all_supplied_inputs,
        'total_recipe_input_capacity': expected_fields,
        'total_candidate_formulas': expected_formulas,
        'mechanisms_computed': actually_computed,
        'mechanisms_total': len(mechanisms),
        'model_loaded': trained,
        'PIT_independently_certified': False,
        'chronological_OOS_scientifically_validated': False,
        'user_assertions_are_not_evidence': bool(claimed_independent_PIT or claimed_chronological_validation),
        'worlds': worlds,
        'missing_integrity_conditions': [
            'PER_WORLD_ACTUAL_INPUTS_AND_DERIVATIONS',
            'ORIGINAL_PREMATCH_RAW_SOURCE_PIT_INDEPENDENT_PROOF',
            'WORLD_INTERACTION_DEPENDENCE_AND_JOINT_SCENARIO_AUDIT',
            'FITTED_MODEL_WITH_AUDITED_LINEAGE',
            'INDEPENDENT_CHRONOLOGICAL_OOS_BEATING_REFERENCE',
            'CALIBRATION_AND_UNCERTAINTY_VALIDATED'
        ],
        'no_numeric_weight_invented': True,
        'remedy': 'Show reference separate; do not call it the user-requested full IC.'
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('packet', type=Path)
    p.add_argument('engine_output', type=Path)
    p.add_argument('catalogue', type=Path)
    p.add_argument('--output', type=Path)
    opts = p.parse_args()
    packet = json.loads(opts.packet.read_text(encoding='utf-8'))
    result = json.loads(opts.engine_output.read_text(encoding='utf-8'))
    if 'engine_output' in result:
        result = result['engine_output']
    catalog = json.loads(opts.catalogue.read_text(encoding='utf-8'))
    analysis = audit(packet, result, catalog)
    s = json.dumps(analysis, ensure_ascii=False, indent=2) + '\n'
    if opts.output:
        opts.output.write_text(s, encoding='utf-8')
    else:
        print(s, end='')

if __name__ == '__main__':
    main()
