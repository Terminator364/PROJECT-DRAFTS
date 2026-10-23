#!/usr/bin/env python3
"""D061: review source-schema coverage without pretending every field is causal.

Resolve each of 355 R8 L3 rows to its exact original document or verified
archival member; list original definition candidates and missing fields.
Outputs remain in isolated private R8 audit branch.
"""
from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path
from typing import Any
from source_graph_v04 import extract_original_archives, SourceGraphError

TEXTUAL=("definition_du_sous_parametre","definition","description","scope",
         "mechanistic_hypothesis","mechanism","rationale","target_fact",
         "problem_definition","study_goal","question","purpose")
def original_lookup(root:Path, rows:list[dict[str,Any]])->dict[str,dict[str,Any]]:
    contracts={}
    original_archive=None
    children={}
    for row in rows:
        cid=row["id"]
        source=row.get("source_contract")
        if source is None:
            if original_archive is None:original_archive=extract_original_archives(root)
            original=original_archive.get(cid)
        else:
            if source not in contracts:
                target=(root/source).resolve()
                if not target.is_relative_to(root.resolve()) or not target.is_file():
                    raise SourceGraphError("SOURCE_PATH_INVALID:"+str(source))
                raw=json.loads(target.read_text(encoding="utf-8"))
                records={}
                for w in raw.get("worlds",[]):
                    for c in w.get("children",[]):
                        key=c.get("id",c.get("subparameter_id"))
                        if key in records:raise SourceGraphError("DUPLICATE_SOURCE_CHILD:"+key)
                        records[key]=c
                contracts[source]=records
            original=contracts[source].get(cid)
        if not isinstance(original,dict):
            raise SourceGraphError("ABSENT_ORIGINAL_CHILD:"+cid)
        if original.get("parent_world_id") not in (None,row["world"]):
            raise SourceGraphError("PARENT_MISMATCH:"+cid)
        if cid in children:raise SourceGraphError("DUPLICATE_CHILD:"+cid)
        children[cid]=original
    if len(children)!=355:raise SourceGraphError("NOT_355_ORIGINAL_RECORDS")
    return children

def summarize(sem:dict[str,Any], originals:dict[str,dict[str,Any]])->dict[str,Any]:
    rows=sem.get("subparameters",[])
    if len(rows)!=355 or set(originals)!={r["id"] for r in rows}:
        raise SourceGraphError("REQUIRED_EXACT_355")
    missing=[]
    by_source=defaultdict(lambda:Counter())
    definitions=0; usable_candidates=0; archives=0; missing_source_text=0
    for r in rows:
        cid=r["id"];doc=originals[cid];source=r.get("source_contract") or "VERIFIED_ARCHIVAL_SOURCE"
        if r.get("source_contract") is None:archives+=1
        own=r.get("private_semantic_contract",{})
        if not isinstance(own,dict) or r.get("direction_of_effect_on_goals")!="NOT_SIGNED":
            raise SourceGraphError("SOURCE_SEMANTIC_NOT_VERIFIED")
        has_def=isinstance(doc.get("definition_du_sous_parametre"),str) and bool(doc["definition_du_sous_parametre"].strip())
        alternatives={k:v for k in TEXTUAL if k!="definition_du_sous_parametre" 
                      if isinstance((v:=doc.get(k)),str) and v.strip()}
        if has_def:definitions+=1;by_source[source]["canonical_definition"]+=1
        else:
            by_source[source]["no_canonical_definition"]+=1
            if alternatives:usable_candidates+=1
            else:missing_source_text+=1
            missing.append({"id":cid,"source":source,"original_source_text_keys":list(alternatives),
                            "candidate_source_quotes_not_normalized":{k:v[:180] for k,v in alternatives.items()},
                            "required_manual_semantic_review":True,
                            "original_raw_field_keys":sorted(doc)})
    return {"schema":"R8_L3_D061_SOURCE_SCHEMA_DEF_AUDIT",
            "worlds":62,"children":355,
            "canonical_definition_field_present":definitions,
            "original_definition_field_absent":len(missing),
            "missing_with_other_text_fields":usable_candidates,
            "missing_without_any_supported_text_field":missing_source_text,
            "verified_archived_children":archives,
            "by_source":{k:dict(v) for k,v in sorted(by_source.items())},
            "missing_examples_and_provenance":missing,
            "numeric_probabilities":None,
            "decision":"UNRECOGNIZED_SCHEMA_IS_NOT_A_CAUSAL_MECHANISM",
            "semantic_review_completed":False}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--semantic",required=True,type=Path)
    parser.add_argument("--r8-repo-root",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    sem=json.loads(args.semantic.read_text(encoding="utf-8"))
    root=args.r8_repo_root.resolve()
    found=original_lookup(root,sem["subparameters"])
    result=summarize(sem,found)
    args.out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in (
        "children","canonical_definition_field_present","original_definition_field_absent",
        "missing_with_other_text_fields","missing_without_any_supported_text_field","verified_archived_children")},sort_keys=True))
if __name__=="__main__":main()
