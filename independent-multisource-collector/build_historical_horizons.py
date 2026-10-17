#!/usr/bin/env python3
"""Historical as-of horizon candidate ledger. Date-only research placeholders, NOT PIT.

Creates J-6/J-4/J-3/J-1/H-1/H0 as-of training *skeletons* per match.
Never includes target match's outcome as a feature, and never asserts
a historical source was published at that horizon without timestamp proof.
"""
import argparse
from collections import defaultdict
from datetime import date,timedelta,datetime,timezone
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
LIBRARY=ROOT/"05_JOURNEES"/"HISTORIQUE_J1_ACTUEL"
OFFSETS=(("J_MINUS_6",6),("J_MINUS_4",4),("J_MINUS_3",3),("J_MINUS_1",1))
NOTES="MATCH_DATE_ONLY: eligible is based solely on past match dates; original data publication times missing"
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")

def load(code):
    result=[]
    for d in range(1,39):
        f=LIBRARY/code/("J%02d"%d)/"matchday.json"
        if not f.exists(): continue
        p=json.loads(f.read_text(encoding="utf-8"))
        result.extend(p["matches"])
    result.sort(key=lambda v:(v["prematch_identity_observed_in_current_archive"]["date"],
                              v["fixture_key_local"]))
    return result

def prior_ids(matches,target,asof_day):
    team=target["prematch_identity_observed_in_current_archive"]["home"]
    opponent=target["prematch_identity_observed_in_current_archive"]["away"]
    def eligible(r):
        date_r=date.fromisoformat(r["prematch_identity_observed_in_current_archive"]["date"])
        if not date_r<asof_day:return False
        return r["fixture_key_local"]!=target["fixture_key_local"]
    return {
       "home_team_history_candidates":[r["fixture_key_local"] for r in matches
              if eligible(r) and team in (
                r["prematch_identity_observed_in_current_archive"]["home"],
                r["prematch_identity_observed_in_current_archive"]["away"])],
       "away_team_history_candidates":[r["fixture_key_local"] for r in matches
              if eligible(r) and opponent in (
                r["prematch_identity_observed_in_current_archive"]["home"],
                r["prematch_identity_observed_in_current_archive"]["away"])],
       "league_history_candidate_count":sum(eligible(r) for r in matches)
    }

def build():
    stats={}
    for code in ("E0","I1"):
        games=load(code)
        if len(games)!=60:
            raise ValueError(code+" unexpected expected historical training targets "+str(len(games)))
        days=defaultdict(list)
        for r in games:
            target_date=date.fromisoformat(r["prematch_identity_observed_in_current_archive"]["date"])
            horizons=[]
            for name,offset in OFFSETS:
                day=target_date-timedelta(days=offset)
                historical=prior_ids(games,r,day)
                horizons.append({
                    "horizon":name,"calendar_cutoff_date_exclusive":day.isoformat(),
                    "utc_asof_instant":None,
                    "asof_certification":"NOT_CERTIFIED_MISSING_SOURCE_PUBLICATION_PROOF",
                    "candidate_training_history":historical,
                    "unknown_in_history":"all source publication and availability at horizon",
                    "target_game_final_score_in_inputs":False,
                    "source_calendar_availability_assumed":False
                })
            for stage in ("H_MINUS_1","H0_KICKOFF"):
                hist=prior_ids(games,r,target_date)
                horizons.append({
                    "horizon":stage,
                    "calendar_cutoff_date_exclusive":target_date.isoformat(),
                    "utc_asof_instant":None,
                    "asof_certification":"NOT_CERTIFIED_MATCH_TIMEZONE_AND_PUBLICATION_UNVERIFIED",
                    "candidate_training_history":hist,
                    "target_game_final_score_in_inputs":False,
                    "source_calendar_availability_assumed":False,
                    "warning":"H0 kickoff != final whistle; no target in-game/postgame observations allowed"
                })
            days[r["matchday"]].append({
                "fixture_key_local":r["fixture_key_local"],
                "matchdate":target_date.isoformat(),
                "horizons":horizons,
                "outcome_pointer":r["fixture_key_local"],
                "outcome_must_be_fetched_separately_for_supervised_label":True,
                "pit_certification":False
            })
        for day,rows in days.items():
            write(LIBRARY/code/("J%02d"%day)/"REPLAY_HORIZONS_RECHERCHE.json",{
                "league":code,"matchday":day,
                "date_only_design_not_historical_point_in_time":True,
                "asof_notes":NOTES,
                "training_target_count":len(rows),
                "horizon_records":rows,
                "sealed_target_outcome_feature":False
            })
        stats[code]={"matches":len(games),"matchdays":len(days),
            "horizons":len(games)*6,
            "source_available_at_verified":False}
    final={"schema":"BCP_HISTORICAL_REPLAY_HORIZONS_DRAFT_V1",
           "produced_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "status":"RESEARCH_DESIGN_ONLY_NOT_PIT_CERTIFIED",
           "horizons":["J_MINUS_6","J_MINUS_4","J_MINUS_3","J_MINUS_1","H_MINUS_1","H0_KICKOFF"],
           "matches_total":sum(v["matches"] for v in stats.values()),
           "horizon_records_total":sum(v["horizons"] for v in stats.values()),
           "leagues":stats,
           "postgame_outcome_never_in_target_features":True,
           "warning":"History selection by match date does not establish historical publication availability."
    }
    write(LIBRARY/"INDEX_HORIZONS_NON_CERTIFIES.json",final)
    return final

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    v=p.parse_args()
    data=build()
    print(json.dumps(data,indent=2,ensure_ascii=False))
