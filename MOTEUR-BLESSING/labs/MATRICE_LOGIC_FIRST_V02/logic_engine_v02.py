#!/usr/bin/env python3
"""MATRICE logic-first V0.2, first coupled mechanism lot; no numeric IC.

Extends the immutable V0.1 engine, with verified authentic R8 L3 identifiers.
Every supplied fact must have provenance and at least one auditable role.
"""
from __future__ import annotations
import argparse
import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import base_v01 as core

ENGINE_VERSION = "MATRICE-LOGIC-FIRST-V0.2-LOT01-20261023"
# Entries are not statistically calibrated. HIGH and LOW are explicitly
# HYPOTHETICAL semantic assessments of an observable historical capability.
EXTRA = {
    "SPACE": "TRANSITION_ATTACK.VERTICAL_SPACE_EXPLOITATION",
    "DELAY": "TRANSITION_DEFENSE.FIRST_DELAY_ACTION",
    "RECOVER": "TRANSITION_DEFENSE.RECOVERY_RUN_STRUCTURE",
    "LINEPASS": "PASSING_COMBINATIONS.LINE_BREAK_PASS",
    "BOXENTRY": "FINAL_THIRD_ACCESS.BOX_ENTRY_CONDITIONAL",
    "OFFBALL": "OFF_BALL_MOVEMENT.RUN_BEHIND_DEFENSE",
    "CENTRALGUARD": "DEFENCE_STRUCTURE.CENTRAL_LANE_ASSIGNMENT",
    "CROSS": "WIDE_AERIAL_ATTACK.OPEN_PLAY_CROSS",
    "AERIAL": "WIDE_AERIAL_ATTACK.AERIAL_CONTEST_CONTEXT",
    "AERIALDEF": "ONE_V_ONE_DUELS.AERIAL_PRIMARY",
    "MARKING": "DEFENCE_STRUCTURE.OPEN_PLAY_MARKING",
    "CLEARANCE": "SECOND_BALL_RECOVERY.CLEARANCE_SECOND",
    "REBOUND": "SECOND_BALL_RECOVERY.SETPIECE_REBOUND",
    "SHIFT": "DEFENCE_STRUCTURE.LINE_SHIFT_COORDINATION",
    "MISTAKE": "UNFORCED_MISTAKE_RISK.PASS_MISCONTROL",
    "SCOREMAP": "GAME_STATE_POLICY.CONDITIONAL_SCORE_STATE_MAP",
    "BENCH": "SUBSTITUTION_IMPACT.ELIGIBLE_BENCH_ASOF",
}
assert len(EXTRA) == len(set(EXTRA.values())) == 17
ALL_FIELDS = {k: v[0] for k, v in core.FIELDS.items()} | EXTRA
ID_TO_ALIAS = {v:k for k,v in ALL_FIELDS.items()}
assert len(ID_TO_ALIAS) == len(ALL_FIELDS) == 31
assert len(core.FIELDS) == 14
assert all(p.split(".")[0] in core.CANONICAL_WORLDS for p in ID_TO_ALIAS)

@dataclass(frozen=True)
class Hypothesis:
    code: str
    route: str
    group: str
    criteria: tuple[tuple[str,str,str],...]
    role: str = "POTENTIAL_CHANCE_PATH"  # not actual goals

NEW_RULES = (
    Hypothesis("R-CENTRAL-02", "CENTRAL_ACCESS", "SETTLED_OPEN_PLAY", (
        ("self","LINEPASS","HIGH"),("self","BOXENTRY","HIGH"),
        ("self","OFFBALL","HIGH"),("opp","CENTRALGUARD","LOW"))),
    Hypothesis("R-WIDE-02", "WIDE_AERIAL", "SETTLED_OPEN_PLAY", (
        ("self","CROSS","HIGH"),("self","AERIAL","HIGH"),
        ("opp","AERIALDEF","LOW"),("opp","MARKING","LOW"))),
    Hypothesis("R-SECOND-02", "SECOND_PHASE", "SET_PIECE_CHAIN", (
        ("self","CLEARANCE","HIGH"),("self","REBOUND","HIGH"),
        ("opp","SHIFT","LOW"))),
    Hypothesis("R-PRESS-ERROR-02", "PRESSURE_ERROR_CONTEXT", "HIGH_REGAIN", (
        ("opp","MISTAKE","HIGH"),("self","PRESS","HIGH")), "CONTEXT_NOT_INDEPENDENT_PATH"),
    Hypothesis("R-TRAIL-BENCH-02", "LATER_TRAILING_REACTION", "FUTURE_HYPOTHETICAL", (
        ("self","SCOREMAP","HIGH"),("self","BENCH","HIGH"),
        ("self","TRAIL_RESPONSE","HIGH")), "FUTURE_CONDITIONAL_NOT_A_GOAL_PATH"),
    Hypothesis("R-COUNTER-CHECK-02", "COUNTER_ANTAGONISTIC_CONTEXT", "TRANSITION", (
        ("self","SPACE","HIGH"),("opp","DELAY","LOW"),
        ("opp","RECOVER","LOW")), "CONTESTING_GUARD_NOT_INDEPENDENT_PATH"),
)
assert {key for r in NEW_RULES for _,key,_ in r.criteria if key in EXTRA} == set(EXTRA)

LEGACY_GROUPS = {"HIGH_REGAIN":"HIGH_REGAIN", "COUNTER":"TRANSITION",
                 "POSITIONAL":"SETTLED_OPEN_PLAY", "SET_PIECE":"SET_PIECE_CHAIN"}

# D056: source-contract semantic holds; do not turn documentary event
# definitions into directional sporting advantages without a valid scale.
SEMANTIC_HOLDS = {
    "R-WIDE-02": "AERIAL_CONTEST_CONTEXT and AERIAL_PRIMARY attest event/opposition; HIGH/LOW do not establish aerial superiority",
    "R-SECOND-02": "CLEARANCE_SECOND and SETPIECE_REBOUND need common incident lineage and team ownership before forming an independent second-phase path",
    "R-PRESS-ERROR-02": "PASS_MISCONTROL is specifically unforced; it must not be relabeled as an error caused by opponent pressing",
    "R-TRAIL-BENCH-02": "CONDITIONAL_SCORE_STATE_MAP and ELIGIBLE_BENCH_ASOF are structural/eligibility contracts, not ordinal HIGH skill measures",
}


def _validate_all(case: dict[str,Any]) -> dict[str,Any]:
    if not isinstance(case,dict) or not case.get("fixture_id"):
        raise core.InvalidPrematch("FIXTURE_ID_REQUIRED")
    cutoff=core.iso(case["analysis_asof_utc"])
    kickoff=core.iso(case["kickoff_utc"])
    if cutoff >= kickoff:
        raise core.InvalidPrematch("POST_KICKOFF_CUTOFF_REJECTED")
    raw=case.get("facts")
    if not isinstance(raw,dict) or not raw:
        raise core.InvalidPrematch("FACTS_REQUIRED")
    accepted={}
    for key, fact in raw.items():
        if not isinstance(key,str) or "." not in key:
            raise core.InvalidPrematch("INVALID_KEY:"+str(key))
        side, child=key.split(".",1)
        if side not in core.SIDES or child not in ID_TO_ALIAS:
            raise core.InvalidPrematch("UNMAPPED_L3_CHILD_REJECTED:"+key)
        if not isinstance(fact,dict) or fact.get("state") not in core.STATES:
            raise core.InvalidPrematch("INVALID_FACT_STATE:"+key)
        required=("source_id","source_issued_utc","source_first_seen_utc","assessment_status")
        if any(not fact.get(x) for x in required):
            raise core.InvalidPrematch("PIT_AND_PROVENANCE_REQUIRED:"+key)
        issued=core.iso(fact["source_issued_utc"])
        seen=core.iso(fact["source_first_seen_utc"])
        if issued > seen or seen > cutoff:
            raise core.InvalidPrematch("LATE_OR_INCONSISTENT_PROVENANCE:"+key)
        if fact["assessment_status"] not in ("DOCUMENTED_SYNTHETIC","VERIFIED_BEFORE_T0","HYPOTHESIS_ONLY"):
            raise core.InvalidPrematch("INVALID_ASSESSMENT_STATUS:"+key)
        if fact["assessment_status"] == "VERIFIED_BEFORE_T0" and fact.get("original_publisher_verified") is not True:
            raise core.InvalidPrematch("VERIFIED_LABEL_WITHOUT_PUBLISHER_PROOF:"+key)
        if fact.get("target_match_inplay") is True or fact.get("target_match_final") is True:
            raise core.InvalidPrematch("TARGET_MATCH_FUTURE_LEAK:"+key)
        accepted[key] = {**fact,"team":side,"child_id":child,"alias":ID_TO_ALIAS[child]}
    # Compatibility audit: V0.1 validation must accept precisely its own subset.
    prior={k:v for k,v in raw.items() if k.split(".",1)[1] in core.FIELD_TO_ALIAS}
    if prior:
        prior_case={**case,"facts":prior}
        core.validate(prior_case)
    return accepted


def _evaluate(rule:Hypothesis, side:str, facts:dict[str,Any])->dict[str,Any]:
    opposing="B" if side=="A" else "A"
    evidence=[]
    for role,alias,expected in rule.criteria:
        k=(side if role=="self" else opposing)+"."+ALL_FIELDS[alias]
        f=facts.get(k)
        actual=f["state"] if f else "UNKNOWN"
        status="UNKNOWN" if actual=="UNKNOWN" else "MATCH" if actual==expected else "CONTRADICTED"
        evidence.append({"input":k,"expected":expected,"actual":actual,"evaluation":status,
                         "source_id":f["source_id"] if f else None})
    if any(e["evaluation"]=="CONTRADICTED" for e in evidence):
        status="NOT_SUPPORTED_BY_PRESENT_INPUTS"
    elif any(e["evaluation"]=="UNKNOWN" for e in evidence):
        status="UNKNOWN_NEEDS_INPUTS"
    else:status="LOGICALLY_ENABLED_CONDITIONAL_PATH"
    return {"rule_id":rule.code,"team":side,"route":rule.route,"dependency_group":rule.group,
            "logical_role":rule.role,"status":status,"prematch_facts":evidence}


def analyze(case:dict[str,Any])->dict[str,Any]:
    facts=_validate_all(case)
    # Keep all seven existing hypotheses, unchanged, rather than replacing V0.1.
    legacy=[core.rule_evidence(rule,side,facts) for side in core.SIDES for rule in core.RULES]
    for r in legacy:
        r["dependency_group"]=LEGACY_GROUPS.get(r["route"],"NONPRIMARY_LEGACY_CONTEXT")
        r["logical_role"]="POTENTIAL_CHANCE_PATH" if r["route"] in LEGACY_GROUPS else "NONINDEPENDENT_MODIFIER"
    new=[_evaluate(rule,side,facts) for side in core.SIDES for rule in NEW_RULES]
    # Fail closed on semantically unsigned mechanisms while preserving full trace.
    for r in new:
        if r["rule_id"] in SEMANTIC_HOLDS:
            r["pre_semantic_hold_status"]=r["status"]
            r["status"]="SEMANTIC_HOLD_REVIEW_REQUIRED"
            r["semantic_hold_reason"]=SEMANTIC_HOLDS[r["rule_id"]]
            r["logical_role"]="SOURCE_CONTRACT_GUARD_UNTIL_DIRECTION_VALIDATED"
    # Strong recover/delay evidence contests a counter; it cannot prove it impossible.
    for side in core.SIDES:
        counter=next(r for r in legacy if r["team"]==side and r["route"]=="COUNTER")
        guard=next(r for r in new if r["team"]==side and r["route"]=="COUNTER_ANTAGONISTIC_CONTEXT")
        contradictory=[x["input"] for x in guard["prematch_facts"] if x["evaluation"]=="CONTRADICTED"]
        counter["antagonistic_inputs"] = contradictory
        if contradictory and counter["status"]=="LOGICALLY_ENABLED_CONDITIONAL_PATH":
            counter["status"]="CONTESTED_BY_ANTAGONISTIC_CONTEXT"
    trace=legacy+new
    all_consumed={e["input"] for r in trace for e in r["prematch_facts"]}
    if not set(facts).issubset(all_consumed):
        raise AssertionError("SILENTLY_IGNORED_INPUT:"+str(set(facts)-all_consumed))
    primary=LEGACY_GROUPS | {"CENTRAL_ACCESS":"SETTLED_OPEN_PLAY",
                             "WIDE_AERIAL":"SETTLED_OPEN_PLAY","SECOND_PHASE":"SET_PIECE_CHAIN"}
    teams={}
    for side in core.SIDES:
        side_rules=[r for r in trace if r["team"]==side]
        enabled=[r for r in side_rules if r["status"]=="LOGICALLY_ENABLED_CONDITIONAL_PATH"
                 and r["route"] in primary]
        groups=sorted({primary[r["route"]] for r in enabled})
        contested=[r["route"] for r in side_rules if r["status"]=="CONTESTED_BY_ANTAGONISTIC_CONTEXT"]
        teams[side]={"enabled_routes":[r["route"] for r in enabled],"independent_pathway_groups":groups,
                     "contested_routes":contested,"goals_guaranteed":False}
    n=sum(len(x["independent_pathway_groups"]) for x in teams.values())
    if n>=2: logical="MULTIPLE_DISTINCT_MECHANISM_GROUPS_PLAUSIBLE_NOT_GOALS"
    elif n==1: logical="ONE_MECHANISM_GROUP_PLAUSIBLE_NOT_GOAL"
    elif any(r["status"]=="UNKNOWN_NEEDS_INPUTS" and r["route"] in primary for r in trace):
        logical="INDETERMINATE_MISSING_CRITICAL_VALUES"
    else:logical="NO_ENABLED_PATHWAY_NOT_UNDER15_PREDICTION"
    future=[]
    for state in ("TIED_AT_HYPOTHETICAL_LATER_TIME","A_TRAILS_AT_HYPOTHETICAL_LATER_TIME", "B_TRAILS_AT_HYPOTHETICAL_LATER_TIME"):
        trailing="A" if state.startswith("A_TRAILS") else "B" if state.startswith("B_TRAILS") else None
        future.append({"exclusive_future_score_state":state,"observed_before_kickoff":False,
                       "conditional_team":trailing,
                       "bench_policy_enabled":any(x["route"]=="LATER_TRAILING_REACTION" and x["team"]==trailing and x["status"]=="LOGICALLY_ENABLED_CONDITIONAL_PATH" for x in new) if trailing else False,
                       "joint_probability":None,"goal_count_inferred":None})
    return {
        "engine":ENGINE_VERSION,"fixture_id":case["fixture_id"],"analysis_asof_utc":case["analysis_asof_utc"],
        "kickoff_utc":case["kickoff_utc"],"worlds_canonical":62,"l3_documented":355,
        "active_l3_identifiers":31,"l3_still_not_executable":324,
        "new_l3_identifiers":sorted(EXTRA.values()),"facts_supplied":len(facts),
        "facts_consumed":len(facts),"audit_input_roles":{k:[r["rule_id"] for r in trace if any(e["input"]==k for e in r["prematch_facts"])] for k in facts},
        "rules":trace,"teams":teams,"logical_issue":logical,
        "compatible_future_score_states":future,
        "numeric_IC_theoretical_under_hypotheses":None,"numeric_IC_calibrated":None,
        "numeric_IC_reason":"No justified joint scenario frequencies or calibrated goal production laws",
        "independent_goal_events_proven":0,
        "evidence_scope":"HYPOTHETICAL_LOGIC_ONLY_NOT_REAL_SPORT_VALIDATION",
        "double_count_policy":"group by shot-generation origin; modifiers and hypothetical future branches excluded from independent groups"
    }


def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("case",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    payload=json.loads(args.case.read_text(encoding="utf-8"))
    result=analyze(payload)
    data=json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n"
    if args.output:args.output.write_text(data,encoding="utf-8")
    else:print(data,end="")

if __name__=="__main__":main()
