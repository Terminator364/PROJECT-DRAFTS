#!/usr/bin/env python3
"""BCP - two-league historical matchday reconciliation pilot. Local files only.

This tool never calls a sports website. Source A is a cached Football-Data CSV.
Source B is an OpenFootball JSON snapshot explicitly transferred to this PC.
Matches on/after the cut-off date receive no finalized results or pre-match inputs.
"""
import argparse
import collections
import csv
from datetime import date, datetime, timezone
import hashlib
import io
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
LEAGUES={"E0": ("Premier League", "en.1"), "I1": ("Serie A", "it.1")}
# Exact mapping: no guess from fuzzy team names.
ALIASES={
"AFC Bournemouth":"Bournemouth","Arsenal FC":"Arsenal","Aston Villa FC":"Aston Villa",
"Brentford FC":"Brentford","Brighton & Hove Albion FC":"Brighton",
"Chelsea FC":"Chelsea","Coventry City FC":"Coventry","Crystal Palace FC":"Crystal Palace",
"Everton FC":"Everton","Fulham FC":"Fulham","Hull City AFC":"Hull",
"Ipswich Town FC":"Ipswich","Leeds United FC":"Leeds","Liverpool FC":"Liverpool",
"Manchester City FC":"Man City","Manchester United FC":"Man United",
"Newcastle United FC":"Newcastle","Nottingham Forest FC":"Nott'm Forest",
"Sunderland AFC":"Sunderland","Tottenham Hotspur FC":"Tottenham",
"AC Milan":"Milan","AC Monza":"Monza","ACF Fiorentina":"Fiorentina",
"AS Roma":"Roma","Atalanta BC":"Atalanta","Bologna FC 1909":"Bologna",
"Cagliari Calcio":"Cagliari","Como 1907":"Como",
"FC Internazionale Milano":"Inter","Frosinone Calcio":"Frosinone",
"Genoa CFC":"Genoa","Juventus FC":"Juventus","Parma Calcio 1913":"Parma",
"SS Lazio":"Lazio","SSC Napoli":"Napoli","Torino FC":"Torino",
"Udinese Calcio":"Udinese","US Lecce":"Lecce",
"US Sassuolo Calcio":"Sassuolo","Venezia FC":"Venezia"
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def json_save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
                    encoding="utf-8")

def csv_date(d):
    for fmt in ("%d/%m/%Y","%d/%m/%y"):
        try: return datetime.strptime(d.strip(),fmt).date()
        except ValueError: pass
    raise ValueError("CSV invalid date")

def external_score(score):
    if isinstance(score,dict):
        v=score.get("ft")
    else:
        v=score
    if isinstance(v,list) and len(v)==2 and all(isinstance(x,int) and x>=0 for x in v):
        return v
    return None

def run(csv_bytes,open_bytes,code,cutoff):
    a=list(csv.DictReader(io.StringIO(csv_bytes.decode("utf-8-sig"))))
    b=json.loads(open_bytes.decode("utf-8-sig"))
    if len(a)<1 or not isinstance(b.get("matches"),list):
        raise ValueError("Missing source rows")
    compiled=[]
    unmatched_aliases=set()
    b_keys=set()
    b_by_key={}
    for item in b["matches"]:
        home=ALIASES.get(item["team1"])
        away=ALIASES.get(item["team2"])
        if home is None or away is None:
            unmatched_aliases.add(item["team1"] if home is None else item["team2"])
            continue
        day=date.fromisoformat(item["date"])
        key=(day.isoformat(),home,away)
        if key in b_by_key:
            raise ValueError("Duplicate OpenFootball fixture")
        b_by_key[key]=item
        b_keys.add(key)
        try: rnd=int(item["round"].split()[-1])
        except (TypeError,ValueError,IndexError): rnd=None
        compiled.append({
            "matchday":rnd,"date":day.isoformat(),"home":home,"away":away,
            "openfootball_teams":[item["team1"],item["team2"]],
            "scheduled_time_openfootball":item.get("time"),
            "score_openfootball":external_score(item.get("score")) if day<cutoff else None,
            "score_football_data":None,"score_status":"unverified",
            "football_data_matched":False,
            "is_pre_cutoff":day<cutoff,
            "allowed_use":"RESEARCH_ONLY_NO_HISTORICAL_PIT_CERTIFICATION",
        })
    by_key={(m["date"],m["home"],m["away"]):m for m in compiled}
    anomalies=[]
    valid_csv=0
    matched_csv=0
    for item in a:
        try:
            day=csv_date(item["Date"])
            h=item["HomeTeam"].strip();aw=item["AwayTeam"].strip()
            hg=int(item["FTHG"]);ag=int(item["FTAG"])
            if hg<0 or ag<0: raise ValueError("Negative score")
            if item["FTR"].strip()!=("H" if hg>ag else "A" if ag>hg else "D"):
                raise ValueError("Score/result conflict")
            if day>=cutoff: continue
            valid_csv+=1
        except (ValueError,KeyError,TypeError) as err:
            anomalies.append({"kind":"invalid_csv_row","reason":str(err),"row":item.get("Date")})
            continue
        key=(day.isoformat(),h,aw)
        if key not in by_key:
            anomalies.append({"kind":"fixture_not_reconciled","key":list(key),"score":[hg,ag]})
            continue
        m=by_key[key]
        if m["football_data_matched"]:
            anomalies.append({"kind":"duplicate_csv_match","key":list(key)})
            continue
        matched_csv+=1
        m["football_data_matched"]=True
        m["score_football_data"]=[hg,ag]
        other=m["score_openfootball"]
        if other is None: m["score_status"]="score_only_football_data"
        elif other==[hg,ag]: m["score_status"]="two_sources_agree"
        else:
            m["score_status"]="score_conflict"
            anomalies.append({"kind":"score_conflict","key":list(key),
                              "football_data":[hg,ag],"openfootball":other})
    for m in compiled:
        if not m["is_pre_cutoff"]:
            m["score_status"]="same_day_or_future_no_result_admitted"
        elif not m["football_data_matched"] and m["score_openfootball"] is not None:
            m["score_status"]="score_only_openfootball"
        elif not m["football_data_matched"]:
            m["score_status"]="no_confirmed_result"
    by_round={}
    for n,values in sorted(((n,list(rows)) for n,rows in __group_rounds(compiled).items()),key=lambda x:x[0]):
        days=sorted(x["date"] for x in values)
        counts=dict(collections.Counter(x["score_status"] for x in values))
        by_round[str(n)]={
            "matchday":n,"first_date":days[0],"last_date":days[-1],
            "scheduled_fixtures":len(values),"status_counts":counts,
            "matches":sorted(values,key=lambda x:(x["date"],x["home"],x["away"]))
        }
    months={}
    for month in ("2026-10","2026-09","2026-08"):
        selected=[x for x in compiled if x["date"].startswith(month)]
        months[month]={"fixtures":len(selected),
                       "matchdays":sorted(set(x["matchday"] for x in selected if x["matchday"] is not None)),
                       "matched_historic_results":sum(x["score_football_data"] is not None for x in selected),
                       "two_sources_agree":sum(x["score_status"]=="two_sources_agree" for x in selected),
                       "score_conflicts":sum(x["score_status"]=="score_conflict" for x in selected)}
    return {"league":LEAGUES[code][0],"competition_code":code,"cutoff_exclusive":cutoff.isoformat(),
            "n_matchdays_schedule":len(by_round),"total_schedule_fixtures":len(compiled),
            "eligible_csv_rows":valid_csv,"csv_rows_reconciled":matched_csv,
            "source_a_sha256":sha(csv_bytes),"source_b_sha256":sha(open_bytes),
            "scores_compared_with_matching_identity":sum(
                x["score_status"] in ("two_sources_agree","score_conflict") for x in compiled),
            "source_statuses":dict(collections.Counter(x["score_status"] for x in compiled)),
            "unmapped_aliases":sorted(unmatched_aliases),
            "anomalies":anomalies,"month_priority":months,"by_matchday":by_round,
            "scientific_status":"RESEARCH_ONLY_NOT_PIT_CERTIFIED"}

def __group_rounds(matches):
    output=collections.defaultdict(list)
    for m in matches:
        if m["matchday"] is not None:
            output[m["matchday"]].append(m)
    return output

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cutoff",default="2026-10-17")
    p.add_argument("--base",default=str(BASE))
    p.add_argument("--out",default="matchday_pilot")
    args=p.parse_args()
    cutoff=date.fromisoformat(args.cutoff)
    base=Path(args.base)
    manifest=json.loads((base/"integration"/"manifest.json").read_text(encoding="utf-8"))
    out=base/args.out
    out.mkdir(parents=True,exist_ok=True)
    aggregate={"generated_utc":datetime.now(timezone.utc).isoformat(),
               "cutoff_exclusive":cutoff.isoformat(),"method":"two-source date/team/score comparison",
               "warning":"No provenance of pre-match historical availability. Never inject in predictive model.",
               "provider_notes":{"A":"Football-Data previously downloaded cached CSV (no new HTTP request)",
                                 "B":"OpenFootball GitHub snapshot, score freshness can lag"},
               "leagues":{}}
    for code in LEAGUES:
        cached=manifest["sources"]["2627_"+code]
        csv_bytes=(base/"integration"/"raw"/(cached["sha256"]+".csv")).read_bytes()
        if sha(csv_bytes)!=cached["sha256"]: raise ValueError("Cached source A corrupted")
        open_bytes=(base/("openfootball_"+code+"_2627.json")).read_bytes()
        audit=run(csv_bytes,open_bytes,code,cutoff)
        json_save(out/(code+"_matchdays.json"),audit)
        aggregate["leagues"][code]={k:v for k,v in audit.items() if k!="by_matchday" and k!="anomalies"}
        aggregate["leagues"][code]["anomaly_count"]=len(audit["anomalies"])
    json_save(out/"summary.json",aggregate)
    print(json.dumps(aggregate,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
