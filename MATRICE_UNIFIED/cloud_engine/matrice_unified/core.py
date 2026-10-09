"""Provenance-safe Over 1.5 research engine. Pure stdlib; no joblib/pickle/network.

A compatibility layer for isolated legacy engine outputs, NOT a certified or
newly trained football prediction model. All historical metrics are external.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json
import math
from typing import Any, Iterable

BANNED_FEATURE_NAMES = {'goals', 'total_goals', 'home_goals', 'away_goals',
                        'result', 'score', 'is_over15', 'over15_label', 'ft_score'}
BLOCKED_STATUSES = {'FT', 'AET', 'AP', 'CANCELLED', 'POSTPONED', 'ABANDONED'}
PREMATCH_STATUSES = {'SCHEDULED', 'NS', 'TIMED', 'PRE_MATCH'}
ROUTES = ('v28_legacy', 'v27_legacy', 'v25_legacy', 'v29_legacy',
          'isi_probability', 'poisson_prior')


def parse_dt(value: str) -> datetime:
    """Strictly UTC-aware timestamp; never guess timezone."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError('timestamp_missing')
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('timestamp_timezone_required')
    return dt.astimezone(timezone.utc)


def deterministic_digest(record: Any) -> str:
    payload = json.dumps(record, ensure_ascii=False, sort_keys=True,
                         separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def poisson_over15(lambda_total: float) -> float:
    """P(X >= 2) for X~Poisson(lambda_total). Not a fitted model."""
    lam = float(lambda_total)
    if not math.isfinite(lam) or lam < 0:
        raise ValueError('invalid_poisson_lambda')
    return -math.expm1(-lam) - lam * math.exp(-lam)


def market_ou25_to_over15(over_decimal: float, under_decimal: float) -> dict:
    """Convert de-vigged O/U2.5 odds to O1.5 via Poisson approximation.

    IMPORTANT: shape assumption must be calibrated/validated empirically.
    """
    o, u = float(over_decimal), float(under_decimal)
    if min(o,u) <= 1 or not (math.isfinite(o) and math.isfinite(u)):
        raise ValueError('invalid_decimal_odds')
    io, iu = 1/o, 1/u
    p_over25 = io / (io + iu)
    lo, hi = 0.0, 32.0
    for _ in range(80):
        mid = (lo+hi)/2
        p = 1-math.exp(-mid)*(1+mid+mid*mid/2)
        if p < p_over25: lo = mid
        else: hi = mid
    lam = (lo+hi)/2
    return {'lambda_total': lam, 'market_p25_novig': p_over25,
            'market_p15_poisson_approx': poisson_over15(lam),
            'overround': io+iu-1}


@dataclass(frozen=True)
class Prediction:
    match_id: str
    status: str
    reason: str
    route: str | None
    p_over15: float | None
    digest: str
    expected_roi_net: float | None
    evidence: dict


def _fail(match_id: str, reason: str, evidence: dict | None = None) -> Prediction:
    evidence = evidence or {}
    d = deterministic_digest({'match_id': match_id,'reason':reason,'evidence':evidence})
    return Prediction(match_id,'ABSTAIN',reason,None,None,d,None,evidence)


def _valid_source(source: dict, decision: datetime, kickoff: datetime) -> tuple[bool, str]:
    if not isinstance(source, dict) or not source.get('source_id'):
        return False,'source_id_missing'
    try:
        known = parse_dt(source['known_at_utc'])
    except (KeyError, TypeError, ValueError):
        return False,'known_at_invalid'
    if known > decision: return False,'future_information_leakage'
    if known >= kickoff: return False,'post_kickoff_information'
    return True,'ok'


def predict(packet: dict) -> Prediction:
    """Validate fixture and route precomputed evidence without deserializing models.

    packet={match_id,fixture:{kickoff_utc,status},decision_at_utc,
            feature_evidence:[{name,value,source_id,known_at_utc}],
            route_candidates:[{route,p_over15,source_id,known_at_utc,verified}],
            route_policy:[...], optional odds_o15:{...}, optional fees_fraction}
    No invented p if no route evidence. Optional Poisson prior also requires
    timestamped, sourced lambda_total and explicit research approval.
    """
    if not isinstance(packet,dict): return _fail('UNKNOWN','packet_invalid')
    match_id = str(packet.get('match_id') or 'UNKNOWN')
    fixture = packet.get('fixture') or {}
    if not isinstance(fixture,dict) or not str(fixture.get('competition','')).strip():
        return _fail(match_id,'fixture_competition_missing')
    if not all(str(fixture.get(k,'')).strip() for k in ('home','away','kickoff_utc','status')):
        return _fail(match_id,'fixture_required_fields_missing')
    if fixture['home']==fixture['away']: return _fail(match_id,'self_match_invalid')
    if str(fixture['status']).upper() in BLOCKED_STATUSES:
        return _fail(match_id,'fixture_not_prematch')
    if str(fixture['status']).upper() not in PREMATCH_STATUSES:
        return _fail(match_id,'fixture_status_unknown')
    try:
        kickoff = parse_dt(fixture['kickoff_utc'])
        decision = parse_dt(packet['decision_at_utc'])
    except (ValueError,KeyError,TypeError): return _fail(match_id,'time_contract_invalid')
    if decision >= kickoff: return _fail(match_id,'decision_not_before_kickoff')
    evidence_fields = packet.get('feature_evidence')
    if evidence_fields is None or not isinstance(evidence_fields,list):
        return _fail(match_id,'feature_evidence_missing')
    for f in evidence_fields:
        if not isinstance(f,dict): return _fail(match_id,'feature_malformed')
        if str(f.get('name','')).strip().lower() in BANNED_FEATURE_NAMES:
            return _fail(match_id,'outcome_feature_not_allowed')
        ok, reason = _valid_source(f,decision,kickoff)
        if not ok: return _fail(match_id,'feature_'+reason)
        if f.get('value') is None: return _fail(match_id,'feature_missing_value')
    candidates=packet.get('route_candidates') or []
    if not isinstance(candidates,list):return _fail(match_id,'route_candidates_malformed')
    approved=[]
    for c in candidates:
        if not isinstance(c,dict): return _fail(match_id,'route_malformed')
        if c.get('verified') is not True: continue
        if c.get('route') not in ROUTES: continue
        ok,reason=_valid_source(c,decision,kickoff)
        if not ok: return _fail(match_id,'route_'+reason)
        try:p=float(c['p_over15'])
        except (TypeError,ValueError,KeyError):return _fail(match_id,'route_p_invalid')
        if not math.isfinite(p) or not (0<=p<=1):return _fail(match_id,'route_p_invalid')
        approved.append((c['route'],p,c['source_id']))
    policy = packet.get('route_policy')
    if not isinstance(policy,list) or not policy:
        return _fail(match_id,'frozen_route_policy_missing')
    if len(policy)!=len(set(policy)) or any(rt not in ROUTES for rt in policy):
        return _fail(match_id,'route_policy_invalid')
    chosen = next(((route,p,src) for name in policy for route,p,src in approved if name==route),None)
    if chosen is None:return _fail(match_id,'no_valid_legacy_model_output')
    route,p,src=chosen
    edge=None
    odds=packet.get('odds_o15')
    if odds is not None:
        ok, reason = _valid_source(odds,decision,kickoff)
        if not ok:return _fail(match_id,'odds_'+reason)
        try:
            dec=float(odds['decimal'])
            fee=float(packet.get('fees_fraction',0.0))
        except (ValueError,KeyError,TypeError):return _fail(match_id,'odds_or_fee_invalid')
        if dec<=1 or not math.isfinite(dec) or not (0<=fee<1):
            return _fail(match_id,'odds_or_fee_invalid')
        edge=p*dec*(1-fee)-1
    ev={'source_id':src,'decision_at_utc':decision.isoformat(),
        'kickoff_utc':kickoff.isoformat(),'other_sources_validated':len(evidence_fields),
        'route_policy':policy}
    d=deterministic_digest({'match_id':match_id,'p':p,'route':route,'evidence':ev,'roi':edge})
    return Prediction(match_id,'SHADOW','not_certified',route,p,d,edge,ev)


def evaluate(outcomes: Iterable[dict], bins: int=10) -> dict:
    """Evaluate externally-supplied OOS prediction records; never retune them here.

    Each record: match_id, eligible, selected, p_over15, label, optionally odds_o15.
    Histories with missing labels/invalid probabilities fail closed.
    """
    rows=list(outcomes)
    if not rows:raise ValueError('empty_universe')
    if len({r['match_id'] for r in rows})!=len(rows):raise ValueError('duplicate_match_id')
    eligible=[r for r in rows if r.get('eligible') is True]
    if not eligible:raise ValueError('no_eligible_fixtures')
    selected=[r for r in eligible if r.get('selected') is True]
    if not selected: return {'eligible':len(eligible),'selected':0,'coverage':0.0,
                             'hit_rate':None,'brier':None,'logloss':None,
                             'ece':None,'roi_realized':None}
    ps,ys=[],[];net_returns=[]
    for r in selected:
        p=r.get('p_over15'); y=r.get('label')
        if not isinstance(y,int) or isinstance(y,bool) or y not in (0,1):raise ValueError('invalid_label')
        if p is None or not math.isfinite(float(p)) or not 0<=float(p)<=1:raise ValueError('invalid_probability')
        ps.append(float(p));ys.append(y)
        if 'odds_o15' in r:
            o=float(r['odds_o15']);fee=float(r.get('fees_fraction',0.0))
            if o<=1 or not 0<=fee<1:raise ValueError('bad_economic_input')
            net_returns.append(y*o*(1-fee)-1)
    n=len(selected)
    brier=sum((p-y)**2 for p,y in zip(ps,ys))/n
    loss=-sum(y*math.log(max(1e-15,min(1-1e-15,p)))+(1-y)*math.log(max(1e-15,min(1-1e-15,1-p))) for p,y in zip(ps,ys))/n
    ece=0.0
    for i in range(bins):
        group=[(p,y) for p,y in zip(ps,ys) if min(int(p*bins),bins-1)==i]
        if group:ece+=len(group)/n*abs(sum(p for p,y in group)/len(group)-sum(y for p,y in group)/len(group))
    return {'eligible':len(eligible),'selected':n,'coverage':n/len(eligible),
            'hit_rate':sum(ys)/n,'brier':brier,'logloss':loss,'ece':ece,
            'roi_realized':(sum(net_returns)/len(net_returns) if len(net_returns)==n else None),
            'digest':deterministic_digest([{'id':r['match_id'],'p':p,'y':y} for r,p,y in zip(selected,ps,ys)])}


def paired_compare(baseline: Iterable[dict], challenger: Iterable[dict]) -> dict:
    """Strictly paired comparison; no winner if match/selection/label differs.

    Only compares already-frozen outputs for identical selected fixtures.
    Records: match_id, eligible=True, selected=True, label 0/1, p_over15.
    The observed hit rate is identical if both predict only Over1.5 on same
    exact selections; improvements must instead arise via calibration or
    *preregistered* changed selection policy with comparable coverage.
    """
    b = {str(x['match_id']):x for x in baseline}
    c = {str(x['match_id']):x for x in challenger}
    if not b or set(b)!=set(c): raise ValueError('unpaired_match_universe')
    if any(x is None for x in b.values()) or any(x is None for x in c.values()):
        raise ValueError('malformed_record')
    for mid in b:
        left,right=b[mid],c[mid]
        for field in ('eligible','selected','label'):
            if left.get(field)!=right.get(field):
                raise ValueError('different_selection_or_label_contract')
        if left.get('selected') and left.get('eligible'):
            for rec in (left,right):
                if 'kickoff_utc' not in rec or 'prediction_at_utc' not in rec:
                    raise ValueError('missing_timestamp_provenance')
                if parse_dt(rec['prediction_at_utc']) >= parse_dt(rec['kickoff_utc']):
                    raise ValueError('post_kickoff_prediction')
    B=evaluate([b[mid] for mid in sorted(b)])
    C=evaluate([c[mid] for mid in sorted(c)])
    return {'status':'SHADOW_COMPARISON_ONLY',
            'common_matches':len(b),'common_selections':B['selected'],
            'baseline':B,'challenger':C,
            'delta_brier': (C['brier']-B['brier'] if B['brier'] is not None else None),
            'delta_logloss':(C['logloss']-B['logloss'] if B['logloss'] is not None else None),
            'same_selection_means_same_hit_rate':True,
            'not_a_promotion':True}