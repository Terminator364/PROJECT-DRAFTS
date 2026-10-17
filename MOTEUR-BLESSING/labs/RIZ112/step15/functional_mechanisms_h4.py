#!/usr/bin/env python3
"""RIZ-112 H4/A: 7 pre-T0 rubrics linked by three *diagnostic* mechanisms.

Cases 003/061: salt inventory and intended use; 049/082: portion plan;
029/030/054: broken grains and planned surface-starch rinse. These are
conservation/feasibility calculations, NOT learned effects on quality or IC.
No after-start observed mass, taste, texture, or Q is ever consumed.
"""
from __future__ import annotations
from datetime import datetime
import math

class H4EvidenceError(ValueError):
    pass

def _ts(value):
    if not isinstance(value, str):
        raise H4EvidenceError('timestamp must be an ISO 8601 string with timezone')
    try:
        t = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as e:
        raise H4EvidenceError('invalid timestamp') from e
    if t.tzinfo is None or t.utcoffset() is None:
        raise H4EvidenceError('timezone required')
    return t

def _value(value, low, high, field):
    if type(value) not in (float, int) or not math.isfinite(value) or not low <= value <= high:
        raise H4EvidenceError(f'{field} must be a finite number between {low} and {high}')
    return float(value)

def _row(row, freeze, start, name, *, allowed=('OBSERVED', 'PLANNED', 'ASSUMPTION')):
    if not isinstance(row, dict) or not isinstance(row.get('source'), str) or not row['source'].strip():
        raise H4EvidenceError(f'{name} requires a source')
    t = _ts(row.get('available_at_utc'))
    if t > freeze or freeze >= start:
        raise H4EvidenceError(f'{name} violates pre-T0 availability')
    state = row.get('state', row.get('kind', row.get('status')))
    if state not in (*allowed, 'UNKNOWN', 'NOT_PLANNED'):
        raise H4EvidenceError(f'{name} has unknown state')
    return state

def _supplement(item, freeze, start, name, unit):
    # Extra pre-T0 measurements must explicitly declare provenance, unit and time.
    if item is None:
        return None
    state = _row(item, freeze, start, name)
    if item.get('unit') != unit:
        raise H4EvidenceError(f'{name}: expected {unit}')
    if state == 'UNKNOWN':
        if item.get('value') is not None:
            raise H4EvidenceError(f'{name}: UNKNOWN cannot have a value')
        return None
    if state not in ('OBSERVED','PLANNED','ASSUMPTION'):
        raise H4EvidenceError(f'{name}: unplanned supplement')
    return item['value']

def evaluate_h4_diagnostics(packet: dict, *,
                            salt_dose: dict | None = None,
                            portion_count: dict | None = None,
                            salt_stock: dict | None = None,
                            broken_grain_fraction: dict | None = None) -> dict:
    """Pure, non-mutating diagnostics; supplemental observations are dated.

    Overrides allowed only for UNKNOWN stock/fraction from a newer pre-T0 source.
    No IC/quality effect is imputed from these arithmetic identities.
    """
    freeze = _ts(packet['prestart']['freeze_utc'])
    start = _ts(packet['prestart']['start_utc'])
    if not freeze < start:
        raise H4EvidenceError('freeze must precede start')
    rows = packet['case_inputs']
    actions = packet['action_plans']
    inputs = packet['prestart']['inputs']
    for case in ('001','003','029','030'):
        _row(rows[case], freeze, start, f'case {case}')
    for case in ('049','054','061','082'):
        _row(actions[case], freeze, start, f'plan {case}')
    for field in ('rice_mass_g','surface_starch_index','rinse_removal_fraction'):
        _row(inputs[field], freeze, start, field)
    rice = _value(inputs['rice_mass_g']['value'], 0.001, 1_000_000, 'rice_mass_g')
    # Require consistent shared primitive to avoid two inputs representing one mass.
    case_mass = _value(rows['001']['value'], 0.001, 1_000_000, 'case 001')
    if abs(case_mass-rice)>1e-8:
        raise H4EvidenceError('case 001 and physical rice_mass_g disagree')
    salt_state = rows['003']['state']
    if salt_state == 'UNKNOWN':
        if rows['003']['value'] is not None:
            raise H4EvidenceError('UNKNOWN stock has value')
        raw_stock = _supplement(salt_stock, freeze, start, 'salt_stock', 'g')
    else:
        if salt_stock is not None:
            raise H4EvidenceError('known stock must not be silently overridden')
        raw_stock = rows['003']['value']
    stock = None if raw_stock is None else _value(raw_stock, 0, 100_000, 'salt stock')
    raw_dose = _supplement(salt_dose, freeze, start, 'salt_dose', 'g')
    if salt_dose is not None and actions['061']['status']!='PLANNED':
        raise H4EvidenceError('salt action 061 not predeclared')
    dose = None if raw_dose is None else _value(raw_dose, 0, 100_000, 'salt dose')
    if stock is not None and dose is not None:
        salt = {'status':'CALCULATED_PRESTART_FEASIBILITY', 'available_g':stock, 'planned_g':dose,
                'shortfall_g':round(max(0,dose-stock),8),'feasible':dose<=stock,
                'planned_salt_per_dry_rice_g':round(dose/rice,8),
                'cases':['003','061']}
    else:
        salt = {'status':'UNKNOWN_INPUT_OR_UNDECLARED_PLAN', 'available_g':stock, 'planned_g':dose,
                'feasible':None, 'cases':['003','061']}
    raw_n = _supplement(portion_count, freeze, start, 'portion_count', 'count')
    if portion_count is not None and any(actions[k]['status']!='PLANNED' for k in ('049','082')):
        raise H4EvidenceError('portion actions 049 and 082 must both be predeclared')
    if raw_n is not None:
        count = _value(raw_n, 1, 100, 'planned portion count')
        if not count.is_integer():
            raise H4EvidenceError('portion count must be integral')
        portions = {'status':'CALCULATED_DRY_MASS_ALLOCATION', 'planned_count':int(count),
                    'dry_rice_per_portion_g':round(rice/count,8),
                    'only_dry_mass_not_final_cooked_yield':True,'cases':['049','082']}
    else:
        portions = {'status':'UNKNOWN_PLAN', 'planned_count':None, 'cases':['049','082']}
    if rows['029']['state']=='UNKNOWN':
        if rows['029']['value'] is not None:raise H4EvidenceError('UNKNOWN broken-grain row has value')
        broken_raw = _supplement(broken_grain_fraction,freeze,start,'broken_grain_fraction','fraction')
    else:
        if broken_grain_fraction is not None:
            raise H4EvidenceError('known broken fraction must not be overwritten')
        broken_raw = rows['029']['value']
    broken = None if broken_raw is None else _value(broken_raw,0,1,'broken fraction')
    native_starch = _value(rows['030']['value'],0,1,'case 030 starch')
    starch = _value(inputs['surface_starch_index']['value'],0,1,'surface starch index')
    if abs(starch-native_starch)>1e-8:
        raise H4EvidenceError('case 030 and surface_starch_index disagree')
    removal = _value(inputs['rinse_removal_fraction']['value'],0,1,'rinse removal')
    if actions['054']['status']!='PLANNED' and removal>0:
        raise H4EvidenceError('positive rinsing fraction requires a predeclared plan 054')
    grain = {'status':'CALCULATED_PRESTART_MASS_AND_INDEX_DIAGNOSTICS',
             'broken_grain_fraction':broken,
             'broken_dry_mass_g':round(rice*broken,8) if broken is not None else None,
             'intact_dry_mass_g':round(rice*(1-broken),8) if broken is not None else None,
             'planned_surface_starch_index_after_rinse':round(starch*(1-removal),8),
             'starch_index_model':'bookkeeping index only; not measured final adhesiveness',
             'cases':['029','030','054']}
    return {'schema':'riz112/H4A/diagnostic/v1', 'status':'PRESTART_DIAGNOSTICS_ONLY',
            'mechanisms':{'salt':salt,'portions':portions,'grain_rinse':grain},
            'rubric_paths':['003','061','049','082','029','030','054'],
            'distinct_primitive_groups':['salt_inventory_vs_planned_dose','dry_rice_mass_vs_count',
                                         'broken_mass_and_surface_starch_rinse'],
            'scientific_ic_percent':None,'new_q_effects_calibrated':0,
            'post_start_values_consumed':0,'independently_authenticated_source_times':False,
            'limitations':['No predicted cooked mass, taste, texture or final quality',
                           'No double-counting with H3 rice-profile physical inputs',
                           'Declared timestamps are not independently authenticated PIT evidence']}
