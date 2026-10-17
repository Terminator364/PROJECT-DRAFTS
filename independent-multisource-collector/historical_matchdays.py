#!/usr/bin/env python3
"""Build historical J1-J6 dossiers, one-shot local task within the single master project.
No network, no external runtime worker, no model inference. Source time != historical PIT time.
"""
from __future__ import annotations
from collections import defaultdict, Counter
from datetime import datetime, date, timezone
import csv
import hashlib
import io
import json
import re
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "02_BCP_COLLECTE" / "TEST_20261017" / "v2"
TARGET = ROOT / "05_JOURNEES" / "HISTORIQUE_J1_J6"
CUT = date(2026, 10, 17)
CODES = {"E0": "PREMIER_LEAGUE", "I1": "SERIE_A"}
GROUPS = {
    "fixture": ["Div","Date","Time","HomeTeam","AwayTeam"],
    "result_90": ["FTHG","FTAG","FTR","HTHG","HTAG","HTR"],
    "shots_xg_post_event": ["HS","AS","HST","AST","HxG","AxG"],
    "discipline_post_event": ["HF","AF","HY","AY","HR","AR"],
    "corners_post_event": ["HC","AC"],
    "referee_identity": ["Referee"],
}
CATEGORY_HINTS = {
    "FIXTURE_ID": ["Div","Date","Time","HomeTeam","AwayTeam"],
    "LEAGUE_BASE": ["FTHG","FTAG","FTR"],
    "TEAM_STRENGTH": ["FTHG","FTAG","HomeTeam","AwayTeam"],
    "SCORING_HISTORY": ["FTHG","FTAG","HTHG","HTAG","FTR"],
    "SHOT_CREATION": ["HS","AS","HST","AST","HxG","AxG"],
    "FORM_TRENDS": ["Date","FTHG","FTAG"],
    "REFEREE": ["Referee"],
    "DISCIPLINE": ["HF","AF","HY","AY","HR","AR"],
    "REST_CONGESTION": ["Date","HomeTeam","AwayTeam"],
    "DATA_QUALITY": ["Date","Div","FTR"],
    "MODEL_DOMAIN": ["Div","Date"],
    "MARKET_SIGNAL": ["B365H","B365D","B365A"],
    "SHOT_QUALITY": ["HxG","AxG"],
    "SHOT_CONVERSION": ["FTHG","FTAG","HS","AS","HxG","AxG"],
    "SHOT_SUPPRESSION": ["HS","AS","HST","AST"],
    "GK_DEFENSE": ["FTHG","FTAG"],
    "GOAL_TIMING": ["HTHG","HTAG","FTHG","FTAG"],
    "SETPIECE_ATTACK": ["HC","AC"],
    "SETPIECE_DEFENSE": ["HC","AC"],
    "PLAY_TIME_RULES": ["FTHG","FTAG"],
}
POSTMATCH = {"FTHG","FTAG","FTR","HTHG","HTAG","HTR","HS","AS","HST","AST",
    "HxG","AxG","HF","AF","HY","AY","HR","AR","HC","AC"}
# Never label odds as PIT-certified: date/issue time/closing provenance absent.
ODDS = re.compile(r"^(B365|BFD|BFE|BV|BW|PP|SKB|Max|Avg|AH)", re.IGNORECASE)

def save(path: Path, item):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".pending")
    temp.write_text(json.dumps(item, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)

def source_date(s):
    for fmt in ("%d/%m/%Y","%d/%m/%y"):
        try: return datetime.strptime(s, fmt).date()
        except ValueError: pass
    raise ValueError("bad_source_date: "+s)

def score(row):
    h,a=int(row["FTHG"]),int(row["FTAG"])
    if h < 0 or a < 0 or row["FTR"]!=("H" if h>a else "A" if a>h else "D"):
        raise ValueError("invalid_or_conflicting_score")
    return h,a

def numeric_optional(value):
    try:
        if value is not None and str(value).strip() != "":
            return float(value)
    except ValueError:
        pass
    return None

def team_history(rows, name, match_date):
    past = [r for r in rows if r["_date"] < match_date and name in (r["HomeTeam"],r["AwayTeam"])]
    past = sorted(past,key=lambda r:(r["_date"],r["HomeTeam"],r["AwayTeam"]))[-5:]
    goals_for=[];goals_against=[];shots=[];xgs=[]
    for r in past:
        home = r["HomeTeam"] == name
        gf,ga = score(r)
        if not home: gf,ga = ga,gf
        goals_for.append(gf);goals_against.append(ga)
        shots.append(numeric_optional(r.get("HS" if home else "AS")))
        xgs.append(numeric_optional(r.get("HxG" if home else "AxG")))
    def avg(xs):
        xs=[v for v in xs if v is not None]
        return round(sum(xs)/len(xs),5) if xs else None
    return {"previous_games_strictly_before_calendar_day":len(past),
            "historical_goals_for_last5_mean":avg(goals_for),
            "historical_goals_against_last5_mean":avg(goals_against),
            "historical_shots_last5_mean":avg(shots),
            "historical_xg_last5_mean":avg(xgs),
            "max_prior_game_date":max((r["_date"].isoformat() for r in past),default=None),
            "target_match_outcome_used":False,
            "same_day_results_used":False,
            "evidence_status":"HISTORICAL_RESEARCH_LAG_ONLY_PUBLICATION_TIME_UNVERIFIED"}

def category_value(field):
    if field in POSTMATCH: return "POST_EVENT_OBSERVATION_NOT_TARGET_PREMATCH_INPUT"
    if ODDS.match(field): return "HISTORICAL_ODDS_UNTIMESTAMPED_NOT_PIT_ADMISSIBLE"
    if field in {"Div","Date","Time","HomeTeam","AwayTeam"}: return "FIXTURE_METADATA_ARCHIVED_AFTER_THE_FACT"
    if field == "Referee": return "OFFICIAL_IDENTITY_ARCHIVED_APPOINTMENT_RELEASE_UNKNOWN"
    return "UNCLASSIFIED_ARCHIVE_FIELD_RESEARCH_ONLY"

def register_families(registry, l3):
    w={x["id"]:x for x in registry["families"]}
    children={x["id"]:x["children"] for x in l3["worlds"]}
    if len(w)!=62 or len(set(w))!=62 or sum(map(len,children.values()))!=109 or len(children)!=20:
        raise ValueError("Registry / L3 contract count mismatch")
    return w,children

def build():
    registry=json.loads((BASE/"matrice_62_registry.json").read_text(encoding="utf-8"))
    l3=json.loads((ROOT/"00_GOUVERNANCE"/"MATRICE_R8_L3_CONTRATS_109.json").read_text(encoding="utf-8"))
    manifest=json.loads((BASE/"integration"/"manifest.json").read_text(encoding="utf-8"))
    worlds,children=register_families(registry,l3)
    global_stats={"schema":"BCP_HISTORICAL_JOURNEES_R8_CROSSWALK_V1",
                  "source_date_cutoff_exclusive":CUT.isoformat(),
                  "generated_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
                  "historical_families":len(worlds),
                  "l3_documented_worlds":len(children),
                  "l3_documented_children":sum(len(c) for c in children.values()),
                  "l3_non_documented_worlds":len(worlds)-len(children),
                  "certified_operational_families":0,
                  "point_in_time_proven":False,
                  "target":str(TARGET), "leagues":{},
                  "caveat":"Post-match actuals are labels/reference data; NEVER pre-match inputs for the same fixture."}
    for code,slug in CODES.items():
        league_archive=json.loads((ROOT/"05_JOURNEES"/(code+"_JOURNEES.json")).read_text(encoding="utf-8"))
        src=manifest["sources"]["2627_"+code]
        raw=(BASE/"integration"/"raw"/(src["sha256"]+".csv")).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=src["sha256"]: raise ValueError("SHA source mismatch "+code)
        original=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
        eligible=[]
        for row in original:
            if row.get("FTHG") is None or not str(row["FTHG"]).strip(): continue
            d=source_date(row["Date"])
            if d>=CUT: continue
            score(row)
            eligible.append({**row,"_date":d})
        look={(r["_date"].isoformat(),r["HomeTeam"],r["AwayTeam"]):r for r in eligible}
        if len(look)!=len(eligible): raise ValueError("duplicated CSV fixtures "+code)
        summary={}
        local_counts=Counter()
        whole_field_counts=Counter()
        for day_no in range(1,7):
            rd=league_archive["by_matchday"].get(str(day_no))
            if rd is None or len(rd["matches"])!=10: raise ValueError("unexpected J1-J6 schedule "+code+str(day_no))
            folder=TARGET/slug/("J%02d"%day_no)
            match_dir=folder/"MATCHS"
            items=[]
            round_field=Counter()
            for fixture in sorted(rd["matches"],key=lambda m:(m["date"],m["home"],m["away"])):
                key=(fixture["date"],fixture["home"],fixture["away"])
                row=look.get(key)
                if row is None: raise ValueError("unreconciled historical fixture "+str(key))
                if fixture["score_football_data"]!=list(score(row)):
                    raise ValueError("score mismatch fixture archive "+str(key))
                d=row["_date"]
                field_values={k:(str(v).strip() if v is not None and str(v).strip() else None)
                              for k,v in row.items() if k!="_date"}
                round_field.update({k:1 for k,v in field_values.items() if v is not None})
                whole_field_counts.update({k:1 for k,v in field_values.items() if v is not None})
                hist_home=team_history(eligible,row["HomeTeam"],d)
                hist_away=team_history(eligible,row["AwayTeam"],d)
                fixture_id="RESEARCH:"+code+":2026-27:"+str(day_no)+":"+d.isoformat()+":"+row["HomeTeam"].replace(" ","_")+":"+row["AwayTeam"].replace(" ","_")
                bundle={
                    "schema":"BCP_HISTORICAL_FIXTURE_H0_POSTMATCH_RESEARCH_V1",
                    "fixture_id":fixture_id,
                    "fixture_id_is_official":False,
                    "competition":slug,"competition_code":code,
                    "season":"2026-27","matchday":day_no,"match_date":d.isoformat(),
                    "teams":{"home":row["HomeTeam"],"away":row["AwayTeam"]},
                    "snapshots":{
                        "H0_ASOF_BEFORE_KICKOFF":{"status":"NOT_RECONSTRUCTED","reason":"No contemporaneous source archive proving what was available at H0"},
                        "AFTER_MATCH_ARCHIVE":{"status":"HISTORICAL_RESEARCH_VALIDATED_BASIC_FIELDS",
                            "result_90_min":{"home_goals":int(row["FTHG"]),"away_goals":int(row["FTAG"]),"label_over15":int(sum(score(row))>=2)},
                            "provider_fields":field_values,
                            "field_availability_semantics":"All match-produced statistics POST_EVENT; bookmaker odds NOT PIT verified",
                            "field_classes":{k:category_value(k) for k in field_values if field_values[k] is not None}}},
                    "chronological_research_features":{
                        "home":hist_home,"away":hist_away,
                        "origin":"past matches only, date strictly before target fixture; sources may have later publication",
                        "admissibility":"UNVERIFIED_PIT_NOT_OPERATIONAL"},
                    "cross_source":{"football_data_score":fixture["score_football_data"],
                                    "openfootball_score":fixture["score_openfootball"],
                                    "comparison_status":fixture["score_status"],
                                    "opening_calendar_snapshot_pit":"NOT_VERIFIED"},
                    "provenance":{
                        "football_data_url":src["url"],"football_data_sha256":src["sha256"],
                        "football_data_collected_at_utc":src["collected_at_utc"],
                        "openfootball_original_hash":league_archive["source_b_sha256"],
                        "original_published_at_utc":None,
                        "historically_available_before_fixture":False,
                        "license_audit":"NOT_COMPLETED"},
                    "usage":{"research_only":True,"training_label_available":True,
                             "may_use_target_result_as_feature":False,
                             "PIT_proven":False,"IC_scoring_permitted":False}}
                filename=d.isoformat()+"_"+re.sub(r"[^A-Za-z0-9]+","_",row["HomeTeam"])+"__"+re.sub(r"[^A-Za-z0-9]+","_",row["AwayTeam"])+".json"
                save(match_dir/filename,bundle)
                items.append({"filename":"MATCHS/"+filename,"fixture_id":fixture_id,
                              "date":d.isoformat(),"home":row["HomeTeam"],"away":row["AwayTeam"],
                              "score":[int(row["FTHG"]),int(row["FTAG"])],
                              "label_over15":int(sum(score(row))>=2),
                              "source_agreement":fixture["score_status"],
                              "home_prior_games":hist_home["previous_games_strictly_before_calendar_day"],
                              "away_prior_games":hist_away["previous_games_strictly_before_calendar_day"]})
            world_cover=[]
            for wid,fam in worlds.items():
                names=CATEGORY_HINTS.get(wid,[])
                filled={f:round_field.get(f,0) for f in names}
                provided=[x for x,n in filled.items() if n>0]
                level=("NOT_MAPPED" if not names else "HISTORICAL_INDIRECT_OR_POST_EVENT_ONLY")
                if wid in ("DATA_QUALITY","FIXTURE_ID","MODEL_DOMAIN"):
                    level="METADATA_RESEARCH_ONLY"
                world_cover.append({"world_id":wid,"world_title":fam.get("title"),
                   "R8_family_status":"OBSERVATION_ONLY","available_archive_field_counts":filled,
                   "field_hints":names,"field_evidence_status":level,
                   "L3_children":[{"id":ch["id"],"research_status":"CONTRACT_ONLY_NOT_CERTIFIED",
                                  "required_inputs":ch["inputs"],
                                  "missing_temporal_proofs":["analysis_asof_utc","original_publisher_issue_utc","source_available_at_T"]}
                                 for ch in children.get(wid,[])],
                   "L3_developed":wid in children,
                   "per_match_PIT_verified":0,"IC_enabled":False})
            if len(world_cover)!=62: raise AssertionError("not 62")
            save(folder/"COUVERTURE_62_ET_L3.json",{
                "competition":slug,"round":day_no,"matches":len(items),
                "parent_families":62,"documented_L3_child_contracts":109,
                "families":world_cover,
                "disclaimer":"World mapped to historical columns is NOT the world operationally implemented."})
            day_report={"competition":slug,"matchday":day_no,
                "period":{"from":min(x["date"] for x in items),"to":max(x["date"] for x in items)},
                "matches":items,"matches_count":len(items),
                "scores_two_sources_agree":sum(x["source_agreement"]=="two_sources_agree" for x in items),
                "scores_source_only":sum(x["source_agreement"]=="score_only_football_data" for x in items),
                "over15_match_count":sum(x["label_over15"] for x in items),
                "observed_field_counts":dict(sorted(round_field.items())),
                "labels_and_training_features":"TRAINING_EXPLORATION_ONLY_PIT_UNVERIFIED",
                "H0_pre_match_archive_present":False,"H0_after_match_archive_present":True,
                "unproven_worlds":62,"certified_worlds":0}
            save(folder/"SOMMAIRE_JOURNEE.json",day_report)
            local_counts.update({"matches":len(items),"two_source":day_report["scores_two_sources_agree"],
                                 "single_source":day_report["scores_source_only"],
                                 "goals_over15":day_report["over15_match_count"]})
            summary["J%02d"%day_no]={k:v for k,v in day_report.items() if k not in ("matches","observed_field_counts")}
        # Reports are reproducible across runs for the same source snapshot.
        global_stats["leagues"][slug]={
            "matchdays_exported":6,"matches_exported":local_counts["matches"],
            "two_source_scores_agree":local_counts["two_source"],
            "single_source_scores":local_counts["single_source"],
            "over15_count":local_counts["goals_over15"],
            "field_nonempty_counts":dict(sorted(whole_field_counts.items())),
            "matchdays":summary,"source_sha256":src["sha256"]}
    assert sum(x["matches_exported"] for x in global_stats["leagues"].values()) == 120
    save(TARGET/"BILAN_GENERAL.json",global_stats)
    print(json.dumps({"target":str(TARGET),"families":62,"l3_children":109,
        "leagues":{k:{"matches":v["matches_exported"],"two_source":v["two_source_scores_agree"],
                      "single_source":v["single_source_scores"],
                      "J1_to_J6":list(v["matchdays"])} for k,v in global_stats["leagues"].items()},
        "certified_ICS":0},ensure_ascii=False))
    return global_stats

if __name__ == "__main__":
    build()
