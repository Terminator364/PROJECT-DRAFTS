#!/usr/bin/env python3
"""Single-match historical enrichment probe; no background worker, no live data."""
import hashlib, json, pathlib, urllib.request, datetime as dt
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/"03_FOURNISSEURS"/"THESPORTSDB_HISTORIQUE"/"EVENT_DETAIL_PROBE"
EVENT="2494000"  # First PL match Arsenal-Coventry, August 21 2026, archived id.
ROUTES={"lineup":"lookuplineup.php", "timeline":"lookuptimeline.php", "eventstats":"lookupeventstats.php"}
WORLD={"lineup":["LINEUP_ROTATION","SQUAD_AVAIL","GK_DEFENSE"],
       "timeline":["GOAL_TIMING","SCORING_HISTORY","GAME_STATE_POLICY"],
       "eventstats":["SHOT_CREATION","SHOT_QUALITY","POSSESSION_TERRITORIAL_CONTROL"]}

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    result={"schema":"BCP_HISTORICAL_EVENT_DETAIL_SOURCE_AUDIT_V1",
        "collected_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "event_id":EVENT,"fixture":"Arsenal - Coventry, 2026-08-21, PL J1",
        "observations_asof":"POSTMATCH_ARCHIVE_COLLECTED_OCT_2026",
        "PIT_available_at_H0":"UNVERIFIED",
        "PIT_available_at_J_MINUS_6":"UNVERIFIED",
        "allowed_use":"RESEARCH_ONLY_NOT_PREDICTIVE_FEATURE",
        "provider":"TheSportsDB free v1",
        "coverage_assessment":{},
        "warning":"Free API truncates each of these categories to at most five records; zero ability to reconstruct full lineup/events."}
    for key,endpoint in ROUTES.items():
        url="https://www.thesportsdb.com/api/v1/json/123/"+endpoint+"?id="+EVENT
        req=urllib.request.Request(url,headers={"User-Agent":"BCP-Independent-Historical-Research/1.0"})
        with urllib.request.urlopen(req,timeout=18) as response:
            raw=response.read(300001)
        if len(raw)>300000: raise ValueError("Response too big")
        obj=json.loads(raw.decode("utf-8-sig"))
        rows=obj.get(key) or []
        if not isinstance(rows,list): raise ValueError("Unexpected response "+key)
        sha=hashlib.sha256(raw).hexdigest()
        (OUT/(sha+".json")).write_bytes(raw)
        result["coverage_assessment"][key]={
          "returned_records":len(rows),
          "free_limit":5,
          "complete_series_proven":False,
          "truncation_possible":True,
          "sha256":sha,
          "field_names":sorted(set(k for rec in rows for k in rec.keys())),
          "families_candidate_only":WORLD[key],
          "historical_published_at":None,
          "use_in_model":"FORBIDDEN_UNTIL_PIT_AND_VALIDATION"}
    (OUT/"ASSESSMENT.json").write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"event_id":EVENT,"results":{key:{"records":v["returned_records"],"columns":len(v["field_names"])} for key,v in result["coverage_assessment"].items()},"status":"RESEARCH_ONLY_FREE_TRUNCATED"},ensure_ascii=False))
if __name__=="__main__": run()
