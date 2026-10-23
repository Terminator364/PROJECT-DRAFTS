#!/usr/bin/env python3
"""D063: independent projected-shot Poisson-binomial pathway for Over1.5.

Unlike an arbitrary score bonus per R8 child, this model uses a transparent
chance -> conversion -> goal process: each *projected* hypothetical shot has a
conditional probability of conversion. It does not forecast number/quality of
shots from documentary parameters. All outputs are uncalibrated conditional
hypotheses. Do not treat constructed shots as actual target-match observations.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
from typing import Any
from theoretical_ic_v08 import UnjustifiedIC

SCHEMA="MOTEUR_D063_PROJECTED_SHOTS_POISSON_BINOMIAL_THEORETICAL_ONLY"
ALLOWED_TYPES=frozenset(("OPEN_PLAY","SET_PIECE","PENALTY","OWN_GOAL_RISK"))
MAX_SLOTS_PER_TEAM=150

def _p(x:Any)->float:
    if isinstance(x,bool) or not isinstance(x,(float,int)):
        raise UnjustifiedIC("SHOT_PROJECTION_P_MUST_BE_NUMERIC")
    val=float(x)
    if not math.isfinite(val) or not 0<=val<=1:
        raise UnjustifiedIC("SHOT_PROJECTION_PROBABILITY_OUT_OF_RANGE")
    return val

def first_two_masses(probabilities:list[float])->tuple[float,float]:
    """Exactly P(total=0), P(total=1) via a stable dynamic-programming recursion."""
    p0,p1=1.0,0.0
    for item in probabilities:
        p=_p(item)
        p1=p1*(1-p)+p0*p
        p0=p0*(1-p)
    return p0,p1

def calculate(case:dict[str,Any],proposal:dict[str,Any],
              source_graph:dict[str,Any]|None=None)->dict[str,Any]:
    from logic_engine_v02 import core
    if not isinstance(case,dict) or not case.get("fixture_id"):
        raise UnjustifiedIC("FIXTURE_ID_REQUIRED")
    try:
        cutoff=core.iso(case["analysis_asof_utc"])
        kickoff=core.iso(case["kickoff_utc"])
    except (KeyError,ValueError) as e:
        raise UnjustifiedIC("CUTOFF_KICKOFF_UTC_REQUIRED") from e
    if cutoff>=kickoff:raise UnjustifiedIC("CUTOFF_NOT_PREMATCH")
    if not isinstance(proposal,dict) or proposal.get("projection_kind")!="HYPOTHETICAL_PRET0_SHOT_EVENTS":
        raise UnjustifiedIC("PROJECTIONS_MUST_BE_LABELED_HYPOTHETICAL")
    if proposal.get("target_match_shots_observed") is True or proposal.get("empirically_calibrated") is True:
        raise UnjustifiedIC("NO_INPLAY_SHOTS_OR_FAKE_CALIBRATION")
    if proposal.get("projection_declared_at_utc") is None:
        raise UnjustifiedIC("PROJECTION_TIMESTAMP_REQUIRED")
    try:declared=core.iso(proposal["projection_declared_at_utc"])
    except ValueError as exc:raise UnjustifiedIC("PROJECTION_TIMESTAMP_INVALID") from exc
    if declared>cutoff:raise UnjustifiedIC("PROJECTION_CREATED_AFTER_ANALYSIS_CUTOFF")
    if source_graph is not None:
        if source_graph.get("worlds")!=62 or source_graph.get("documentary_subparameters")!=355:
            raise UnjustifiedIC("CANONICAL_355_SOURCE_GRAPH_REQUIRED")
        registered={item["id"] for item in source_graph["nodes"]}
        if len(registered)!=355:raise UnjustifiedIC("CANONICAL_355_SOURCE_GRAPH_REQUIRED")
    else:
        registered=None
    rows={}
    ids=set()
    all_p=[]
    for side in ("A","B"):
        projections=proposal.get("shots_"+side)
        if not isinstance(projections,list) or len(projections)>MAX_SLOTS_PER_TEAM:
            raise UnjustifiedIC("PROJECTED_EVENTS_LIST_MISSING_OR_OVERSIZED:"+side)
        details=[]
        for raw in projections:
            if not isinstance(raw,dict) or not isinstance(raw.get("shot_slot_id"),str) or not raw["shot_slot_id"].strip():
                raise UnjustifiedIC("UNIQUE_SHOT_SLOT_REQUIRED")
            slot=raw["shot_slot_id"]
            if slot in ids:raise UnjustifiedIC("DUPLICATE_SHARED_SHOT_SLOT:"+slot)
            ids.add(slot)
            if raw.get("event_type") not in ALLOWED_TYPES:
                raise UnjustifiedIC("UNCLASSIFIED_PROJECTED_EVENT:"+slot)
            if raw.get("observed_in_target_match") is True or raw.get("is_actual_match_shot") is True:
                raise UnjustifiedIC("FUTURE_TARGET_SHOT_LEAK:"+slot)
            prob=_p(raw.get("p_goal_if_projected_event"))
            if raw.get("p_goal_empirically_calibrated") is True:
                raise UnjustifiedIC("UNSUPPORTED_CALIBRATION_CLAIM:"+slot)
            refs=raw.get("source_child_context_ids",[])
            if not isinstance(refs,list) or not all(isinstance(k,str) for k in refs):
                raise UnjustifiedIC("INVALID_R8_CONTEXT_REFERENCE_LIST")
            if len(refs)!=len(set(refs)):raise UnjustifiedIC("DUPLICATE_R8_CONTEXT_REFERENCE")
            if registered is not None and not set(refs).issubset(registered):
                raise UnjustifiedIC("UNREGISTERED_SOURCE_CHILD_REFERENCE")
            details.append({"slot":slot,"class":raw["event_type"],
                           "p_goal_conditional_assumption":prob,
                           "source_child_context_ids":refs,
                           "source_child_context_not_a_weight":True})
            all_p.append(prob)
        p0,p1=first_two_masses([x["p_goal_conditional_assumption"] for x in details])
        rows[side]={"assumed_projected_shot_events":len(details),
                    "expected_goals_conditional_assumption":sum(x["p_goal_conditional_assumption"] for x in details),
                    "P_zero_goals_conditional":p0,"P_one_goal_conditional":p1,
                    "slots":details}
    z,o=first_two_masses(all_p)
    total=max(0.0,min(1.0,1-z-o))
    return {"schema":SCHEMA,"fixture_id":case["fixture_id"],
            "preT0_cutoff":case["analysis_asof_utc"],
            "shot_event_count_assumed":len(all_p),
            "teams":rows,
            "P_0_goals_conditional":z,"P_exactly_1_goal_conditional":o,
            "IC_over15_theoretical_percent":100*total,
            "IC_over15_empirically_calibrated_percent":None,
            "real_match_predictive_accuracy_percent":None,
            "real_goal_count_observed":None,
            "all_R8_children_used_to_estimate_conversion_probabilities":False,
            "source_graph_context_verified":source_graph is not None,
            "independence_assumption":"ALL_PROJECTED_SHOT_CONVERSIONS_CONDITIONALLY_INDEPENDENT",
            "model_limits":"PROJECTED_EVENT_COUNT_AND_PER_EVENT_CONVERSION_ARE_SUPPLIED_HYPOTHESES_NOT_FORECASTS",
            "status":"LAB_CONDITIONAL_SHOT_PROCESS_NOT_A_VALIDATED_MATCH_IC"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--case",type=Path,required=True)
    p.add_argument("--proposal",type=Path,required=True)
    p.add_argument("--source-graph",type=Path)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=calculate(json.loads(a.case.read_text(encoding="utf8")),
                     json.loads(a.proposal.read_text(encoding="utf8")),
                     json.loads(a.source_graph.read_text(encoding="utf8")) if a.source_graph else None)
    a.out.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"shots":result["shot_event_count_assumed"],
                      "IC_conditional":result["IC_over15_theoretical_percent"],
                      "IC_calibrated":None}))
if __name__=="__main__":main()
