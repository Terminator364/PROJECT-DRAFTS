#!/usr/bin/env python3
"""MOTEUR D066: leakage-resistant, zero-budget team/league Poisson historical baseline.

A narrow empirical *baseline* from legally held finished historical games. NOT
an estimate of each of the 355 R8 document-source effects. Never manufacture
fixtures, result records, source timestamps or performance claims.

Input rows: fixture_id, home_team, away_team, kickoff_utc,
 final_whistle_utc, source_issued_utc, source_first_seen_utc, home_goals,
 away_goals. Each timestamp should have explicit timezone. The result must be
 published and FIRST seen before analysis cutoff; no target-match results.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from math import isfinite, log
import json
from pathlib import Path
from typing import Any
from theoretical_ic_v08 import poisson_over15
from logic_engine_v02 import core

class HistoricalEvidenceError(ValueError): pass

REQUIRED=("fixture_id","home_team","away_team","kickoff_utc",
          "final_whistle_utc","source_issued_utc","source_first_seen_utc",
          "home_goals","away_goals")
MAX_GOALS=20
def _date(row:dict[str,Any], field:str)->datetime:
    try:return core.iso(row[field])
    except (ValueError,KeyError,TypeError) as exc:
        raise HistoricalEvidenceError("INVALID_EVIDENCE_TIMESTAMP:"+field) from exc

def _check_games(games:list[dict[str,Any]])->list[dict[str,Any]]:
    if not isinstance(games,list):raise HistoricalEvidenceError("HISTORICAL_GAMES_LIST_REQUIRED")
    verified=[];ids=set()
    for game in games:
        if not isinstance(game,dict) or any(k not in game for k in REQUIRED):
            raise HistoricalEvidenceError("INCOMPLETE_HISTORICAL_MATCH")
        fid=game["fixture_id"]
        if not isinstance(fid,str) or not fid or fid in ids:raise HistoricalEvidenceError("DUPLICATE_OR_EMPTY_FIXTURE_ID")
        ids.add(fid)
        if (not isinstance(game["home_team"],str) or not game["home_team"] or
            not isinstance(game["away_team"],str) or not game["away_team"] or
            game["home_team"]==game["away_team"]):
            raise HistoricalEvidenceError("INVALID_TEAM_IDS")
        a=game["home_goals"];b=game["away_goals"]
        if any(isinstance(x,bool) or not isinstance(x,int) or x<0 or x>MAX_GOALS for x in (a,b)):
            raise HistoricalEvidenceError("INVALID_GOALS")
        kick=_date(game,"kickoff_utc")
        final=_date(game,"final_whistle_utc")
        issued=_date(game,"source_issued_utc")
        first=_date(game,"source_first_seen_utc")
        if not (kick<final<=issued<=first):
            raise HistoricalEvidenceError("INVALID_HISTORICAL_EVENT_PROVENANCE")
        if game.get("synthetic") is True or game.get("target_match_inplay") is True:
            raise HistoricalEvidenceError("NO_SYNTHETIC_OR_INPLAY_TRAINING")
        verified.append({**game,"_kick":kick,"_first":first,"_issued":issued})
    return verified

def _fixture(case:dict[str,Any])->tuple[datetime,datetime]:
    if not isinstance(case,dict) or any(k not in case for k in ("fixture_id","home_team","away_team","analysis_asof_utc","kickoff_utc")):
        raise HistoricalEvidenceError("PREMATCH_FIXTURE_REQUIRED")
    if not all(isinstance(case[k],str) and case[k] for k in ("fixture_id","home_team","away_team")):
        raise HistoricalEvidenceError("BAD_FIXTURE_ID")
    if case["home_team"]==case["away_team"]:raise HistoricalEvidenceError("SAME_TEAM_NOT_A_FIXTURE")
    try:
        asof=core.iso(case["analysis_asof_utc"]);kick=core.iso(case["kickoff_utc"])
    except (ValueError,KeyError,TypeError) as exc:raise HistoricalEvidenceError("INVALID_FIXTURE_CLOCK") from exc
    if not asof<kick:raise HistoricalEvidenceError("TARGET_CUTOFF_NOT_BEFORE_KICKOFF")
    return asof,kick

def predict(case:dict[str,Any],all_history:list[dict[str,Any]],
            *,minimum_games:int=30,prior_strength:float=8.0)->dict[str,Any]:
    cutoff,kick=_fixture(case)
    if isinstance(minimum_games,bool) or not isinstance(minimum_games,int) or minimum_games<1:
        raise HistoricalEvidenceError("INVALID_MINIMUM_HISTORY")
    if isinstance(prior_strength,bool) or not isinstance(prior_strength,(int,float)) or not isfinite(float(prior_strength)) or prior_strength<=0:
        raise HistoricalEvidenceError("INVALID_PRIOR_STRENGTH")
    recorded=_check_games(all_history)
    eligible=[g for g in recorded if
              g["fixture_id"]!=case["fixture_id"] and
              g["_kick"]<kick and
              g["_first"]<=cutoff and
              _date(g,"final_whistle_utc")<=cutoff]
    # Exclude later historical records rather than secretly retro-fitting data.
    excluded=len(recorded)-len(eligible)
    home=case["home_team"];away=case["away_team"]
    template={"schema":"MOTEUR_D066_CHRONOLOGICAL_TEAM_GOALS_BASELINE",
              "fixture_id":case["fixture_id"],"home_team":home,"away_team":away,
              "analysis_asof_utc":case["analysis_asof_utc"],
              "source_games_total":len(recorded),"eligible_games":len(eligible),
              "excluded_late_or_target_games":excluded,
              "minimum_history":minimum_games,
              "evidence_synthetic":False,
              "R8_children_assigned_nonzero_coefficients":0,
              "P_over15":None,"IC_over15_percent":None,
              "lambda_home":None,"lambda_away":None,
              "calibration_verified":False,
              "predictive_accuracy_percent":None}
    if len(eligible)<minimum_games:
        return {**template,"status":"ABSTAIN_NOT_ENOUGH_PIT_HISTORICAL_MATCHES"}
    hh=[x for x in eligible if x["home_team"]==home]
    aa=[x for x in eligible if x["away_team"]==away]
    # Both target teams need histories; otherwise league-only guess would
    # silently be misrepresented as team-specific inference.
    if not hh or not aa:
        return {**template,"status":"ABSTAIN_NO_BOTH_TEAM_HISTORIES"}
    n=len(eligible)
    league_home=sum(x["home_goals"] for x in eligible)/n
    league_away=sum(x["away_goals"] for x in eligible)/n
    if league_home<=0 or league_away<=0:
        return {**template,"status":"ABSTAIN_NO_NONZERO_GOAL_BASELINE"}
    # Attack is scored goals, defense is conceded goals, location-adjusted and
    # shrunk against league baseline. These are simple estimator assumptions,
    # NOT empirically learned causal effects from the 355 R8 contracts.
    k=float(prior_strength)
    home_attack=(sum(x["home_goals"] for x in hh)+k*league_home)/(len(hh)+k)/league_home
    away_defense=(sum(x["home_goals"] for x in aa)+k*league_home)/(len(aa)+k)/league_home
    away_attack=(sum(x["away_goals"] for x in aa)+k*league_away)/(len(aa)+k)/league_away
    home_defense=(sum(x["away_goals"] for x in hh)+k*league_away)/(len(hh)+k)/league_away
    lam_h=league_home*home_attack*away_defense
    lam_a=league_away*away_attack*home_defense
    result=poisson_over15(lam_h,lam_a)
    return {**template,"status":"BASELINE_PREMATCH_ESTIMATE_UNVALIDATED",
            "training_matches":len(eligible),"target_home_games_in_training":len(hh),
            "target_away_games_in_training":len(aa),
            "base_league_home_goals":league_home,"base_league_away_goals":league_away,
            "prior_strength":k,
            "lambda_home":lam_h,"lambda_away":lam_a,
            "P_over15":result["P_over_1_5_goals"],
            "IC_over15_percent":result["IC_over15_theoretical_percent"],
            "validation_scope":"NOT_A_CALIBRATION_OR_BACKTEST_RESULT",
            "source_coverage":"ONLY_HISTORIC_FINAL_SCORES_NO_355_EFFECTS"}

def walkforward(matches:list[dict[str,Any]],*,minimum_games:int=30,
                prior_strength:float=8.0)->dict[str,Any]:
    """Every prediction has a real temporal exclusion boundary.
    This is an evaluation procedure; it never calls its own fit 'calibrated'.
    """
    games=_check_games(matches)
    out=[]
    for g in sorted(games,key=lambda x:(x["_kick"],x["fixture_id"])):
        case={"fixture_id":g["fixture_id"],"home_team":g["home_team"],"away_team":g["away_team"],
              "kickoff_utc":g["kickoff_utc"],
              "analysis_asof_utc":g["kickoff_utc"]}
        # Predictor requires strict cutoff BEFORE kickoff: evaluate as of one
        # microsecond before kickoff; this prevents target-game leakage.
        t=g["_kick"]-__import__("datetime").timedelta(microseconds=1)
        case["analysis_asof_utc"]=t.isoformat()
        p=predict(case,matches,minimum_games=minimum_games,prior_strength=prior_strength)
        if p["P_over15"] is None:continue
        y=int(g["home_goals"]+g["away_goals"]>=2)
        out.append({"fixture_id":g["fixture_id"],"p":p["P_over15"],
                    "outcome_over15":y,"asof_utc":case["analysis_asof_utc"]})
    if not out:
        return {"schema":"MOTEUR_D066_WALKFORWARD","test_predictions":0,
                "status":"NO_ELIGIBLE_OUT_OF_TIME_TESTS","brier":None,"logloss":None,
                "independent_external_validation":False}
    brier=sum((q["p"]-q["outcome_over15"])**2 for q in out)/len(out)
    ll=-sum(q["outcome_over15"]*log(max(q["p"],1e-12))+
             (1-q["outcome_over15"])*log(max(1-q["p"],1e-12)) for q in out)/len(out)
    return {"schema":"MOTEUR_D066_WALKFORWARD","test_predictions":len(out),
            "brier":brier,"logloss":ll,
            "observed_over15_rate":sum(q["outcome_over15"] for q in out)/len(out),
            "mean_predicted_over15":sum(q["p"] for q in out)/len(out),
            "status":"RETROSPECTIVE_WALKFORWARD_NOT_PROOF_OF_INDEPENDENT_VALIDATION",
            "independent_external_validation":False,
            "per_fixture":out}

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--history",type=Path,required=True)
    ap.add_argument("--fixture",type=Path)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--min-games",type=int,default=30)
    ap.add_argument("--walkforward",action="store_true")
    a=ap.parse_args()
    games=json.loads(a.history.read_text(encoding="utf8"))
    if a.walkforward:
        if a.fixture:ap.error("--fixture is incompatible with --walkforward")
        result=walkforward(games,minimum_games=a.min_games)
    else:
        if not a.fixture:ap.error("--fixture is required without --walkforward")
        result=predict(json.loads(a.fixture.read_text(encoding="utf8")),games,minimum_games=a.min_games)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({key:result.get(key) for key in ("schema","status","eligible_games","test_predictions","IC_over15_percent")}))
if __name__=="__main__":main()
