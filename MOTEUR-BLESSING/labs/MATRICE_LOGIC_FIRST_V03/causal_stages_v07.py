#!/usr/bin/env python3
"""MOTEUR D062: exhaustive 355-child conceptual routing, NOT 355 signed causes.

Seven domain stages are expert-specified from the 62 canonical R8 worlds.
The stages are conceptual pathways, not measured numerical coefficients.
Documented R8 links (1088) are NOT promoted to causal edges.
"""
from __future__ import annotations
from collections import Counter
from typing import Any
import logic_engine_v02 as v02

WORLD_STAGE={
"SOURCE_AND_BOUNDARY":"""FIXTURE_ID LEAGUE_BASE DATA_QUALITY MODEL_DOMAIN MARKET_SIGNAL SOCIAL_MEDIA""",
"TEAM_CAPACITY_CONTEXT":"""TEAM_STRENGTH FORM_TRENDS SQUAD_AVAIL LINEUP_ROTATION COACH_TRANSITION TRANSFERS REST_CONGESTION FATIGUE_INJURY_INTERACTION FITNESS_RETURN TEAM_COHESION TACTICAL_ADAPTABILITY OPPONENT_SPECIFIC_PREPARATION PROMOTION_RELEGATION MOTIVATION_CONTEXT""",
"EXTERNAL_MATCH_CONTEXT":"""REFEREE WEATHER PITCH_STADIUM TRAVEL INTERNATIONAL NEUTRAL_VENUE DISCIPLINE PLAY_TIME_RULES HOME_CROWD_PRESSURE CUP_TIE""",
"ATTACK_OPPORTUNITY":"""SCORING_HISTORY SHOT_CREATION TACTIC_STYLE ATTACK_BUILDUP PRESSING_TURNOVERS TRANSITION_ATTACK SETPIECE_ATTACK ATTACK_DEF_MATCHUP POSSESSION_TERRITORIAL_CONTROL FINAL_THIRD_ACCESS OFF_BALL_MOVEMENT PASSING_COMBINATIONS WIDE_AERIAL_ATTACK INDIVIDUAL_TECHNICAL_EXECUTION ONE_V_ONE_DUELS SECOND_BALL_RECOVERY MATCH_RHYTHM_POTENTIAL GK_BUILDUP_DISTRIBUTION EXPECTED_MATCH_PROCESS UNFORCED_MISTAKE_RISK""",
"DEFENSIVE_OPPOSITION":"""GK_DEFENSE TRANSITION_DEFENSE SHOT_SUPPRESSION SETPIECE_DEFENSE DEFENCE_STRUCTURE""",
"SHOT_AND_GOAL_CONDITIONAL":"""SHOT_QUALITY SHOT_CONVERSION PENALTY_PATHWAYS OWN_GOAL_DEFLECTION_PATHWAYS""",
"FUTURE_SCORE_STATE_BRANCH":"""GOAL_TIMING GAME_STATE_POLICY SUBSTITUTION_IMPACT""",
}
CATEGORIES={k:frozenset(v.split()) for k,v in WORLD_STAGE.items()}
ALL=sum((list(v) for v in CATEGORIES.values()),[])
assert len(ALL)==len(set(ALL))==62
assert set(ALL)==set(v02.core.CANONICAL_WORLDS)
STAGE_BY_WORLD={world:key for key,worlds in CATEGORIES.items() for world in worlds}
STAGE_NOTES={
"SOURCE_AND_BOUNDARY":"Information eligibility, provenance and scope; no direct goal-creating contribution",
"TEAM_CAPACITY_CONTEXT":"Potential constraint on team capability; requires a measured mediator before changing chance rates",
"EXTERNAL_MATCH_CONTEXT":"Potential conditional context: apply only with justified match-specific data",
"ATTACK_OPPORTUNITY":"Possible route towards a shot or dangerous chance, never automatically a goal",
"DEFENSIVE_OPPOSITION":"Opposition prevention/allowance candidate: not a second independent goal process",
"SHOT_AND_GOAL_CONDITIONAL":"Can modify goal chances only conditioned on a preceding shot, penalty or documented event",
"FUTURE_SCORE_STATE_BRANCH":"Unknown future state must remain a counterfactual branch, not a pre-T0 observation",
}
# Explicit conceptual process topology. Each edge is an interpretation to review,
# not an empirical relationship, and is never numerically evaluated.
PROCESS_EDGES=(
("TEAM_CAPACITY_CONTEXT","ATTACK_OPPORTUNITY","CONDITIONAL_MEDIATOR_ONLY"),
("TEAM_CAPACITY_CONTEXT","DEFENSIVE_OPPOSITION","CONDITIONAL_MEDIATOR_ONLY"),
("EXTERNAL_MATCH_CONTEXT","ATTACK_OPPORTUNITY","CONDITIONAL_MEDIATOR_ONLY"),
("EXTERNAL_MATCH_CONTEXT","DEFENSIVE_OPPOSITION","CONDITIONAL_MEDIATOR_ONLY"),
("ATTACK_OPPORTUNITY","SHOT_AND_GOAL_CONDITIONAL","REQUIRES_REAL_SHOT_OR_EVENT"),
("DEFENSIVE_OPPOSITION","ATTACK_OPPORTUNITY","CROSS_TEAM_PREVENTION_NOT_INDEPENDENT"),
("SHOT_AND_GOAL_CONDITIONAL","GOALS","REQUIRES_EXPLICIT_GOAL_RATE_LAW"),
("FUTURE_SCORE_STATE_BRANCH","ATTACK_OPPORTUNITY","COUNTERFACTUAL_ONLY"),
)
GATES=frozenset({"SOURCE_AND_BOUNDARY"})
def route_source_graph(source_graph:dict[str,Any])->dict[str,Any]:
    if source_graph.get("worlds")!=62 or source_graph.get("documentary_subparameters")!=355:
        raise ValueError("WRONG_R8_SOURCE_GRAPH")
    entries=source_graph.get("nodes")
    if not isinstance(entries,list) or len(entries)!=355:
        raise ValueError("ALL_355_SOURCE_NODES_REQUIRED")
    if len({r["id"] for r in entries})!=355:raise ValueError("DUPLICATE_R8_CHILD")
    world_counts=Counter()
    stage_counts=Counter()
    all_nodes=[]
    for r in entries:
        cid=r["id"];parent=r["parent"]
        if cid.split(".",1)[0]!=parent or parent not in STAGE_BY_WORLD:
            raise ValueError("INVALID_WORLD_CHILD:"+str(cid))
        if r.get("direction_of_goal_effect")!="UNESTABLISHED" or r.get("IC_effect") is not None:
            raise ValueError("UNAUTHORIZED_GOAL_EFFECT:"+cid)
        stage=STAGE_BY_WORLD[parent]
        stage_counts[stage]+=1
        world_counts[parent]+=1
        all_nodes.append({"id":cid,"world":parent,
                          "conceptual_stage":stage,
                          "semantic_review":"NOT_COMPLETED_FOR_CAUSAL_DIRECTION",
                          "causal_effect_sign":None,
                          "numeric_effect":None,
                          "source_name":r.get("name_source"),
                          "source_definition_present":bool(r.get("definition_source")),
                          "source_origin":r.get("source_origin")})
    if len(world_counts)!=62:raise ValueError("NOT_ALL_62_WORLDS")
    uncertain=source_graph.get("unresolved_source_references",[])
    if not isinstance(uncertain,list):raise ValueError("INVALID_UNRESOLVED_REFERENCE_LIST")
    return {"schema":"MOTEUR_D062_ALL_355_CONCEPTUAL_STAGE_GRAPH",
            "worlds":62,"children_in_stage_routing":355,
            "documentary_edge_count":len(source_graph.get("edges",[])),
            "unresolved_documentary_references":uncertain,
            "stage_counts":dict(sorted(stage_counts.items())),
            "world_child_counts":dict(sorted(world_counts.items())),
            "conceptual_stages":STAGE_NOTES,
            "conceptual_process_edges":[{"source":a,"destination":b,"constraint":c,"causality_validated":False}
                                        for a,b,c in PROCESS_EDGES],
            "all_children":all_nodes,
            "signed_per_child_goal_effects":0,
            "goal_probability_law_from_355":None,
            "status":"EXHAUSTIVE_CONCEPTUAL_CLASSIFICATION_NOT_CAUSAL_CALIBRATION"}

def main():
    from pathlib import Path
    import argparse,json
    p=argparse.ArgumentParser()
    p.add_argument("--source-graph",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    obj=route_source_graph(json.loads(a.source_graph.read_text(encoding="utf8")))
    a.out.write_text(json.dumps(obj,sort_keys=True,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"worlds":62,"source_children":355,"stages":obj["stage_counts"],
                      "source_edges":obj["documentary_edge_count"],"IC_calibrated":None},sort_keys=True))
if __name__=="__main__":main()
