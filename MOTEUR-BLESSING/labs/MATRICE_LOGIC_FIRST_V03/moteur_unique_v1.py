#!/usr/bin/env python3
"""MOTEUR D065: single-entry, offline-capable R8 logic and conditional IC engine.

Commands build *all* 355 original source-native dossier cards, 355-stage routes
and evidence graph. Numeric ICs are returned only if explicit, exogenous
hypotheses are supplied. Nothing is trained/calibrated silently or claimed
to be a validated sports forecast.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from typing import Any
import sys
# Standalone on Windows/Linux: resolve sibling original V0.2 code without
# requiring a manually-set PYTHONPATH or a Desktop Commander session.
_V02_PATH = Path(__file__).resolve().parent.parent / "MATRICE_LOGIC_FIRST_V02"
if not _V02_PATH.is_dir():
    raise RuntimeError("MOTEUR_V02_SIBLING_REQUIRED_NO_SILENT_FALLBACK")
if str(_V02_PATH) not in sys.path:
    sys.path.insert(0, str(_V02_PATH))
import registry_builder
import logic_registry_v03
import enrich_registry_v03
import source_graph_v04
import source_field_audit_v05
import source_mechanism_dossiers_v11
import causal_stages_v07
import theoretical_ic_v08
import shot_process_v10
import historical_baseline_v12

SCHEMA="MOTEUR_D065_SINGLE_ENTRY_LOGIC_FIRST_AND_THEORETICAL_IC"

def _read(path:Path|None)->dict[str,Any]|None:
    if path is None:return None
    data=json.loads(path.read_text(encoding="utf8"))
    if not isinstance(data,dict):raise ValueError("JSON_OBJECT_REQUIRED:"+str(path))
    return data

def build(root:Path,fixture:dict[str,Any]|None=None,
          rate_hypothesis:dict[str,Any]|None=None,
          shot_hypothesis:dict[str,Any]|None=None,
          generate_grid:bool=False,
          historical_games:list[dict[str,Any]]|None=None,
          historical_walkforward:bool=False)->dict[str,Any]:
    if not root.is_dir():raise FileNotFoundError("ORIGINAL_R8_REPOSITORY_REQUIRED")
    if (rate_hypothesis is not None or shot_hypothesis is not None) and fixture is None:
        raise ValueError("FIXTURE_WITH_ASOF_AND_KICKOFF_REQUIRED_FOR_THEORETICAL_IC")
    compiled=registry_builder.read_canonical(root.resolve())
    reg=registry_builder.assemble(compiled)
    source=enrich_registry_v03.enrich(reg,root.resolve())
    archive=source_graph_v04.extract_original_archives(root.resolve())
    full=source_graph_v04.complete_archives(source,archive)
    graph=source_graph_v04.graph(full)
    stages=causal_stages_v07.route_source_graph(graph)
    original=source_field_audit_v05.original_lookup(root.resolve(),full["subparameters"])
    schema_audit=source_field_audit_v05.summarize(full,original)
    dossiers=source_mechanism_dossiers_v11.dossiers(full,original)
    evidence=logic_registry_v03.analyze(fixture,reg) if fixture is not None else None
    rates=theoretical_ic_v08.evaluate(fixture,rate_hypothesis,evidence) if fixture is not None else None
    shots=shot_process_v10.calculate(fixture,shot_hypothesis,graph) if shot_hypothesis is not None else None
    grid=theoretical_ic_v08.synthetic_grid_1000() if generate_grid else None
    historical=(historical_baseline_v12.predict(fixture,historical_games)
                if historical_games is not None and fixture is not None else None)
    backtest=(historical_baseline_v12.walkforward(historical_games)
              if historical_games is not None and historical_walkforward else None)
    assert len(graph["nodes"])==len(dossiers["dossiers"])==355
    assert len(stages["all_children"])==355 and stages["signed_per_child_goal_effects"]==0
    summary={"schema":SCHEMA,
             "continuity_code":"Moteur/continue",
             "status":"LOGICAL_DOSSIERS_COMPLETE_CAUSAL_GOAL_EFFECTS_NOT_ALL_SIGNED",
             "authentic_R8_worlds":62,
             "original_R8_subparameters":355,
             "native_operational_dossiers":355,
             "two_team_prematch_evidence_slots":710,
             "source_definition_field_count":schema_audit["canonical_definition_field_present"],
             "source_definition_field_missing":schema_audit["original_definition_field_absent"],
             "stage_counts":stages["stage_counts"],
             "documentary_relation_count":len(graph["edges"]),
             "unresolved_source_references":graph["unresolved_source_references"],
             "original_12_archives_verifiably_recovered":True,
             "experimental_children_connected_to_v02":31,
             "blocked_semantic_children_of_these_31":10,
             "remaining_324_without_individually_signed_goal_effects":324,
             "numeric_probability_from_R8_alone":None,
             "numeric_probability_calibrated":None,
             "real_world_predictive_accuracy":None,
             "independent_real_match_test_completed":False,
             "theoretical_poisson_ic_pct":rates["IC_over15_theoretical_percent"] if rates else None,
             "theoretical_shot_process_ic_pct":shots["IC_over15_theoretical_percent"] if shots else None,
             "hypothetical_sensitivity_cases":grid["scenario_count"] if grid else 0,
             "historical_baseline_status":historical["status"] if historical else None,
             "historical_baseline_IC_over15_percent":historical["IC_over15_percent"] if historical else None,
             "walkforward_brier":backtest["brier"] if backtest else None,
             "hypotheses_not_empirical_validation":True}
    return {"summary":summary,"registry":reg,"semantics":full,
            "source_graph":graph,"conceptual_stages":stages,
            "schema_audit":schema_audit,"dossiers":dossiers,
            "prematch_evidence":evidence,"poisson_IC":rates,
            "shot_IC":shots,"synthetic_grid":grid,
            "historical_baseline":historical,"historical_backtest":backtest}

def persist(result:dict[str,Any],outdir:Path)->dict[str,str]:
    outdir.mkdir(parents=True,exist_ok=True)
    names={"summary":"MOTEUR_V1_SUMMARY.json",
           "registry":"R8_ORIGINAL_355_REGISTRY.json",
           "semantics":"R8_ORIGINAL_355_SEMANTICS_PRIVATE.json",
           "source_graph":"R8_SOURCE_GRAPH_355_PRIVATE.json",
           "conceptual_stages":"R8_ALL_355_STAGES.json",
           "schema_audit":"R8_SOURCE_DEFINITION_AUDIT_PRIVATE.json",
           "dossiers":"R8_NATIVE_OPERATIONAL_355_PRIVATE.json",
           "prematch_evidence":"PRET0_EVIDENCE.json",
           "poisson_IC":"IC_THEORETICAL_POISSON.json",
           "shot_IC":"IC_THEORETICAL_SHOT_PROCESS.json",
           "synthetic_grid":"IC_THEORETICAL_GRID_1000.json",
           "historical_baseline":"IC_HISTORICAL_BASELINE_UNCALIBRATED.json",
           "historical_backtest":"HISTORICAL_WALKFORWARD_BRIER.json"}
    digests={}
    for key,filename in names.items():
        item=result.get(key)
        if item is None:continue
        value=json.dumps(item,sort_keys=True,ensure_ascii=False,indent=2)+"\n"
        dest=outdir/filename
        dest.write_text(value,encoding="utf8")
        digests[filename]=hashlib.sha256(value.encode("utf8")).hexdigest()
    manifest={"schema":"MOTEUR_D065_FILES_SHA256","files":digests,
              "no_calibrated_IC_claimed":True}
    (outdir/"MANIFEST_SHA256.json").write_text(
        json.dumps(manifest,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return digests

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--r8-repo-root",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    p.add_argument("--fixture",type=Path)
    p.add_argument("--rates",type=Path)
    p.add_argument("--projected-shots",type=Path)
    p.add_argument("--grid-1000",action="store_true")
    p.add_argument("--history",type=Path)
    p.add_argument("--walkforward-history",action="store_true")
    a=p.parse_args()
    if a.walkforward_history and not a.history:p.error("--walkforward-history requires --history")
    historical=json.loads(a.history.read_text(encoding="utf8")) if a.history else None
    product=build(a.r8_repo_root,_read(a.fixture),_read(a.rates),
                  _read(a.projected_shots),a.grid_1000,historical,a.walkforward_history)
    sha=persist(product,a.outdir)
    print(json.dumps({"summary":product["summary"],"files":len(sha)},sort_keys=True,ensure_ascii=False))
if __name__=="__main__":main()
