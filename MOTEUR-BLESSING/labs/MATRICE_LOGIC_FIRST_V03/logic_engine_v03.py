#!/usr/bin/env python3
"""MOTEUR/MATRICE Logic First V0.3: exhaustive R8 evidence routing, no invented IC.

Structural completeness (355/355) is not causal completeness. Every accepted fact is
explicitly checked, classified and traced. Only V0.2 reviewed hypotheses can
activate paths; all unreviewed L3 fields remain process evidence, guards or contexts.
"""
from __future__ import annotations
import argparse
import copy
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
import sys

THIS = Path(__file__).resolve().parent
V02 = THIS.parent / "MATRICE_LOGIC_FIRST_V02"
if str(V02) not in sys.path:
    sys.path.insert(0, str(V02))
import logic_engine_v02 as engine
import registry_builder

VERSION = "MATRICE-LOGIC-FIRST-V0.3-EXHAUSTIVE-EVIDENCE-20261023"
REGISTRY_FILE = THIS / "REGISTRE_R8_355.json"
ROLES = ("SOURCE_OR_DEFINITION_GUARD_REVIEW_REQUIRED",
         "HYPOTHETICAL_CONDITIONAL_CONTEXT_REVIEW_REQUIRED",
         "POTENTIAL_PROCESS_EVIDENCE_REVIEW_REQUIRED")
VALID_CLASSIFICATIONS = ("SOURCE_GUARD", "CONDITIONAL_CONTEXT", "PROCESS_EVIDENCE",
                         "SIGNED_HYPOTHESIS", "SEMANTIC_HOLD")
ROLE_MAP = dict(zip(ROLES, VALID_CLASSIFICATIONS[:3]))

class RegistryError(ValueError):
    pass

def validate_registry(registry: dict[str, Any]) -> dict[str, dict]:
    if registry.get("worlds") != 62 or registry.get("source_documentary_subparameters") != 355:
        raise RegistryError("BAD_R8_COUNTS")
    entries = registry.get("subparameters")
    if not isinstance(entries, list) or len(entries) != 355:
        raise RegistryError("REGISTRY_SIZE")
    ids = {}
    for e in entries:
        cid = e.get("id")
        if not isinstance(cid, str) or cid in ids:
            raise RegistryError("DUPLICATE_OR_INVALID_CHILD")
        if cid.split(".", 1)[0] not in engine.core.CANONICAL_WORLDS:
            raise RegistryError("UNKNOWN_WORLD:" + cid)
        if e.get("world") != cid.split(".", 1)[0]:
            raise RegistryError("WRONG_PARENT:" + cid)
        if e.get("numeric_effect_calibrated") is not False:
            raise RegistryError("FALSE_CALIBRATION:" + cid)
        if e.get("inventory_role_candidate") not in ROLES:
            raise RegistryError("MISSING_REVIEW_ROUTE:" + cid)
        ids[cid] = e
    if len(ids) != 355 or not set(engine.ID_TO_ALIAS).issubset(ids):
        raise RegistryError("MISSING_WIRED_ID")
    if len({e["world"] for e in entries}) != 62:
        raise RegistryError("MISSING_WORLD")
    return ids

def role_for(cid: str, item: dict) -> tuple[str, str]:
    if cid in registry_builder.HELD_ONLY_IDS:
        return "SEMANTIC_HOLD", "D056_SOURCE_SEMANTICS_UNRESOLVED"
    if cid in engine.ID_TO_ALIAS:
        return "SIGNED_HYPOTHESIS", "D055_EXPLICIT_RULE_HYPOTHESIS_NOT_VALIDATED"
    role = ROLE_MAP[item["inventory_role_candidate"]]
    return role, "UNSIGNED_CONTRACT_NOT_ALLOWED_TO_ACTIVATE_GOAL_PATH"

def _validated_facts(case: dict, registry_index: dict) -> dict:
    if not isinstance(case, dict) or not case.get("fixture_id"):
        raise engine.core.InvalidPrematch("FIXTURE_ID_REQUIRED")
    cutoff = engine.core.iso(case["analysis_asof_utc"])
    kickoff = engine.core.iso(case["kickoff_utc"])
    if cutoff >= kickoff:
        raise engine.core.InvalidPrematch("POST_KICKOFF_CUTOFF_REJECTED")
    raw = case.get("facts")
    if not isinstance(raw, dict) or not raw:
        raise engine.core.InvalidPrematch("FACTS_REQUIRED")
    accepted = {}
    for k, v in raw.items():
        if not isinstance(k, str) or "." not in k:
            raise engine.core.InvalidPrematch("INVALID_INPUT_ID")
        side, cid = k.split(".", 1)
        if side not in engine.core.SIDES or cid not in registry_index:
            raise engine.core.InvalidPrematch("UNREGISTERED_L3_CHILD:" + k)
        if not isinstance(v, dict) or v.get("state") not in engine.core.STATES:
            raise engine.core.InvalidPrematch("INVALID_STATE:" + k)
        for required in ("source_id", "source_issued_utc", "source_first_seen_utc", "assessment_status"):
            if not v.get(required):
                raise engine.core.InvalidPrematch("PIT_AND_PROVENANCE_REQUIRED:" + k)
        issued = engine.core.iso(v["source_issued_utc"])
        seen = engine.core.iso(v["source_first_seen_utc"])
        if issued > seen or seen > cutoff:
            raise engine.core.InvalidPrematch("LATE_OR_INCONSISTENT_PROVENANCE:" + k)
        if v["assessment_status"] not in ("DOCUMENTED_SYNTHETIC", "VERIFIED_BEFORE_T0", "HYPOTHESIS_ONLY"):
            raise engine.core.InvalidPrematch("INVALID_ASSESSMENT_STATUS:" + k)
        if v["assessment_status"] == "VERIFIED_BEFORE_T0" and v.get("original_publisher_verified") is not True:
            raise engine.core.InvalidPrematch("VERIFIED_LABEL_WITHOUT_PUBLISHER_PROOF:" + k)
        if v.get("target_match_inplay") is True or v.get("target_match_final") is True:
            raise engine.core.InvalidPrematch("TARGET_MATCH_FUTURE_LEAK:" + k)
        accepted[k] = v
    return accepted

def analyze(case: dict, registry: dict) -> dict:
    catalog = validate_registry(registry)
    accepted = _validated_facts(case, catalog)
    wired = {k: v for k, v in accepted.items() if k.split(".", 1)[1] in engine.ID_TO_ALIAS}
    original = {**case, "facts": wired}
    # Core V0.2 cannot evaluate an empty payload. Explicit conservative abstention.
    prior = engine.analyze(original) if wired else None
    ledger = []
    counts = Counter()
    for key in sorted(accepted):
        side, cid = key.split(".", 1)
        meta = catalog[cid]
        role, caveat = role_for(cid, meta)
        fact = accepted[key]
        counts[role] += 1
        ledger.append({
            "input": key, "world": meta["world"], "role": role,
            "state": fact["state"], "source_id": fact["source_id"],
            "source_first_seen_utc": fact["source_first_seen_utc"],
            "assessment_status": fact["assessment_status"],
            "status": "UNKNOWN_NO_IMPUTATION" if fact["state"] == "UNKNOWN" else
                      "QUALITATIVE_OBSERVATION_NOT_NUMERIC_EFFECT",
            "mechanism_or_guard": caveat, "rule_ids": (prior or {}).get("audit_input_roles", {}).get(key, []),
            "candidate_not_semantically_signed": meta["role_review_status"] == "MACHINE_PROVISIONAL_NOT_SEMANTICALLY_SIGNED"
        })
    assert len(ledger) == len(accepted)
    distinct = sorted({x["world"] for x in ledger})
    if prior is None:
        outcome = "ABSTAIN_NO_SIGNED_HYPOTHESES_PROVIDED"
        teams = {}
        branches = []
        rules = []
    else:
        outcome = prior["logical_issue"]
        teams = prior["teams"]
        branches = prior["compatible_future_score_states"]
        rules = prior["rules"]
    result = {
        "engine": VERSION, "fixture_id": case["fixture_id"],
        "analysis_asof_utc": case["analysis_asof_utc"],
        "kickoff_utc": case["kickoff_utc"],
        "registered_L3": 355, "canonical_worlds": 62,
        "registered_unexamined_semantic_contracts": 355,
        "software_route_coverage": "355/355",
        "fact_count_supplied": len(accepted),
        "fact_count_evaluated": len(ledger),
        "worlds_with_submitted_facts": distinct,
        "role_counts": dict(counts),
        "input_evidence_ledger": ledger,
        "path_hypotheses": rules,
        "teams": teams, "logical_issue": outcome,
        "exclusive_future_score_states": branches,
        "numeric_IC_theoretical_percent": None,
        "numeric_IC_calibrated_percent": None,
        "mechanistically_proven_goals": 0,
        "source_proven_causal_effects": 0,
        "full_355_executable_causal_effects_claimed": False,
        "structural_completion_is_not_predictive_validation": True,
        "warning": "Documentary source fields and unsigned hypotheses cannot produce numeric Over1.5 probabilities.",
    }
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("fixture", type=Path)
    p.add_argument("--registry", type=Path, default=REGISTRY_FILE)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = analyze(json.loads(args.fixture.read_text(encoding="utf-8")),
                     json.loads(args.registry.read_text(encoding="utf-8")))
    result_string = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(result_string, encoding="utf-8")
    else:
        print(result_string, end="")

if __name__ == "__main__":
    main()
