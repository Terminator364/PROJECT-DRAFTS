#!/usr/bin/env python3
"""MOTEUR R8 — deterministic, pre-match, logic-first reasoning over 355 source IDs.

Never treats documentary relations as causal signs. Without explicit goal-rate
assumptions it returns no numeric Over 1.5 probability. Standard library only.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path

SCHEMA = "MOTEUR_R8_LOGIQUE_V1"
STAGES = {
    "SOURCE_AND_BOUNDARY": "FIXTURE_ID LEAGUE_BASE DATA_QUALITY MODEL_DOMAIN MARKET_SIGNAL SOCIAL_MEDIA",
    "TEAM_CAPACITY_CONTEXT": "TEAM_STRENGTH FORM_TRENDS SQUAD_AVAIL LINEUP_ROTATION COACH_TRANSITION TRANSFERS REST_CONGESTION FATIGUE_INJURY_INTERACTION FITNESS_RETURN TEAM_COHESION TACTICAL_ADAPTABILITY OPPONENT_SPECIFIC_PREPARATION PROMOTION_RELEGATION MOTIVATION_CONTEXT",
    "EXTERNAL_MATCH_CONTEXT": "REFEREE WEATHER PITCH_STADIUM TRAVEL INTERNATIONAL NEUTRAL_VENUE DISCIPLINE PLAY_TIME_RULES HOME_CROWD_PRESSURE CUP_TIE",
    "ATTACK_OPPORTUNITY": "SCORING_HISTORY SHOT_CREATION TACTIC_STYLE ATTACK_BUILDUP PRESSING_TURNOVERS TRANSITION_ATTACK SETPIECE_ATTACK ATTACK_DEF_MATCHUP POSSESSION_TERRITORIAL_CONTROL FINAL_THIRD_ACCESS OFF_BALL_MOVEMENT PASSING_COMBINATIONS WIDE_AERIAL_ATTACK INDIVIDUAL_TECHNICAL_EXECUTION ONE_V_ONE_DUELS SECOND_BALL_RECOVERY MATCH_RHYTHM_POTENTIAL GK_BUILDUP_DISTRIBUTION EXPECTED_MATCH_PROCESS UNFORCED_MISTAKE_RISK",
    "DEFENSIVE_OPPOSITION": "GK_DEFENSE TRANSITION_DEFENSE SHOT_SUPPRESSION SETPIECE_DEFENSE DEFENCE_STRUCTURE",
    "SHOT_AND_GOAL_CONDITIONAL": "SHOT_QUALITY SHOT_CONVERSION PENALTY_PATHWAYS OWN_GOAL_DEFLECTION_PATHWAYS",
    "FUTURE_SCORE_STATE_BRANCH": "GOAL_TIMING GAME_STATE_POLICY SUBSTITUTION_IMPACT",
}
WORLD_STAGE = {w: stage for stage, worlds in STAGES.items() for w in worlds.split()}
assert len(WORLD_STAGE) == 62 and sum(map(lambda v: len(v.split()),STAGES.values())) == 62

class LogicalContractError(ValueError):
    pass

def require(cond, reason):
    if not cond:
        raise LogicalContractError(reason)

def utc(value):
    require(isinstance(value, str), "UTC_REQUIRED")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as e:
        raise LogicalContractError("BAD_ISO_TIMESTAMP") from e
    require(dt.tzinfo is not None, "NAIVE_TIMESTAMP_FORBIDDEN")
    return dt.astimezone(timezone.utc)

def original_graph(graph):
    """Validate the real 355 R8 documentary catalogue without synthesizing IDs."""
    require(graph.get("worlds") == 62 and graph.get("documentary_subparameters") == 355,
            "ORIGINAL_R8_62_355_REQUIRED")
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    require(isinstance(nodes, list) and len(nodes) == 355, "355_NODES_REQUIRED")
    require(isinstance(edges, list) and len(edges) == 1088, "1088_SOURCE_LINKS_REQUIRED")
    require(graph.get("cross_world_edges_are_causal") is False,
            "DOCUMENTARY_GRAPH_CANNOT_BE_PROMOTED_TO_CAUSAL")
    require(graph.get("each_goals_effect_human_signed") is False,
            "UNSUPPORTED_CAUSAL_SOURCE_CLAIM")
    require(graph.get("numeric_ic_calibrated") is None,
            "ORIGINAL_GRAPH_FALSE_CALIBRATION")
    ids = set()
    worlds = set()
    for n in nodes:
        cid = n.get("id")
        world = n.get("parent")
        require(isinstance(cid, str) and isinstance(world, str)
                and cid.startswith(world + ".") and world in WORLD_STAGE,
                "INVALID_SOURCE_CHILD_ID")
        require(cid not in ids, "DUPLICATE_CHILD_ID:" + cid)
        require(n.get("IC_effect") is None and n.get("direction_of_goal_effect") == "UNESTABLISHED",
                "UNSIGNED_SOURCE_MUST_NOT_HAVE_GOAL_EFFECT:" + cid)
        ids.add(cid)
        worlds.add(world)
    require(len(ids) == 355 and len(worlds) == 62, "SOURCE_INVENTORY_GAP")
    types = Counter()
    for e in edges:
        require(e.get("from") in ids, "DANGLING_EDGE_SOURCE")
        if "to_world" in e:
            require(e["to_world"] in WORLD_STAGE, "INVALID_RELATED_WORLD")
        elif "to" in e:
            require(e["to"] in ids, "INVALID_RELATED_CHILD")
        else:
            require(False, "MISSING_EDGE_DESTINATION")
        types[e.get("kind")] += 1
    require(sum(types.values()) == 1088, "SOURCE_EDGE_DRIFT")
    # Original authors explicitly left this editorial reference unresolved.
    require(isinstance(graph.get("unresolved_source_references"), list),
            "UNRESOLVED_REFERENCE_REGISTER_MISSING")
    return {"nodes": nodes, "edges": edges, "ids": ids,
            "worlds": worlds, "edge_types": dict(sorted(types.items()))}

def checked_observation(item, target, asof, kickoff, ids, mode):
    require(isinstance(item, dict), "OBSERVATION_NOT_OBJECT")
    child = item.get("subparameter_id")
    side = item.get("team")
    state = item.get("state")
    require(child in ids, "UNKNOWN_OR_INVENTED_SUBPARAMETER:" + str(child))
    require(side in ("HOME", "AWAY"), "TEAM_MUST_BE_HOME_OR_AWAY")
    require(state in ("TRUE", "FALSE", "UNKNOWN"), "BAD_TRI_STATE")
    require(item.get("evidence_kind") in ("SYNTHETIC_ASSUMPTION", "VERIFIED_PRET0"),
            "EVIDENCE_KIND_REQUIRED")
    evidence = item["evidence_kind"]
    require(evidence == "SYNTHETIC_ASSUMPTION" or mode == "PREMATCH_EVIDENCE",
            "REAL_DATA_NOT_ALLOWED_IN_LAB_MODE")
    if evidence == "SYNTHETIC_ASSUMPTION":
        require(mode == "LAB_SYNTHETIC", "LAB_ASSUMPTION_NOT_ACCEPTED_AS_REAL")
    else:
        require(item.get("original_publisher_issue_independently_verified") is True,
                "PUBLISHER_ISSUE_NOT_ATTESTED")
        require(item.get("license_cleared") is True,
                "SOURCE_RIGHTS_NOT_CLEARED")
        require(isinstance(item.get("source_id"), str) and bool(item["source_id"].strip()),
                "SOURCE_ID_REQUIRED")
        issued = utc(item.get("original_publisher_issue_utc"))
        first_seen = utc(item.get("source_first_seen_utc"))
        require(issued <= first_seen <= asof < kickoff,
                "SOURCE_PUBLICATION_AFTER_CUTOFF")
        require(item.get("historic_fixture_id") != target,
                "TARGET_MATCH_NOT_HISTORICAL_EVIDENCE")
        require(item.get("historic_fixture_id"), "HISTORIC_ID_REQUIRED")
        require(utc(item.get("historic_final_utc")) <= issued,
                "HISTORIC_MATCH_NOT_COMPLETED_AT_ISSUE")
    return {"subparameter_id": child, "team": side, "state": state,
            "evidence_kind": evidence, "source_id": item.get("source_id")}

def source_status(graph, fixture):
    g = original_graph(graph)
    require(isinstance(fixture, dict) and fixture.get("schema") == "MOTEUR_R8_LOGIQUE_V1_INPUT",
            "FIXTURE_SCHEMA_INVALID")
    target = fixture.get("fixture_id")
    require(isinstance(target, str) and bool(target), "TARGET_ID_REQUIRED")
    asof = utc(fixture.get("analysis_asof_utc"))
    kickoff = utc(fixture.get("kickoff_utc"))
    require(asof < kickoff, "TARGET_KICKOFF_PASSED")
    mode = fixture.get("mode")
    require(mode in ("LAB_SYNTHETIC", "PREMATCH_EVIDENCE"), "SOURCE_MODE_REQUIRED")
    observations = fixture.get("observations", [])
    require(isinstance(observations, list), "OBSERVATIONS_NOT_LIST")
    ids = g["ids"]
    raw = defaultdict(set)
    checked = []
    for item in observations:
        o = checked_observation(item, target, asof, kickoff, ids, mode)
        checked.append(o)
        raw[(o["subparameter_id"], o["team"])].add(o["state"])
    rows = []
    statuses = {}
    counts = Counter()
    for n in g["nodes"]:
        cid = n["id"]
        stage = WORLD_STAGE[n["parent"]]
        for team in ("HOME", "AWAY"):
            seen = raw.get((cid, team), set())
            state = ("CONTRADICTED" if "TRUE" in seen and "FALSE" in seen
                     else "TRUE" if "TRUE" in seen
                     else "FALSE" if "FALSE" in seen else "UNKNOWN")
            statuses[(cid, team)] = state
            counts[state] += 1
            rows.append({"subparameter_id": cid, "world": n["parent"],
                         "stage": stage, "team": team, "state": state,
                         "goal_effect_sign": None, "goal_coefficient": None})
    require(len(rows) == 710, "R8_TWO_TEAM_COVERAGE_ERROR")
    return g, checked, statuses, rows, counts

def stage_paths(source, statuses):
    # These conditional AND-rules are *typed pathway constraints*, not signed
    # causal effects nor numerical additions to expected goals.
    groups = {}
    for side in ("HOME", "AWAY"):
        stage_ids = defaultdict(list)
        for n in source["nodes"]:
            if statuses[(n["id"], side)] == "TRUE":
                stage_ids[WORLD_STAGE[n["parent"]]].append(n["id"])
        groups[side] = stage_ids
    rules = [
        ("CAPACITY_CONDITIONED_OPPORTUNITY", [("SAME", "TEAM_CAPACITY_CONTEXT"), ("SAME", "ATTACK_OPPORTUNITY")],
         "Capacity and attacking opportunity appear together; effect on goals remains unknown."),
        ("EXTERNAL_CONTEXT_CONDITIONED_OPPORTUNITY", [("SAME", "EXTERNAL_MATCH_CONTEXT"), ("SAME", "ATTACK_OPPORTUNITY")],
         "Match context may condition the attack, without an assumed direction."),
        ("OPPOSITION_CONTESTS_ATTACK", [("SAME", "ATTACK_OPPORTUNITY"), ("OTHER", "DEFENSIVE_OPPOSITION")],
         "Opponent defence intersects attacking opportunity; no independent double count."),
        ("SHOT_TO_GOAL_CONDITIONAL_PATHWAY", [("SAME", "ATTACK_OPPORTUNITY"), ("SAME", "SHOT_AND_GOAL_CONDITIONAL")],
         "Opportunity together with conversion pathway; no goal is asserted without a shot/event."),
        ("FULL_CONTESTED_GOAL_PATHWAY", [("SAME", "ATTACK_OPPORTUNITY"), ("OTHER", "DEFENSIVE_OPPOSITION"),
                                         ("SAME", "SHOT_AND_GOAL_CONDITIONAL")],
         "Opportunity, opposition and shot-to-goal mechanism jointly represented; qualitative only."),
    ]
    results = []
    for side in ("HOME", "AWAY"):
        other = "AWAY" if side == "HOME" else "HOME"
        for rid, reqs, message in rules:
            evidence = []
            unknown = []
            for who, stage in reqs:
                s = side if who == "SAME" else other
                ids = groups[s].get(stage, [])
                if ids:
                    evidence.append({"team": s, "stage": stage,
                                     "subparameter_id": ids[0], "additional_present": len(ids) - 1})
                else:
                    unknown.append({"team": s, "stage": stage})
            results.append({"rule": rid, "team": side,
                            "status": "CANDIDATE_PATHWAY" if not unknown else "INSUFFICIENT_INPUT",
                            "premises_satisfied": evidence,
                            "missing_premises": unknown,
                            "interpretation": message,
                            "individual_causal_sign_claimed": False,
                            "numeric_weight": None})
    return results

def documentary_joins(graph, statuses):
    # Only declare that two documented concepts were simultaneously selected;
    # a documentary edge is not a transmission of causal effect.
    by_world = defaultdict(list)
    for n in graph["nodes"]:
        for side in ("HOME", "AWAY"):
            if statuses[(n["id"], side)] == "TRUE":
                by_world[(n["parent"], side)].append(n["id"])
    joins = []
    seen = set()
    for e in graph["edges"]:
        source = e["from"]
        if e.get("kind") == "SOURCE_DECLARED_RELATED_WORLD_UNDIRECTED_NOT_CAUSAL":
            target = e.get("to_world")
            if target not in WORLD_STAGE:
                continue
            for side in ("HOME", "AWAY"):
                if statuses[(source, side)] != "TRUE":
                    continue
                for match_id in by_world.get((target, side), ()):
                    pair = (side, source, match_id, e["kind"])
                    if pair in seen:
                        continue
                    seen.add(pair)
                    joins.append({"team": side, "from": source, "to": match_id,
                                  "relation": "DOCUMENTARY_COOCCURRENCE_NOT_CAUSAL",
                                  "original_relation_kind": e["kind"],
                                  "numeric_weight": None})
    return joins

def theoretical_ic(fixture):
    rates = fixture.get("hypothetical_goal_rates")
    if rates is None:
        return {"IC_over15_theoretical_percent": None,
                "reason": "NO_EXPLICIT_GOAL_RATE_ASSUMPTIONS"}
    require(fixture.get("mode") == "LAB_SYNTHETIC", "REAL_GOAL_RATES_NOT_CALIBRATED")
    require(isinstance(rates, dict), "GOAL_RATES_NOT_OBJECT")
    a, b = rates.get("lambda_home"), rates.get("lambda_away")
    require(all(type(v) in (int, float) and math.isfinite(v) and 0 <= v <= 12 for v in (a,b)),
            "GOAL_RATES_INVALID")
    total = a+b
    p = -math.expm1(-total) - total * math.exp(-total)
    return {"IC_over15_theoretical_percent": round(100*p, 6),
            "assumptions": {"lambda_home": a, "lambda_away": b,
                            "model": "EXOGENOUS_INDEPENDENT_POISSON_ONLY"},
            "independent_real_match_validation": False,
            "learned_from_355_source_features": False}

def run(graph, fixture):
    g, evidence, statuses, rows, counts = source_status(graph, fixture)
    joins = documentary_joins(g, statuses)
    paths = stage_paths(g, statuses)
    ic = theoretical_ic(fixture)
    return {"schema": SCHEMA, "fixture_id": fixture["fixture_id"],
            "source_graph_identity": graph.get("schema"),
            "source_children": 355, "worlds": 62,
            "source_documentary_links": 1088, "prematch_two_team_slots": 710,
            "mode": fixture["mode"],
            "counts_by_state": dict(sorted(counts.items())),
            "accepted_observations": len(evidence),
            "documentary_cooccurrences": joins,
            "documentary_cooccurrence_count": len(joins),
            "conditional_pathways": paths,
            "conditional_pathways_supported": sum(r["status"] == "CANDIDATE_PATHWAY" for r in paths),
            "source_edges_causal": False,
            "goal_effect_weights_355": None,
            "IC": ic,
            "scientifically_calibrated_IC": None,
            "real_match_accuracy_validated": False,
            "all_710_slots": rows,
            "uncertainties": ["All 355 original R8 directions and weights remain unsigned.",
                              "Source documentary relations do not establish causality.",
                              "A candidate pathway does not mean a scored goal.",
                              "Without declared quantitative assumptions, numeric IC is unknown."],
            "interpretation": "An explicit inference of logical conjunctions and typed conditional pathways; not a match forecast."}

def write_result(result, out):
    out.mkdir(parents=True, exist_ok=True)
    data = json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    filename = "RESULTAT_MOTEUR_LOGIQUE_R8.json"
    (out / filename).write_bytes(data)
    manifest = {"schema": "MOTEUR_R8_LOGIC_OUTPUT_SHA256",
                "files": {filename: hashlib.sha256(data).hexdigest()},
                "non_calibrated": True,
                "source_count": 355,
                "no_unjustified_effects": True}
    (out / "MANIFEST_SHA256.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return manifest

def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--source-graph", required=True, type=Path)
    a.add_argument("--fixture", required=True, type=Path)
    a.add_argument("--outdir", required=True, type=Path)
    args = a.parse_args()
    result = run(json.loads(args.source_graph.read_text(encoding="utf-8")),
                 json.loads(args.fixture.read_text(encoding="utf-8")))
    write_result(result, args.outdir)
    print(json.dumps({"worlds": result["worlds"], "children": result["source_children"],
                      "documentary_edges": result["source_documentary_links"],
                      "two_team_slots": result["prematch_two_team_slots"],
                      "interactions": result["documentary_cooccurrence_count"],
                      "pathways": result["conditional_pathways_supported"],
                      "IC": result["IC"]}, ensure_ascii=False))
if __name__ == "__main__":
    main()