#!/usr/bin/env python3
"""D064: 355 original, source-native, pre-T0 operational mechanism dossiers.

Every dossier is sourced from the actual original R8 JSON or byte-verified old
archive, preserving required inputs, provenance, scenario guard, anti-overlap
ownership, forbidden effects, horizons, and seven-stage conceptual routing.
This is an EXHAUSTIVE OPERATIONAL CONTRACT AUDIT, NOT an approved goal model.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
from typing import Any
from source_field_audit_v05 import original_lookup
from causal_stages_v07 import STAGE_BY_WORLD
from source_graph_v04 import SourceGraphError

SCHEMA="R8_D064_ALL_355_NATIVE_OPERATIONAL_MECHANISM_DOSSIERS"

def _string_or_none(val:Any)->str|None:
    return val.strip() if isinstance(val,str) and val.strip() else None

def _raw_scenario_branches(original:dict[str,Any])->list[dict[str,Any]]:
    tree=original.get("scenario_tree")
    if not isinstance(tree,dict):raise SourceGraphError("SCENARIO_TREE_NOT_DICT")
    raw=tree.get("branches")
    if not isinstance(raw,list) or not raw:raise SourceGraphError("ORIGINAL_BRANCHES_MISSING")
    result=[]
    for b in raw:
        if not isinstance(b,dict):raise SourceGraphError("SCENARIO_BRANCH_NOT_OBJECT")
        if b.get("weight") is not None or b.get("probability") is not None:
            raise SourceGraphError("FORBIDDEN_SOURCE_BRANCH_WEIGHTS")
        guard=_string_or_none(b.get("guard_predicate")) or _string_or_none(b.get("guard"))
        if not guard:raise SourceGraphError("UNSPECIFIED_SOURCE_BRANCH_GUARD")
        result.append({"branch_id":b.get("id"),
                       "original_guard_predicate":guard,
                       "original_qualitative_consequence":(
                           b.get("qualitative_consequence") or b.get("hypothesis")),
                       "original_branch_status":b.get("status","UNWEIGHTED_SOURCE_DESIGN"),
                       "branch_weight":None,
                       "causal_direction_signed":False})
    return result

def dossiers(semantics:dict[str,Any], original:dict[str,dict[str,Any]])->dict[str,Any]:
    rows=semantics.get("subparameters")
    if not isinstance(rows,list) or len(rows)!=355 or len(original)!=355:
        raise SourceGraphError("REQUIRED_R8_355")
    seen=set()
    docs=[]
    ctr=Counter()
    for row in rows:
        cid=row["id"];world=row["world"]
        if cid in seen or cid not in original or world not in STAGE_BY_WORLD or not cid.startswith(world+"."):
            raise SourceGraphError("SOURCE_DOSSIER_ID_DRIFT:"+cid)
        seen.add(cid)
        c=original[cid]
        if c.get("scoring_active") is not False or c.get("numeric_effect") is not None:
            raise SourceGraphError("SOURCE_PROMOTED_SCORING_UNAUTHORIZED:"+cid)
        owner=c.get("anti_double_count_owner")
        if not isinstance(owner,str) or not owner:
            raise SourceGraphError("SOURCE_ANTI_DOUBLE_COUNT_OWNER_MISSING:"+cid)
        req=c.get("required_inputs")
        if not isinstance(req,list) or not req or any(not isinstance(k,str) or not k for k in req):
            raise SourceGraphError("SOURCE_REQUIRED_INPUTS_MISSING:"+cid)
        evidence=c.get("evidence_search_plan",c.get("source_search_plan"))
        if not isinstance(evidence,list) or not evidence:
            raise SourceGraphError("SOURCE_EVIDENCE_PLAN_MISSING:"+cid)
        anticipations=c.get("anticipations_by_horizon")
        if not isinstance(anticipations,list) or len(anticipations)!=6:
            raise SourceGraphError("SOURCE_SIX_HORIZONS_MISSING:"+cid)
        plan=[]
        for h in anticipations:
            if not isinstance(h,dict) or not isinstance(h.get("horizon"),str):
                raise SourceGraphError("SOURCE_HORIZON_CORRUPT:"+cid)
            plan.append({"horizon":h["horizon"],"guard_procedure":h.get("procedure"),
                         "missing_data_policy":h.get("when_no_source",h.get("if_missing","UNKNOWN")),
                         "future_data_not_allowed":True})
        scenario=_raw_scenario_branches(c)
        question=(_string_or_none(c.get("purpose_and_causal_question")) or
                  _string_or_none(c.get("definition_du_sous_parametre")) or
                  _string_or_none(c.get("question")))
        original_name=_string_or_none(c.get("name_fr"))
        if not original_name:raise SourceGraphError("ORIGINAL_NAME_MISSING:"+cid)
        source_description=(_string_or_none(c.get("definition_du_sous_parametre")) or
                            _string_or_none(c.get("purpose_and_causal_question")) or
                            _string_or_none(c.get("question")))
        if source_description:ctr["source_description_present"]+=1
        else:ctr["no_original_descriptive_sentence"]+=1
        stage=STAGE_BY_WORLD[world]
        doc={"id":cid,"world":world,"source_origin":row.get("source_contract") or "ARCHIVE_BYTES_VERIFIED",
             "native_name_fr":original_name,
             "native_source_question_or_definition":question,
             "conceptual_pipeline_stage":stage,
             "context_type":c.get("context_type"),
             "source_owned_mechanism_label":c.get("owned_mechanism"),
             "applicability_condition_as_written":c.get("applicability_condition"),
             "not_owned_or_excluded_effects":c.get("not_owned",c.get("excluded_effects")),
             "anti_double_count_owner":owner,
             "required_inputs_as_written":req,
             "evidence_source_search_count":len(evidence),
             "evidence_sources_original":evidence,
             "prematch_six_horizons":plan,
             "conditional_source_scenarios":scenario,
             "unresolved_source_related_identifiers":[],
             "inference_goals_effect_sign":None,
             "numeric_goals_coefficient":None,
             "empirical_validation_completed":False,
             "review_status":"COMPLETE_ORIGINAL_OPERATIONAL_DOSSIER_NOT_APPROVED_CAUSAL_SIGN"}
        docs.append(doc)
        ctr[stage]+=1
    if len(seen)!=355 or len(docs)!=355:raise SourceGraphError("DOSSIER_355_COUNT_MISMATCH")
    return {"schema":SCHEMA,"worlds":62,"operational_dossiers":355,
            "dossiers":docs,"counts":dict(ctr),
            "prematch_slots_two_teams":710,
            "source_six_horizons_each":True,
            "manual_signed_causal_effects":0,
            "empirical_calibration":None,
            "theoretical_goal_IC_from_r8_provenance_alone":None,
            "stage_classification_not_individual_causal_validation":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--semantic",type=Path,required=True)
    p.add_argument("--r8-repo-root",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    root=a.r8_repo_root.resolve()
    semantics=json.loads(a.semantic.read_text(encoding="utf8"))
    origins=original_lookup(root,semantics["subparameters"])
    output=dossiers(semantics,origins)
    a.out.write_text(json.dumps(output,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"worlds":62,"dossiers":355,"original_text_present":output["counts"].get("source_description_present",0),
                      "original_no_descriptive_sentence":output["counts"].get("no_original_descriptive_sentence",0),
                      "IC_calibrated":None}))
if __name__=="__main__":main()
