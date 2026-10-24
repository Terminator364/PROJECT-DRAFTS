#!/usr/bin/env python3
"""D071 strict true-original R8 one-command integration gate.

DO NOT use fixture output as a real sporting prediction. Source-authorized
355 original private R8 children are checked and built by moteur_unique_v1.
This fails closed on source drift, a missing archival member, a made-up weight,
or an incomplete output/hash manifest. The lab fixture is wholly synthetic.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import traceback
import moteur_unique_v1 as m

FIXTURE = {
    "fixture_id": "D071_PURELY_SYNTHETIC_AUDIT_ONLY",
    "analysis_asof_utc": "2026-10-22T12:00:00Z",
    "kickoff_utc": "2026-10-23T19:00:00Z",
    "facts": {}
}
RATES = {
    "source_kind": "SYNTHETIC_ASSUMPTION_ONLY",
    "declared_at_utc": "2026-10-22T11:00:00Z",
    "lambda_A": 1.1, "lambda_B": 0.9
}
SHOTS = {
    "projection_kind": "HYPOTHETICAL_PRET0_SHOT_EVENTS",
    "projection_declared_at_utc": "2026-10-22T11:00:00Z",
    "shots_A": [
        {"shot_slot_id":"A-1","event_type":"OPEN_PLAY",
         "p_goal_if_projected_event":0.2},
        {"shot_slot_id":"A-2","event_type":"SET_PIECE",
         "p_goal_if_projected_event":0.3}
    ],
    "shots_B": [
        {"shot_slot_id":"B-1","event_type":"OPEN_PLAY",
         "p_goal_if_projected_event":0.1},
        {"shot_slot_id":"B-2","event_type":"PENALTY",
         "p_goal_if_projected_event":0.25}
    ]
}

class IntegrationGateFailed(RuntimeError): pass

def demand(ok:bool,reason:str):
    if not ok:
        raise IntegrationGateFailed(reason)

def verify_original_355(result:dict)->dict:
    summary=result["summary"]
    semantic=result["semantics"]
    graph=result["source_graph"]
    stages=result["conceptual_stages"]
    dos=result["dossiers"]
    origin=dos["dossiers"]
    source_rows=semantic["subparameters"]
    rids=[r["id"] for r in source_rows]
    gids=[r["id"] for r in graph["nodes"]]
    cids=[r["id"] for r in origin]
    demand(len(source_rows)==len(graph["nodes"])==len(origin)==355,
           "REAL_SOURCE_RECORD_COUNT_NOT_355")
    demand(len(set(rids))==355 and set(rids)==set(gids)==set(cids),
           "REAL_SOURCE_ID_MISMATCH")
    demand(semantic.get("worlds")==graph.get("worlds")==62,
           "62_SOURCE_WORLDS_REQUIRED")
    demand(len({r["world"] for r in source_rows})==62,
           "SOME_CANONICAL_WORLDS_MISSING")
    demand(len(stages["all_children"])==355,
           "NOT_355_IN_CONCEPTUAL_PIPELINE")
    demand(dos["prematch_slots_two_teams"]==710,
           "NOT_710_TWO_TEAM_PRET0_SLOTS")
    demand(len(graph["edges"])==1088,
           "DOCUMENTARY_EDGE_COUNT_SOURCE_DRIFT_REVIEW_REQUIRED")
    demand(len(graph["unresolved_source_references"])==1,
           "UNRESOLVED_SOURCE_REFERENCE_COUNT_CHANGED_REVIEW_REQUIRED")
    modern=[r for r in source_rows if r.get("source_contract")]
    archived=[r for r in source_rows if not r.get("source_contract")]
    demand(len(modern)==343 and len(archived)==12,
           "343_MODERN_12_ARCHIVAL_SOURCE_SPLIT_REQUIRED")
    modern_sources={r["source_contract"] for r in modern}
    demand(len(modern_sources)==24,
           "EXACT_24_MODERN_ORIGINAL_FILES_REQUIRED")
    demand(all(r.get("source_origin")=="ARCHIVE_BYTES_VERIFIED"
               for r in origin if r["id"] in {a["id"] for a in archived}),
           "ARCHIVE_12_SOURCE_IDENTITY_NOT_ATTESTED")
    demand(dos["source_named_branch_without_guard_child_count"]==12,
           "BATCH23_NAMED_GUARDLESS_BRANCH_COUNT_CHANGED")
    demand(dos["source_archival_state_without_guard_child_count"]==12,
           "12_ARCHIVED_QUALITATIVE_STATES_NOT_PRESERVED")
    demand(dos["source_owner_not_declared_child_count"]==4,
           "FOUR_PILOT_OWNERS_UNKNOWN_EXPECTED")
    demand(dos["source_horizon_incomplete_child_count"]==0,
           "ORIGINAL_SIX_HORIZON_COVERAGE_INCOMPLETE")
    demand(summary["source_definition_field_count"]==306,
           "ORIGINAL_SOURCE_DEFINITION_FIELD_COUNT_DRIFT")
    demand(summary["source_definition_field_missing"]==49,
           "ORIGINAL_MISSING_DEFINITION_COUNT_DRIFT")
    demand(all(v["numeric_goals_coefficient"] is None
               and v["inference_goals_effect_sign"] is None
               and not v["empirical_validation_completed"]
               for v in origin), "UNAUTHORIZED_INDIVIDUAL_GOAL_COEFFICIENT")
    demand(all(b["branch_weight"] is None
               and not b["causal_direction_signed"]
               and (b["guard_executable"] or b["guard_not_authored_abstain"])
               for v in origin for b in v["conditional_source_scenarios"]),
           "UNAUTHORIZED_BRANCH_PROBABILITY_OR_INVENTED_GUARD")
    demand(summary["remaining_324_without_individually_signed_goal_effects"]==324,
           "EXPERIMENTAL_CAUSAL_STATUS_DRIFT")
    demand(summary["numeric_probability_calibrated"] is None
           and summary["real_world_predictive_accuracy"] is None,
           "FALSE_EMPIRICAL_CALIBRATION")
    demand(result["prematch_evidence"]["source_children"]==355
           and result["prematch_evidence"]["two_team_evidence_slots"]==710,
           "TWO_TEAM_PIT_CONTEXT_LOST")
    demand(summary["hypothetical_sensitivity_cases"]==1000
           and len(result["synthetic_grid"]["scenarios"])==1000,
           "NOT_1000_LAB_SCENARIOS")
    demand(result["poisson_IC"]["IC_over15_theoretical_percent"] is not None
           and result["shot_IC"]["IC_over15_theoretical_percent"] is not None,
           "CONDITIONAL_THEORETICAL_ICS_MISSING")
    demand(result["poisson_IC"]["IC_over15_calibrated_percent"] is None
           and result["shot_IC"]["IC_over15_empirically_calibrated_percent"] is None,
           "FALSE_NUMERIC_GOAL_CALIBRATION")
    return {
        "original_modern_files":24,
        "original_modern_children":343,
        "original_archived_children":12,
        "source_worlds":62,
        "all_355_canonical_ids_reconciled":True,
        "prematch_team_slots":710,
        "documentary_edges":1088,
        "quarantined_unresolved_source_references":1,
        "original_canonical_definitions_present":306,
        "source_named_branch_children_without_guard":12,
        "archival_state_branch_children_without_guard":12,
        "original_pilot_children_without_attested_owner":4,
        "all_six_source_horizons_complete":True,
        "causal_goal_effects_not_signed":324,
        "hypothetical_lab_ics":1000,
        "goal_probabilities_calibrated":False
    }

def verify_manifest(out:Path,expected:dict[str,str]):
    manifest_path=out/"MANIFEST_SHA256.json"
    manifest=json.loads(manifest_path.read_text(encoding="utf8"))
    demand(manifest["files"]==expected,
           "MANIFEST_DOES_NOT_AGREE_WITH_PERSISTENCE_RESULT")
    demand(manifest["no_calibrated_IC_claimed"] is True,
           "HASH_MANIFEST_FALSE_CALIBRATION")
    for filename,digest in manifest["files"].items():
        item=(out/filename).resolve()
        demand(item.parent==out.resolve() and item.is_file(),
               "OUTPUT_FILE_MISSING_OR_ESCAPES_OUTPUT_DIR:"+filename)
        demand(hashlib.sha256(item.read_bytes()).hexdigest()==digest,
               "OUTPUT_SHA256_MISMATCH:"+filename)
    demand("R8_NATIVE_OPERATIONAL_355_PRIVATE.json" in expected,
           "PRIVATE_DOSSIERS_NOT_PERSISTED")
    demand("IC_THEORETICAL_GRID_1000.json" in expected,
           "LAB_GRID_1000_NOT_PERSISTED")
    return {"verified_manifest_files":len(expected),
            "sha256_manifest_integrity":True}

def run(root:Path,out:Path,receipt_path:Path):
    metadata={"schema":"MOTEUR_D071_ORIGINAL_PRIVATE_R8_PYTHON_E2E",
              "source_kind":"ORIGINAL_PRIVATE_R8_V22_PLUS_VERIFIED_ARCHIVE",
              "readiness":"UNVERIFIED_UNTIL_TEST_FINISHES",
              "run_id":os.environ.get("GITHUB_RUN_ID"),
              "commit":os.environ.get("GITHUB_SHA"),
              "lab_fixture_only":True,
              "real_match_validation":False,
              "sporting_predictive_accuracy":None}
    try:
        # In-source loader, extraction and semantic graph are REAL, unmocked.
        product=m.build(root,FIXTURE,RATES,SHOTS,generate_grid=True)
        details=verify_original_355(product)
        shas=m.persist(product,out)
        hashed=verify_manifest(out,shas)
        metadata.update({"readiness":"PASS_ORIGINAL_355_PYTHON_E2E",
                         "e2e_pass":True,"source_check":details,
                         "manifest_check":hashed,
                         "conclusion":"R8_SOURCE_INTEGRATION_ONLY_NO_SPORTS_CALIBRATION"})
    except Exception as exc:
        metadata.update({"readiness":"FAIL_SOURCE_E2E",
                         "e2e_pass":False,"error_type":type(exc).__name__,
                         "error":str(exc),
                         "traceback_tail":traceback.format_exc()[-4500:]})
    receipt_path.parent.mkdir(parents=True,exist_ok=True)
    receipt_path.write_text(json.dumps(metadata,sort_keys=True,
                            ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:metadata.get(k) for k in
                     ("schema","readiness","e2e_pass","error_type","error")},
                     sort_keys=True))
    return 0 if metadata["e2e_pass"] else 1

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--r8-repo-root",required=True,type=Path)
    parser.add_argument("--outdir",required=True,type=Path)
    parser.add_argument("--receipt",required=True,type=Path)
    args=parser.parse_args()
    raise SystemExit(run(args.r8_repo_root,args.outdir,args.receipt))
