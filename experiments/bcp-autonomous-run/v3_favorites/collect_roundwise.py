#!/usr/bin/env python3
"""MATRICE two-favorites by-matchday research pilot. No prediction, no live use."""
import csv
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parent
CUT=dt.date(2026,10,17)
LEAGUES={
 "E0":{"name":"Premier League","json":"en.1","official":"https://www.premierleague.com/en/matches/premier-league/2026-27/matchweek-"},
 "I1":{"name":"Serie A","json":"it.1","official":"https://en.legaseriea.it/serie-a/fixtures-results?matchday="}
}
ALIASES={
 "Arsenal FC":"Arsenal","Aston Villa FC":"Aston Villa","AFC Bournemouth":"Bournemouth",
 "Brentford FC":"Brentford","Brighton & Hove Albion FC":"Brighton","Chelsea FC":"Chelsea",
 "Coventry City FC":"Coventry","Crystal Palace FC":"Crystal Palace","Everton FC":"Everton",
 "Fulham FC":"Fulham","Hull City AFC":"Hull","Ipswich Town FC":"Ipswich",
 "Leeds United FC":"Leeds","Liverpool FC":"Liverpool","Manchester City FC":"Man City",
 "Manchester United FC":"Man United","Newcastle United FC":"Newcastle",
 "Nottingham Forest FC":"Nott'm Forest","Sunderland AFC":"Sunderland",
 "Tottenham Hotspur FC":"Tottenham","AC Milan":"Milan","AC Monza":"Monza",
 "ACF Fiorentina":"Fiorentina","AS Roma":"Roma","Atalanta BC":"Atalanta",
 "Bologna FC 1909":"Bologna","Cagliari Calcio":"Cagliari","Como 1907":"Como",
 "FC Internazionale Milano":"Inter","Frosinone Calcio":"Frosinone",
 "Genoa CFC":"Genoa","Juventus FC":"Juventus","Parma Calcio 1913":"Parma",
 "SS Lazio":"Lazio","SSC Napoli":"Napoli","Torino FC":"Torino",
 "US Lecce":"Lecce","US Sassuolo Calcio":"Sassuolo",
 "Udinese Calcio":"Udinese","Venezia FC":"Venezia"}
assert len(ALIASES)==40 and len(set(ALIASES.values()))==40

def download(url):
    req=urllib.request.Request(url,headers={"User-Agent":"MATRICE-Research-MultiSource/0.1"})
    with urllib.request.urlopen(req,timeout=22) as response:
        data=response.read(300001)
    if len(data)>300000: raise ValueError("JSON exceeds bounded size")
    return data

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def atomic_json(path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+".tmp")
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    tmp.replace(path)

def csv_archive(integration, key):
    m=json.loads((integration/"manifest.json").read_text(encoding="utf8"))
    source=m["sources"][key]
    assert source["status"]=="validated"
    path=integration/"raw"/(source["sha256"]+".csv")
    raw=path.read_bytes()
    if sha(raw)!=source["sha256"]:
        raise ValueError("cache SHA-256 check failed for "+key)
    result={}
    for row in csv.DictReader(io.StringIO(raw.decode("utf-8-sig",errors="replace"))):
        try:
            day=dt.datetime.strptime(row["Date"],"%d/%m/%Y").date()
        except ValueError:
            day=dt.datetime.strptime(row["Date"],"%d/%m/%y").date()
        if day>=CUT: continue
        home,away=row["HomeTeam"].strip(),row["AwayTeam"].strip()
        score=[int(row["FTHG"]),int(row["FTAG"])]
        identity=(day.isoformat(),home,away)
        if identity in result: raise ValueError("Duplicate CSV fixture "+str(identity))
        result[identity]={"score":score,"csv_ref":key,"source_sha256":sha(raw)}
    return result

def run(integration, output, getter=download):
    output.mkdir(parents=True,exist_ok=True)
    summary={"pilot":"MATRICE_R8_FAVORITES_ROUNDWISE_TWO_LEAGUES",
        "cutoff_exclusive":CUT.isoformat(),"created_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "scientific_status":"RESEARCH_ONLY; NO HISTORIC PIT AVAILABILITY CERTIFICATION",
        "note":"OpenFootball JSON and prior Football-Data CSV snapshot. Official links are additional manual spot-check references; not ingested programmatically.",
        "leagues":{}}
    for league,opts in LEAGUES.items():
        url=f"https://raw.githubusercontent.com/openfootball/football.json/master/2026-27/{opts['json']}.json"
        raw=getter(url)
        source_sha=sha(raw)
        (output/(source_sha+".json")).write_bytes(raw)
        parsed=json.loads(raw.decode("utf8"))
        matches=parsed["matches"]
        csvdata=csv_archive(integration,"2627_"+league)
        seen=set()
        md={}
        used=set()
        for row in matches:
            round_label=row.get("round","")
            if not round_label.startswith("Matchday "):
                continue
            n=int(round_label.split(" ",1)[1])
            day=dt.date.fromisoformat(row["date"])
            home=ALIASES.get(row["team1"])
            away=ALIASES.get(row["team2"])
            if home is None or away is None:
                raise ValueError("Unrecognized team name: "+str(row["team1"])+"/"+str(row["team2"]))
            key=(day.isoformat(),home,away)
            if key in seen: raise ValueError("Duplicate open fixture: "+str(key))
            seen.add(key)
            assert n>=1 and n<=38
            record={"date":day.isoformat(),"round":n,"home":home,"away":away,
                "original_home":row["team1"],"original_away":row["team2"],
                "official_matchday_url":opts["official"]+str(n),
                "available_at_pre_match":"UNVERIFIED",
                "source_count_with_confirmed_score":0}
            if day>=CUT:
                record["status"]="ON_OR_AFTER_CUTOFF_NO_RESULTS_ADMITTED"
                record["historical_score"]=None
            else:
                score_blob=row.get("score")
                f=score_blob.get("ft") if isinstance(score_blob,dict) else (score_blob if isinstance(score_blob,list) else None)
                c=csvdata.get(key)
                if c: used.add(key)
                record["openfootball_score"]=f if isinstance(f,list) and len(f)==2 else None
                record["football_data_cached_score"]=c["score"] if c else None
                if c and f and c["score"]==f:
                    record["status"]="TWO_SOURCE_RESULT_AGREEMENT"
                    record["source_count_with_confirmed_score"]=2
                    record["historical_score"]=f
                elif c and f and c["score"]!=f:
                    record["status"]="SCORE_CONFLICT"
                    record["historical_score"]=None
                elif c and not f:
                    record["status"]="CSV_RESULT_ONLY"
                    record["source_count_with_confirmed_score"]=1
                    record["historical_score"]=c["score"]
                elif f and not c:
                    record["status"]="OPENFOOTBALL_RESULT_ONLY"
                    record["source_count_with_confirmed_score"]=1
                    record["historical_score"]=f
                else:
                    record["status"]="NO_TWO_SOURCE_RESULT"
                    record["historical_score"]=None
            md.setdefault(n,[]).append(record)
        by_round=[]
        for n in sorted((x for x in md if min(dt.date.fromisoformat(e["date"]) for e in md[x])<=CUT),reverse=True):
            fixtures=sorted(md[n],key=lambda x:(x["date"],x["home"],x["away"]))
            count={}
            for x in fixtures:count[x["status"]]=count.get(x["status"],0)+1
            artifact={"competition":opts["name"],"code":league,
                "matchday":n,"date_range":[fixtures[0]["date"],fixtures[-1]["date"]],
                "coverage":count,"fixtures":fixtures,"cutoff_exclusive":CUT.isoformat(),
                "allowed_use":"RESEARCH_ONLY_NO_IC",
                "sources":[url,"CACHED_PREVIOUS_FOOTBALL_DATA_CSV",
                           opts["official"]+str(n)]}
            atomic_json(output/(f"{league}_matchday_{n:02d}.json"),artifact)
            by_round.append({"matchday":n,"fixtures":len(fixtures),
                "date_range":artifact["date_range"],"statuses":count})
        missing=sorted(set(csvdata)-used)
        summary["leagues"][league]={"name":opts["name"],"openfootball_url":url,
            "openfootball_sha256":source_sha,"openfootball_total_season_fixtures":len(matches),
            "football_data_cached_rows_prior_to_cutoff":len(csvdata),
            "football_data_rows_unmatched":len(missing),
            "unmatched_csv_fixtures":[{"date":d,"home":h,"away":a} for d,h,a in missing],
            "matchdays_from_current_backwards":by_round,
            "two_source_result_agreements":sum(x["statuses"].get("TWO_SOURCE_RESULT_AGREEMENT",0) for x in by_round),
            "score_conflicts":sum(x["statuses"].get("SCORE_CONFLICT",0) for x in by_round),
            "data_quality_warning":"no published_at or available_at proofs; score comparison is retrospective research only"}
    atomic_json(output/"ROUNDWISE_MANIFEST.json",summary)
    return summary

if __name__=="__main__":
    main=ROOT.parents[0]
    integration=ROOT.parents[1]/"v2"/"integration"
    out=ROOT/"outputs"
    result=run(integration,out)
    print(json.dumps({"output":str(out),
        "by_league":{k:{"rounds":len(v["matchdays_from_current_backwards"]),
        "agreements":v["two_source_result_agreements"],
        "conflicts":v["score_conflicts"],"unmatched_csv":v["football_data_rows_unmatched"]}
        for k,v in result["leagues"].items()}},indent=2))
