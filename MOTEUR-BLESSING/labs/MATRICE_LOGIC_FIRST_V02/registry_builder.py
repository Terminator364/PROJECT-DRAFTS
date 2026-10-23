#!/usr/bin/env python3
"""Build a complete, provenance-preserving R8 L3 inventory from compiler V22.

No internet, scoring, data imputation or implicit role promotion.
Input: checked-out R8 ChatGPT-PC source repository with its archived contracts.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any
from logic_engine_v02 import EXTRA, core

N_WORLDS=62
N_CHILDREN=355
ACTIVE_IDS=set(EXTRA.values()) | set(core.FIELD_TO_ALIAS)
assert len(ACTIVE_IDS)==31
HELD_ONLY_ALIASES = ("CROSS", "AERIAL", "AERIALDEF", "MARKING",
                     "CLEARANCE", "REBOUND", "SHIFT", "MISTAKE",
                     "SCOREMAP", "BENCH")
HELD_ONLY_IDS = {EXTRA[alias] for alias in HELD_ONLY_ALIASES}
assert len(HELD_ONLY_IDS) == 10 and HELD_ONLY_IDS.issubset(ACTIVE_IDS)

# Categorization assists review, not proof of actual causal mechanisms.
PROVENANCE_MARKERS=("COVERAGE","DENOMINATOR","SCHEMA","RIGHTS","PROVENANCE",
                    "PIT","SAMPLE_BIAS","VERIFIABILITY","BOUNDARY",
                    "REPORTING_BIAS","CLOCK_DEPENDENCY","DOMAIN_MATCHING")
CONDITIONAL_MARKERS=("SCORE_STATE","LEAD_","TRAIL_","DRAW_LATE",
                     "POLICY","FORCED_SUB_BRANCH")

def initial_role(child_id:str)->str:
    suffix=child_id.split(".",1)[-1]
    if any(x in suffix for x in PROVENANCE_MARKERS):
        return "SOURCE_OR_DEFINITION_GUARD_REVIEW_REQUIRED"
    if any(x in suffix for x in CONDITIONAL_MARKERS):
        return "HYPOTHETICAL_CONDITIONAL_CONTEXT_REVIEW_REQUIRED"
    return "POTENTIAL_PROCESS_EVIDENCE_REVIEW_REQUIRED"


def assemble(compiled:dict[str,Any])->dict[str,Any]:
    if len(compiled.get("worlds",[]))!=N_WORLDS or compiled.get("rich_contract_children")!=N_CHILDREN:
        raise ValueError("NOT_R8_62_355_COMPILER_OUTPUT")
    parents=set()
    IDs=set()
    entries=[]
    for world in compiled["worlds"]:
        parent=world["id"]
        if parent in parents or parent not in core.CANONICAL_WORLDS:
            raise ValueError("NONCANONICAL_OR_DUPLICATE_PARENT:"+str(parent))
        parents.add(parent)
        for raw in world["children"]:
            cid=raw["child_id"]
            if cid in IDs or not cid.startswith(parent+"."):
                raise ValueError("DUPLICATE_OR_MISPLACED_ID:"+cid)
            IDs.add(cid)
            if raw.get("scoring_allowed") is not False or raw.get("numeric_effect") is not None:
                raise ValueError("UNEXPECTED_PREMATURE_SCORING:"+cid)
            if raw.get("publisher_PIT_attested") is True:
                raise ValueError("UNEXPECTED_PIT_ATTESTATION:"+cid)
            active=cid in ACTIVE_IDS
            entries.append({"id":cid,"world":parent,"source_contract":raw.get("contract_file"),
                            "original_documentary_status":raw.get("status"),
                            "declared_evidence_owner":raw.get("owner",parent),
                            "horizons_in_source":raw.get("horizons",[]),
                            "inventory_role_candidate":initial_role(cid),
                            "role_review_status":"MACHINE_PROVISIONAL_NOT_SEMANTICALLY_SIGNED",
                            "code_wiring":("TRACEABLE_SEMANTIC_HOLD_ONLY" if cid in HELD_ONLY_IDS else "EXECUTABLE_SYNTHETIC_LOGIC_LOT01" if active else "NOT_CONNECTED_TO_LOGIC"),
                            "numeric_effect_calibrated":False,"editorial_PIT_independently_proven":False})
    if len(IDs)!=N_CHILDREN or IDs.issuperset(ACTIVE_IDS) is False or len(parents)!=N_WORLDS:
        raise ValueError("EXHAUSTIVENESS_OR_ACTIVE_REFERENCE_FAILURE")
    entries.sort(key=lambda x:x["id"])
    return {"schema":"MATRICE_R8_L3_LOGIC_FIRST_V02_REGISTRY",
            "worlds":N_WORLDS,"source_documentary_subparameters":N_CHILDREN,
            "real_semantic_roles_individually_human_validated":0,
            "software_wired_to_explanatory_rules":31,"held_semantic_only":10,
            "conditionally_activatable_under_lab_hypotheses":21,"not_wired":324,
            "numeric_IC_calibrated":None,"source_compiler":"L3_RUN_B_8_WORLDS_20261018/compile_v22.py",
            "source_sha256_by_contract":compiled.get("source_sha256",{}),
            "classification_contract":"Automatic screening is NOT a completed review of 355 true causal roles",
            "subparameters":entries}


def read_canonical(repo_root:Path)->dict[str,Any]:
    path=repo_root/"MATRICE/R8_G3_DEEP_20261014/L3_RUN_B_8_WORLDS_20261018/compile_v22.py"
    if not path.is_file():raise FileNotFoundError(str(path))
    spec=importlib.util.spec_from_file_location("l3_full_compiler_v22",path)
    if spec is None or spec.loader is None:raise RuntimeError("CANNOT_IMPORT_R8_COMPILER")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.current(repo_root)


def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--r8-repo-root",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    catalogue=assemble(read_canonical(args.r8_repo_root.resolve()))
    args.output.write_text(json.dumps(catalogue,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(args.output),"children":355,"active":31,"remaining":324}))

if __name__=="__main__":main()
