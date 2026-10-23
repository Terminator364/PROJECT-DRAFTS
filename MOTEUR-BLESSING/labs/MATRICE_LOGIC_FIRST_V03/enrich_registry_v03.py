#!/usr/bin/env python3
"""Join R8 full 355 registry to exact private source contracts.

The enriched data must remain on a private branch. This code publishes no
private source text. It records source definitions, overlap contracts and
traceability, not causal signs, coefficients, or a probability.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

FIELDS=("name_fr","definition_du_sous_parametre","mechanistic_hypothesis",
        "owned_mechanism","anti_double_count_owner","anti_overlap","related_worlds",
        "required_inputs","context_domain","applicability","variables",
        "candidate_indices")
PARENT_COUNTS=(62,355)
class SourceContractError(ValueError):pass

def enrich(registry:dict[str,Any],repo_root:Path)->dict[str,Any]:
    if (registry.get("worlds"),len(registry.get("subparameters",[])))!=PARENT_COUNTS:
        raise SourceContractError("EXPECTED_CANONICAL_62_355")
    docs={}
    entries=[]
    counts=Counter()
    for row in registry["subparameters"]:
        origin=row.get("source_contract")
        if origin:
            if origin not in docs:
                path=(repo_root/origin).resolve()
                if not path.is_relative_to(repo_root.resolve()) or not path.is_file():
                    raise SourceContractError("SOURCE_NOT_WITHIN_PRIVATE_R8:"+origin)
                raw=json.loads(path.read_text(encoding="utf-8"))
                children={}
                for w in raw.get("worlds",[]):
                    for c in w.get("children",[]):
                        cid=c.get("id",c.get("subparameter_id"))
                        if cid in children:raise SourceContractError("DUPLICATE_ID_IN_SOURCE:"+str(cid))
                        children[cid]=c
                docs[origin]=children
            original=docs[origin].get(row["id"])
            if original is None:
                raise SourceContractError("MISSING_EXACT_SOURCE_CHILD:"+row["id"])
            core={key:original.get(key) for key in FIELDS}
            core["original_source_fields_present"]=[k for k in FIELDS if k in original]
            status="SOURCE_DOCUMENTED_NOT_CAUSALLY_SIGNED"
            counts["source_documented"]+=1
        else:
            # 12 historically archived L3 children: the compiler validates
            # byte-preserved source archives, not a modern JSON path.
            core={key:None for key in FIELDS}
            core["original_source_fields_present"]=[]
            status="ARCHIVE_VERIFIED_BY_COMPILER_NOT_EXPANDED_IN_THIS_PASS"
            counts["archived"]+=1
        entries.append({**row,"private_semantic_contract":core,
                        "semantic_evidence_status":status,
                        "direction_of_effect_on_goals":"NOT_SIGNED",
                        "direct_goal_probability_effect":None,
                        "human_semantic_review_completed":False})
    if counts["source_documented"]!=343 or counts["archived"]!=12:
        raise SourceContractError("EXPECTED_343_PLUS_12_SOURCE_PROVENANCE")
    return {"schema":"R8_L3_PRIVATE_SEMANTIC_PROVENANCE_D058",
            "worlds":62,"subparameters":entries,"source_documented":343,
            "archived_legacy":12,"unique_source_contract_files":len(docs),
            "readiness":"ALL_355_PROVENANCE_LINKED_NOT_355_CAUSAL_RULES",
            "IC_calibrated":None,"IC_theoretical_numeric":None,
            "publication":"PRIVATE_REPO_ONLY",
            "human_semantic_review_completed":0}

def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--registry",required=True,type=Path)
    parser.add_argument("--r8-repo-root",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    if not args.r8_repo_root.is_dir():raise SourceContractError("R8_REPO_ROOT_MISSING")
    registry=json.loads(args.registry.read_text(encoding="utf-8"))
    data=enrich(registry,args.r8_repo_root.resolve())
    args.output.write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"source_documented":343,"archived":12,"worlds":62,
                      "contract_files":data["unique_source_contract_files"],
                      "IC_calibrated":None}))
if __name__=="__main__":main()
