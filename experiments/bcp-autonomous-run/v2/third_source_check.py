#!/usr/bin/env python3
"""Add limited TheSportsDB free-tier sample as an independent third source.
Reads only saved snapshots. Never makes HTTP calls; no same-day results.
"""
import json, pathlib, datetime, hashlib
ROOT=pathlib.Path(__file__).resolve().parent
ALIASES={
"Coventry City":"Coventry","Hull City":"Hull","Manchester United":"Man United",
"Manchester City":"Man City","Nottingham Forest":"Nott'm Forest",
"Brighton and Hove Albion":"Brighton","Bournemouth":"Bournemouth",
"Ipswich Town":"Ipswich","Leeds United":"Leeds","Newcastle United":"Newcastle",
"Tottenham Hotspur":"Tottenham","Inter Milan":"Inter","AC Milan":"Milan"}
CUTOFF=datetime.date(2026,10,17)
def clean(n): return ALIASES.get(n,n)
def main():
    final={"cutoff_exclusive":str(CUTOFF),"source":"TheSportsDB free v1 eventsseason",
           "source_limit":"15 events per season per league on free key",
           "status":"RESEARCH_ONLY","leagues":{}}
    for code in ("E0","I1"):
        raw=(ROOT/"provider_snapshots"/("thesportsdb_"+code+"_2627.json")).read_bytes()
        third=json.loads(raw)
        primary=json.loads((ROOT/"matchday_pilot"/(code+"_matchdays.json")).read_text(encoding="utf-8"))
        indexed={(x["date"],x["home"],x["away"]):x for day in primary["by_matchday"].values()
                  for x in day["matches"]}
        stats={"provider_events":len(third.get("events") or []),"compared_score":0,
               "three_source_agreement":0,"disagreements":[],"not_matched":[],
               "missing_score":0,"third_sha256":hashlib.sha256(raw).hexdigest()}
        for e in third.get("events") or []:
            day=e.get("dateEvent")
            if not day or day>=str(CUTOFF): continue
            key=(day,clean(e["strHomeTeam"]),clean(e["strAwayTeam"]))
            if key not in indexed:
                stats["not_matched"].append(list(key))
                continue
            x=indexed[key]
            if e.get("intHomeScore") is None or e.get("intAwayScore") is None:
                stats["missing_score"]+=1
                continue
            score=[int(e["intHomeScore"]),int(e["intAwayScore"])]
            stats["compared_score"]+=1
            if score==x["score_football_data"]==x["score_openfootball"]:
                stats["three_source_agreement"]+=1
            else:
                stats["disagreements"].append({"key":list(key),"score_tdb":score,
                    "score_fd":x["score_football_data"],"score_of":x["score_openfootball"]})
        final["leagues"][code]=stats
    out=ROOT/"matchday_pilot"/"three_source_audit.json"
    out.write_text(json.dumps(final,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(final,ensure_ascii=False))
if __name__=="__main__":
    main()
