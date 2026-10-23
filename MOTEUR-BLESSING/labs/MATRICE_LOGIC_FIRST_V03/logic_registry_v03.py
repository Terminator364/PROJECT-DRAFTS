#!/usr/bin/env python3
"""MATRICE Logic-First V0.3: exhaustive evidence contract, not 355 learned effects.

Consumes the exact V22 355-ID registry with two-team PIT semantics and delegates
only signed experimental hypotheses to V0.2. UNKNOWN never becomes zero.
"""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from typing import Any
import logic_engine_v02 as v02

ROLES={
    "SOURCE_OR_DEFINITION_GUARD_REVIEW_REQUIRED":"SOURCE_GUARD",
    "HYPOTHETICAL_CONDITIONAL_CONTEXT_REVIEW_REQUIRED":"CONDITIONAL_CONTEXT",
    "POTENTIAL_PROCESS_EVIDENCE_REVIEW_REQUIRED":"PROCESS_CANDIDATE",
}
SCHEMA="MATRICE_LOGIC_FIRST_V03_EVIDENCE_GRAPH_NOT_SPORTS_PROBABILITY"

def validate_registry(registry:dict[str,Any])->dict[str,dict[str,Any]]:
    rows=registry.get("subparameters", [])
    if registry.get("worlds")!=62 or registry.get("source_documentary_subparameters")!=355 or len(rows)!=355:
        raise ValueError("SOURCE_REGISTRY_62_355_REQUIRED")
    ids={r["id"] for r in rows}
    if len(ids)!=355:raise ValueError("DUPLICATE_REGISTERED_CHILD")
    if set(v02.ID_TO_ALIAS)-ids:raise ValueError("EXECUTABLE_CHILD_NOT_PRESENT_IN_SOURCE")
    if {r["world"] for r in rows}!=set(v02.core.CANONICAL_WORLDS):
        raise ValueError("WRONG_OR_MISSING_WORLD")
    for r in rows:
        if not r["id"].startswith(r["world"]+"."):
            raise ValueError("WRONG_CHILD_PARENT")
        if r["inventory_role_candidate"] not in ROLES:
            raise ValueError("UNREVIEWED_ROLE_FORMAT")
        if r.get("numeric_effect_calibrated") is not False:
            raise ValueError("UNEXPECTED_NUMERIC_EFFECT")
    return {r["id"]:r for r in rows}

def analyze(case:dict[str,Any],registry:dict[str,Any])->dict[str,Any]:
    all_ids=validate_registry(registry)
    if not isinstance(case,dict) or not case.get("fixture_id"):
        raise v02.core.InvalidPrematch("FIXTURE_ID_REQUIRED")
    cutoff=v02.core.iso(case["analysis_asof_utc"])
    kick=v02.core.iso(case["kickoff_utc"])
    if cutoff>=kick:raise v02.core.InvalidPrematch("POST_KICKOFF_CUTOFF_REJECTED")
    facts=case.get("facts")
    if not isinstance(facts,dict):raise v02.core.InvalidPrematch("FACTS_OBJECT_REQUIRED")
    active={}
    source_guard=[]
    per_child={}
    shared=defaultdict(list)
    for key,fact in facts.items():
        if not isinstance(key,str) or "." not in key:
            raise v02.core.InvalidPrematch("INVALID_FACT_KEY")
        side,child=key.split(".",1)
        if side not in v02.core.SIDES or child not in all_ids:
            raise v02.core.InvalidPrematch("UNMAPPED_L3_CHILD_REJECTED:"+str(key))
        if not isinstance(fact,dict) or fact.get("state") not in v02.core.STATES:
            raise v02.core.InvalidPrematch("INVALID_FACT_STATE:"+key)
        required=("source_id","source_issued_utc","source_first_seen_utc","assessment_status")
        if any(not fact.get(k) for k in required):
            raise v02.core.InvalidPrematch("PIT_AND_PROVENANCE_REQUIRED:"+key)
        issued=v02.core.iso(fact["source_issued_utc"])
        first=v02.core.iso(fact["source_first_seen_utc"])
        if issued>first or first>cutoff:
            raise v02.core.InvalidPrematch("LATE_OR_INCONSISTENT_PROVENANCE:"+key)
        if fact["assessment_status"] not in ("DOCUMENTED_SYNTHETIC","HYPOTHESIS_ONLY","VERIFIED_BEFORE_T0"):
            raise v02.core.InvalidPrematch("INVALID_ASSESSMENT_STATUS:"+key)
        if fact["assessment_status"]=="VERIFIED_BEFORE_T0" and fact.get("original_publisher_verified") is not True:
            raise v02.core.InvalidPrematch("VERIFIED_WITHOUT_PUBLISHER_PROOF:"+key)
        if fact.get("target_match_final") is True or fact.get("target_match_inplay") is True:
            raise v02.core.InvalidPrematch("FUTURE_TARGET_LEAK:"+key)
        row=all_ids[child]
        contract_state=row["code_wiring"]
        status=("SEMANTIC_HOLD_NOT_SCORABLE" if contract_state=="TRACEABLE_SEMANTIC_HOLD_ONLY"
                else "SIGNED_EXPERIMENTAL_LOGIC" if child in v02.ID_TO_ALIAS
                else "PIT_EVIDENCE_ONLY_UNCALIBRATED")
        per_child[key]={"source_contract":row.get("source_contract"),
             "world":row["world"],"role_candidate":ROLES[row["inventory_role_candidate"]],
             "candidate_role_requires_semantic_review":True,
             "state":fact["state"],"status":status,"owner":row.get("declared_evidence_owner"),
             "source_id":fact["source_id"]}
        if status=="SIGNED_EXPERIMENTAL_LOGIC" or status=="SEMANTIC_HOLD_NOT_SCORABLE":
            active[key]=fact
        if ROLES[row["inventory_role_candidate"]]=="SOURCE_GUARD":
            source_guard.append(key)
        incident=fact.get("historic_incident_key")
        if incident is not None:
            if not isinstance(incident,str) or not incident.strip():
                raise v02.core.InvalidPrematch("INVALID_INCIDENT_ID:"+key)
            shared[(side,incident)].append(key)
    for (side,incident),keys in shared.items():
        if len(keys)>1:
            for key in keys:
                per_child[key]["shared_historic_incident"]=True
                per_child[key]["independent_event_contribution"]="NOT_PROVEN_SHARED_INCIDENT"
    counts=Counter(ROLES[r["inventory_role_candidate"]] for r in all_ids.values())
    # Full two-team symbolic graph: even omitted slots are UNKNOWN, never zero.
    world_counts={w:{"documented":0,"A_supplied":0,"B_supplied":0} for w in v02.core.CANONICAL_WORLDS}
    for c in all_ids.values():world_counts[c["world"]]["documented"]+=1
    for k,record in per_child.items():world_counts[record["world"]][k[0]+"_supplied"]+=1
    logic=v02.analyze({**case,"facts":active}) if active else None
    return {"schema":SCHEMA,"fixture_id":case["fixture_id"],
        "source_worlds":62,"source_children":355,"two_team_evidence_slots":710,
        "supplied_slots":len(per_child),"unknown_or_unsupplied_slots":710-len(per_child),
        "registered_slots":len(all_ids),"prestart_source_guard_inputs":source_guard,
        "candidate_roles":dict(counts),"world_coverage":world_counts,
        "source_contract_routes":per_child,
        "shared_incident_groups":[{"team":side,"incident":inc,"ids":keys}
                   for (side,inc),keys in sorted(shared.items()) if len(keys)>1],
        "legacy_v02_logic":logic,
        "logic_scope":"V02_RULES_ONLY_REMAINDER_DOCUMENTARY_NO_UNSIGNED_CAUSAL_INFERENCE",
        "numeric_IC_theoretical_under_hypotheses":None,
        "numeric_IC_calibrated":None,
        "no_unsupported_probabilities":True,
        "registry_coverage_complete":True,
        "scientific_sporting_validation":False}

if __name__=="__main__":
    import argparse
    from pathlib import Path
    ap=argparse.ArgumentParser()
    ap.add_argument("--registry",required=True,type=Path)
    ap.add_argument("--case",required=True,type=Path)
    ap.add_argument("--out",type=Path)
    a=ap.parse_args()
    out=analyze(json.loads(a.case.read_text(encoding="utf-8")),
                json.loads(a.registry.read_text(encoding="utf-8")))
    value=json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if a.out:a.out.write_text(value,encoding="utf-8")
    else:print(value,end="")
