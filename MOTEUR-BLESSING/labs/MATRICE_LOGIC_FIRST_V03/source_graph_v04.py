#!/usr/bin/env python3
"""D060: verify all 355 R8 original semantics and construct unscored dependency graph.

Uses exclusively pre-existing private R8 contracts (including byte-verified
archival material); no plus/minus points, causal direction, or goal probability.
"""
from __future__ import annotations
import argparse, importlib.util, json, sys
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA="MATRICE_R8_D060_SOURCE_SEMANTIC_GRAPH_NO_NUMERIC_IC"
ROOT_COMPILER="MATRICE/R8_G3_DEEP_20261014/L3_COMPILER_62_PREMATCH_20261016"
SEMANTIC_FIELDS=("name_fr","definition_du_sous_parametre","mechanistic_hypothesis",
                 "owned_mechanism","anti_double_count_owner","anti_overlap",
                 "related_worlds","required_inputs","context_domain","applicability",
                 "variables","candidate_indices")
class SourceGraphError(ValueError):pass

def extract_original_archives(root:Path)->dict[str,dict[str,Any]]:
    """Read the *original* 12 children, do not silently reconstruct them."""
    module_file=root/ROOT_COMPILER/"archive_adapter.py"
    if not module_file.is_file():raise SourceGraphError("ARCHIVE_ADAPTER_UNAVAILABLE")
    sys.path.insert(0,str(module_file.parent))
    try:
        from archive_adapter import open_verified_archive, LOT01_JSON, PILOT_JSON, recovered
        valid=recovered(root)
        known={r["child_id"] for r in valid}
        with open_verified_archive(root) as z:
            lot=json.loads(z.read(LOT01_JSON))
            pilot=json.loads(z.read(PILOT_JSON))
        all_raw=[c for w in lot["worlds"] for c in w["children"]]+list(pilot["design_children"])
    finally:
        sys.path.pop(0)
    originals={}
    for c in all_raw:
        child=c["subparameter_id"]
        if child in originals:raise SourceGraphError("ARCHIVE_CHILD_DUPLICATE:"+child)
        originals[child]=c
    if set(originals)!=known or len(originals)!=12:
        raise SourceGraphError("ARCHIVE_12_NOT_IDENTICAL_TO_VERIFIED_ORIGINALS")
    return originals

def complete_archives(enriched:dict[str,Any],originals:dict[str,dict[str,Any]])->dict[str,Any]:
    """Map original byte-verifiable archival fields without inventing absent ones."""
    rows=enriched["subparameters"]
    if len(rows)!=355 or enriched.get("source_documented")!=343 or enriched.get("archived_legacy")!=12:
        raise SourceGraphError("D058_355_EXPECTED")
    rest={r["id"] for r in rows if r["source_contract"] is None}
    if len(rest)!=12 or set(originals)!=rest:
        raise SourceGraphError("ARCHIVE_IDS_MUST_MATCH_ALL_12")
    out=[]
    for row in rows:
        fresh=dict(row)
        if row["id"] in rest:
            original=originals[row["id"]]
            if original.get("parent_world_id")!=row["world"]:
                raise SourceGraphError("ARCHIVE_WORLD_MISMATCH:"+row["id"])
            if original.get("scoring_active") is not False or original.get("numeric_effect") is not None:
                raise SourceGraphError("ARCHIVE_UNAUTHORIZED_SCORING")
            fresh["private_semantic_contract"]={
                **{field:original.get(field) for field in SEMANTIC_FIELDS},
                "original_source_fields_present":[k for k in SEMANTIC_FIELDS if k in original],
                "archive_native_source_fields":sorted(original),
                "archive_temporal_policy":original.get("temporal_policy"),
            }
            fresh["semantic_evidence_status"]="ARCHIVE_ORIGINAL_BYTES_VERIFIED_AND_SEMANTICS_EXTRACTED"
        out.append(fresh)
    return {**enriched,"schema":"R8_L3_PRIVATE_SEMANTIC_SOURCE_COMPLETE_D060",
            "subparameters":out,"archive_originals_semantically_extracted":12}

def graph(enriched:dict[str,Any])->dict[str,Any]:
    rows=enriched.get("subparameters",[])
    if enriched.get("worlds")!=62 or len(rows)!=355 or len({r["id"] for r in rows})!=355:
        raise SourceGraphError("NOT_EXACT_CANONICAL_355")
    worlds={r["world"] for r in rows}
    if len(worlds)!=62:raise SourceGraphError("NOT_62_PARENTS")
    edges=[];nodes=[];diagnostics=Counter()
    for row in rows:
        cid=row["id"];parent=row["world"]
        if not cid.startswith(parent+"."):raise SourceGraphError("CHILD_PARENT_MISMATCH:"+cid)
        if row["direction_of_effect_on_goals"]!="NOT_SIGNED" or row.get("direct_goal_probability_effect") is not None:
            raise SourceGraphError("FAKE_SCIENTIFIC_SCORING:"+cid)
        s=row["private_semantic_contract"]
        if not isinstance(s,dict):raise SourceGraphError("MISSING_SEMANTIC_CONTRACT:"+cid)
        raw_name=s.get("name_fr") or row.get("original_name")
        raw_definition=s.get("definition_du_sous_parametre")
        if raw_name:diagnostics["named_by_source"]+=1
        if raw_definition:diagnostics["defined_text_by_source"]+=1
        if row.get("source_contract") is None:
            diagnostics["archived_original_bytes_extracted" if row.get("semantic_evidence_status")=="ARCHIVE_ORIGINAL_BYTES_VERIFIED_AND_SEMANTICS_EXTRACTED" else "archived_metadata_only"]+=1
        else:diagnostics["modern_original_contracts"]+=1
        relation=s.get("related_worlds") or []
        if not isinstance(relation,list):raise SourceGraphError("RELATED_WORLDS_NOT_LIST:"+cid)
        if any(not isinstance(x,str) or x not in worlds for x in relation):
            raise SourceGraphError("UNKNOWN_RELATED_WORLD:"+cid)
        owner=s.get("anti_double_count_owner") or row.get("declared_evidence_owner")
        anti=s.get("anti_overlap")
        if anti is not None and not isinstance(anti,dict):
            raise SourceGraphError("MALFORMED_OVERLAP:"+cid)
        mechanism=s.get("owned_mechanism")
        if not mechanism:diagnostics["mechanism_unresolved"]+=1
        else:diagnostics["mechanism_label_source"]+=1
        if anti:
            partner=anti.get("other_world")
            if partner:
                if partner not in worlds:raise SourceGraphError("UNKNOWN_OVERLAP_WORLD:"+cid)
                edges.append({"from":cid,"to_world":partner,"kind":"DOCUMENTED_SHARED_EVENT_OVERLAP_NOT_CAUSAL","incident_identity_template":anti.get("common_incident_key"),"owner":owner})
                diagnostics["anti_overlap_edges"]+=1
        for other in sorted(set(relation)):
            if other!=parent:
                edges.append({"from":cid,"to_world":other,"kind":"SOURCE_DECLARED_RELATED_WORLD_UNDIRECTED_NOT_CAUSAL","owner":owner})
                diagnostics["related_world_edges"]+=1
        node={"id":cid,"parent":parent,"source_origin":row.get("source_contract") or "VERIFIED_ARCHIVAL_MEMBER",
              "owned_mechanism_source":mechanism,"owner_documentary":owner,
              "name_source":raw_name,"definition_source":raw_definition,
              "candidate_role":row["inventory_role_candidate"],
              "human_causal_sign_review":"NOT_DONE",
              "direction_of_goal_effect":"UNESTABLISHED",
              "IC_effect":None,
              "semantic_gap":("MISSING_ORIGINAL_DEFINITION" if not raw_definition else "MECHANISM_DIRECTION_UNVALIDATED")}
        nodes.append(node)
    if len(nodes)!=355:raise SourceGraphError("NODE_LOSS")
    return {"schema":SCHEMA,"worlds":62,"documentary_subparameters":355,
       "nodes":nodes,"edges":edges,"counts":dict(diagnostics),
       "cross_world_edges_are_causal":False,
       "each_goals_effect_human_signed":0,
       "numeric_ic_under_hypotheses":None,"numeric_ic_calibrated":None,
       "independent_match_outcomes_used":0,
       "scientific_status":"NOT_A_GOAL_PROBABILITY_MODEL"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--enriched",type=Path,required=True)
    p.add_argument("--r8-repo-root",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--full-semantic-out",type=Path,required=True)
    args=p.parse_args()
    original=extract_original_archives(args.r8_repo_root.resolve())
    doc=complete_archives(json.loads(args.enriched.read_text(encoding="utf-8")),original)
    outcome=graph(doc)
    args.full_semantic_out.write_text(json.dumps(doc,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    args.out.write_text(json.dumps(outcome,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"node_count":355,"edges":len(outcome["edges"]),
          "archival_originals_full":outcome["counts"].get("archived_original_bytes_extracted",0),
          "original_definitions_present":outcome["counts"].get("defined_text_by_source",0),
          "IC":None},sort_keys=True))

if __name__=="__main__":main()
