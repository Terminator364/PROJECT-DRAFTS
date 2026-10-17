#!/usr/bin/env python3
"""BCP independent historical library exporter — two pilot leagues, matchday by matchday.
No HTTP, no running worker, no IC calculation. Keeps post-match observations separate
from pre-match metadata, and records missing PIT publication evidence explicitly.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
from datetime import date, datetime, timezone
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
MASTER_ROOT=ROOT
DATA_ROOT=ROOT/"02_BCP_COLLECTE"/"TEST_20261017"/"v2"
FULLTIME={"FTHG","FTAG","FTR","HTHG","HTAG","HTR"}
SHOTS={"HS","AS","HST","AST","HxG","AxG","HC","AC"}
DISCIPLINE={"HF","AF","HY","AY","HR","AR"}
BASIC={"Date","Time","Div","HomeTeam","AwayTeam","Referee"}
FIELDS={
 "FIXTURE_ID": BASIC,
 "LEAGUE_BASE": FULLTIME,
 "TEAM_STRENGTH": FULLTIME,
 "SCORING_HISTORY": FULLTIME,
 "SHOT_CREATION": SHOTS,
 "FORM_TRENDS": FULLTIME,
 "GK_DEFENSE": {"FTHG","FTAG"},
 "REFEREE": {"Referee"},
 "REST_CONGESTION": {"Date"},
 "DISCIPLINE": DISCIPLINE,
 "MARKET_SIGNAL": {"B365H","B365D","B365A","B365>2.5","B365<2.5"},
 "GOAL_TIMING": {"HTHG","HTAG","HTR"},
 "DATA_QUALITY": {"Date","FTR"},
 "MODEL_DOMAIN": {"Div"},
 "SHOT_QUALITY": {"HxG","AxG"},
 "SHOT_CONVERSION": {"HxG","AxG","FTHG","FTAG","HS","AS"},
 "SHOT_SUPPRESSION": {"HS","AS","HST","AST"},
 "SETPIECE_ATTACK": {"HC","AC"},
 "SETPIECE_DEFENSE": {"HC","AC"}
}
# Presence of a column is NOT enough to activate a scientific parameter.
PROXY_ONLY={"TEAM_STRENGTH","FORM_TRENDS","GK_DEFENSE","REST_CONGESTION",
           "GOAL_TIMING","SHOT_QUALITY","SHOT_CONVERSION","SHOT_SUPPRESSION",
           "SETPIECE_ATTACK","SETPIECE_DEFENSE"}
DESIGN_ID="R8_62_FROZEN_L3_RESEARCH_ONLY"


def serialize(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
                    encoding="utf-8")


def parse_date(raw):
    for fmt in ("%d/%m/%Y","%d/%m/%y"):
        try:
            return datetime.strptime(str(raw).strip(),fmt).date()
        except ValueError:
            continue
    raise ValueError("invalid date "+str(raw))


def clean(value):
    if value is None: return None
    value=str(value).strip()
    return value if value else None


def numeric_or_raw(name, value):
    if value is None: return None
    if name in {"FTHG","FTAG","HTHG","HTAG","HS","AS","HST","AST","HC","AC",
                "HF","AF","HY","AY","HR","AR"}:
        try:
            return int(value)
        except ValueError:
            return value
    if name in {"HxG","AxG","B365H","B365D","B365A","B365>2.5","B365<2.5"}:
        try:
            return float(value)
        except ValueError:
            return value
    return value


def cutoff_context(day,cutoff):
    # Match date is known; source publisher issue time was NOT captured by historical CSV.
    return {"match_date":day.isoformat(),"cutoff_exclusive":cutoff.isoformat(),
            "historical_publication_at":None,"historical_available_at":None,
            "historical_asof_replay_certified":False,
            "snapshot_captured_now_not_proof_of_prior_access":True}


def make_family_inventory(registry, available_columns, empirical_count):
    result=[]
    for family in registry["families"]:
        fid=family["id"]
        candidates=sorted(FIELDS.get(fid,set()))
        observed=[x for x in candidates if x in available_columns]
        data_evidence=("HISTORICAL_OBSERVATIONS" if observed and fid not in PROXY_ONLY
                       else "HISTORICAL_PROXY_ONLY" if observed else "NOT_IN_THIS_DATASET")
        result.append({"family_id":fid,"family_name":family["title"],
                       "candidate_fields":candidates,"fields_present_in_archive":observed,
                       "observed_match_count":empirical_count if observed else 0,
                       "evidence_level":data_evidence,
                       "prematch_PIT_certified":False,"ic_eligible":False,
                       "warning":"Field presence is not evidence of a validated R8 mechanism"})
    return result


def make_record(csv_match,matchday,cutoff,sha,code):
    raw_values=csv_match["raw"]
    match_date=date.fromisoformat(csv_match["date"])
    # An archive historical outcome is a learning label, NEVER the pre-kickoff state.
    outcome={x:numeric_or_raw(x,clean(raw_values.get(x))) for x in sorted(
        (FULLTIME|SHOTS|DISCIPLINE|{"B365H","B365D","B365A","B365>2.5","B365<2.5"}) )}
    hg,ag=outcome["FTHG"],outcome["FTAG"]
    if not isinstance(hg,int) or not isinstance(ag,int):
        raise ValueError("Historic match lacks numeric full-time scores")
    label=int(hg+ag>=2)
    return {
      "fixture_key_local":f"{code}|2026-27|J{matchday}|{match_date}|{csv_match['home']}|{csv_match['away']}",
      "fixture_id_official":None,"competition":code,"season":"2026-27",
      "matchday":matchday,
      "prematch_identity_observed_in_current_archive":{
          "date":csv_match["date"],"time_provider_no_timezone":clean(raw_values.get("Time")),
          "home":csv_match["home"],"away":csv_match["away"],
          "stated_referee_if_any":clean(raw_values.get("Referee")),
          "pre_match_publisher_issue_utc":None
       },
      "outcome_known_only_after_game":{"full_time_goals":[hg,ag],
          "over15_fulltime_training_label":label,
          "full_time_score_label_not_a_feature":True,
          "observed_match_statistics":outcome,
          "all_source_columns":{k:numeric_or_raw(k,clean(v)) for k,v in raw_values.items()
                                if k is not None},
          "raw_source_sha256":sha},
      "source_and_asof":cutoff_context(match_date,cutoff),
      "intended_use":"HISTORICAL_MATERIAL_FOR_DESIGN_AND_TRAINING_NOT_CERTIFIED_PIT_INPUT",
      "calibrated_prediction":False
    }


def build(cutoff=date(2026,10,17), output=None, base=ROOT):
    if output is None:output=base/"05_JOURNEES"/"HISTORIQUE_J1_ACTUEL"
    archive=base/"02_BCP_COLLECTE"/"TEST_20261017"/"v2"
    meta=json.loads((archive/"integration"/"manifest.json").read_text(encoding="utf-8"))
    frozen=json.loads((archive/"matrice_62_registry.json").read_text(encoding="utf-8"))
    L3file=base/"00_GOUVERNANCE"/"matrice_r8_l3_index_2026-10-17.json"
    L3=json.loads(L3file.read_text(encoding="utf-8")) if L3file.exists() else {"worlds":[],"children_count":0}
    if len(frozen.get("families",[]))!=62:raise ValueError("Frozen registry count differs from 62")
    root=Path(output)
    summaries={}
    total_matches=0
    errors=[]
    for code,league_name in (("E0","Premier League"),("I1","Serie A")):
        key="2627_"+code
        src=meta["sources"][key]
        path=archive/"integration"/"raw"/(src["sha256"]+".csv")
        raw=path.read_bytes()
        digest=hashlib.sha256(raw).hexdigest()
        if digest!=src["sha256"]:raise ValueError("SHA256 mismatch "+key)
        reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig",errors="replace")))
        if not {"Date","HomeTeam","AwayTeam","FTHG","FTAG","FTR"}<=set(reader.fieldnames or []):
            raise ValueError("CSV incomplete "+key)
        by_key={}
        historical=[]
        for row in reader:
            try:
                day=parse_date(row.get("Date",""))
                if day>=cutoff:continue
                home=clean(row.get("HomeTeam"))
                away=clean(row.get("AwayTeam"))
                hg=int(row["FTHG"]);ag=int(row["FTAG"])
                result="H" if hg>ag else "A" if ag>hg else "D"
                if not home or not away or home==away or row["FTR"]!=result:raise ValueError("invalid result")
                keymatch=(day.isoformat(),home,away)
                if keymatch in by_key:raise ValueError("duplicate fixture")
                entry={"date":day.isoformat(),"home":home,"away":away,"raw":row}
                by_key[keymatch]=entry
                historical.append(entry)
            except (ValueError,TypeError,KeyError) as exc:
                errors.append({"league":code,"reason":str(exc),"date":row.get("Date")})
        matchday_report=json.loads((base/"05_JOURNEES"/(code+"_JOURNEES.json")).read_text(encoding="utf-8"))
        counts=collections.Counter()
        daysets=[]
        used=set()
        for round_idx in range(1,39):
            round_payload=matchday_report["by_matchday"].get(str(round_idx))
            if not round_payload:continue
            ready=[]
            missing=[]
            for fixture in round_payload["matches"]:
                k=(fixture["date"],fixture["home"],fixture["away"])
                if date.fromisoformat(fixture["date"])>=cutoff:continue
                if k in by_key:
                    ready.append(make_record(by_key[k],round_idx,cutoff,digest,code))
                    if k in used:raise ValueError("reused fixture "+str(k))
                    used.add(k)
                else:
                    missing.append({"date":fixture["date"],"home":fixture["home"],
                                    "away":fixture["away"],"official_fixture_id":None,
                                    "result":"MISSING_OR_NOT_YET_SOURCE_VERIFIED",
                                    "never_infer_zero_goals":True})
            if not ready and not missing:continue
            round_doc={
                "league":league_name,"code":code,"season":"2026-27","matchday":round_idx,
                "status":"HISTORICAL_RESEARCH_ONLY","cutoff_exclusive":cutoff.isoformat(),
                "completed_matches_in_archives":len(ready),"missing_results_before_cutoff":len(missing),
                "source_sha256":digest,"prematch_replay_certified":False,
                "postgame_observations_are_labels_not_same_match_features":True,
                "matches":ready,"unresolved":missing
            }
            serialize(root/code/("J%02d"%round_idx)/"matchday.json",round_doc)
            counts[round_idx]=len(ready)
            daysets.append({"matchday":round_idx,"completed":len(ready),"unresolved":len(missing)})
        orphan=sorted(set(by_key)-used)
        if orphan:raise ValueError("Unmapped historical fixtures "+str(orphan[:3]))
        inventory=make_family_inventory(frozen,set(reader.fieldnames or []),len(historical))
        l3_report=[{"parent":w["id"],"children":w["children"],
                    "candidate_fields_present": sorted(set(FIELDS.get(w["id"],set())) & set(reader.fieldnames or [])),
                    "feature_PIT_verified":False}
                   for w in L3["worlds"]]
        serialize(root/code/"family_62_coverage.json",{
            "status":"DESCRIPTIVE_RESEARCH_ONLY","family_count":62,
            "l3_documented_family_count":len(l3_report),
            "l3_documented_subparam_count":sum(len(w["children"]) for w in l3_report),
            "parent_families":inventory,"l3_subparameters":l3_report
        })
        summaries[code]={"competition":league_name,"count_historical":len(historical),
                         "families":62,"l3_mapped_from_repository":sum(len(w["children"]) for w in l3_report),
                         "per_matchday":daysets,"raw_csv_sha256":digest,
                         "total_columns":len(reader.fieldnames or [])}
        total_matches+=len(historical)
    summary={"schema":"COLLECTEUR_BIBLIOTHEQUE_HISTORIQUE_JOURNEES_V1",
             "compiled_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "cutoff_exclusive":cutoff.isoformat(),
             "scope":"2 favorite competitions, first matchdays through before cutoff",
             "historical_matches":total_matches,"leagues":summaries,
             "registry_62_status":"OBSERVATION_ONLY",
             "l3_documented_children_in_index":L3.get("children_count",0),
             "validation":"no historical provider publication time / not certified PIT",
             "source_errors":errors,
             "recency_warning":"Today and later not included even if source says result",
             "prediction_ic_enabled":False}
    serialize(root/"INDEX_HISTORIQUE.json",summary)
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cutoff",default="2026-10-17")
    args=p.parse_args()
    result=build(cutoff=date.fromisoformat(args.cutoff))
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
