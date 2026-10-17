#!/usr/bin/env python3
"""One-process historical sports-data backfill, J1 -> last completed day.

TheSportsDB free eventsday (up to three matches / league / date) is sampled
at four HTTP requests per 5-minute master cycle. No live/future feeds, no IC.
"""
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parent
LIB=ROOT/"05_JOURNEES"/"HISTORIQUE_J1_ACTUEL"
OUT=ROOT/"03_FOURNISSEURS"/"THESPORTSDB_HISTORIQUE"
LEAGUES={"E0":"4328","I1":"4332"}
UA="BCP-Independent-Historical-Library/1.0"
MAX_REQUESTS_PER_CYCLE=4
MAX_BYTES=400_000
ALIASES={
"Coventry City":"Coventry","Hull City":"Hull",
"Manchester United":"Man United","Manchester City":"Man City",
"Nottingham Forest":"Nott'm Forest","Brighton and Hove Albion":"Brighton",
"Ipswich Town":"Ipswich","Leeds United":"Leeds",
"Newcastle United":"Newcastle","Tottenham Hotspur":"Tottenham",
"Inter Milan":"Inter","AC Milan":"Milan"
}


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+".pending")
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    temp.replace(path)


def event_date(item):
    try:return date.fromisoformat(item["dateEvent"])
    except (KeyError,TypeError,ValueError):return None


def schedule(cutoff):
    """Only dates in the J1-current historical library. Date must be BEFORE today."""
    requests=[]
    match_by_date={}
    for code in LEAGUES:
        games={}
        for j in range(1,8):
            f=LIB/code/("J%02d"%j)/"matchday.json"
            if not f.exists():continue
            entry=json.loads(f.read_text(encoding="utf-8"))
            for match in entry.get("matches",[]):
                d=match["prematch_identity_observed_in_current_archive"]["date"]
                if date.fromisoformat(d)>=cutoff:continue
                key=(d,match["prematch_identity_observed_in_current_archive"]["home"],
                     match["prematch_identity_observed_in_current_archive"]["away"])
                games[key]=match["outcome_known_only_after_game"]["full_time_goals"]
            for missing in entry.get("unresolved",[]):
                if date.fromisoformat(missing["date"])<cutoff:
                    key=(missing["date"],missing["home"],missing["away"])
                    games.setdefault(key,None)
        match_by_date[code]=games
        dates=sorted({key[0] for key in games})
        requests.extend([(d,code) for d in dates])
    requests.sort(key=lambda q:(q[0],q[1]))
    return requests,match_by_date


def filter_and_reconcile(payload,code,day,known,cutoff):
    raw_events=payload.get("events") or []
    if not isinstance(raw_events,list):raise ValueError("invalid events payload")
    matched=[]
    unmatched=[]
    conflicts=[]
    for event in raw_events:
        if not isinstance(event,dict):continue
        day_iso=event.get("dateEvent")
        if day_iso!=day or event_date(event) is None or event_date(event)>=cutoff:
            continue
        # Explicitly discard in-progress/postponed; only final historical games.
        if str(event.get("strStatus") or "").upper()!="FT":
            continue
        try:
            scores=[int(event["intHomeScore"]),int(event["intAwayScore"])]
        except (ValueError,KeyError,TypeError):
            continue
        if min(scores)<0:continue
        home=ALIASES.get(event.get("strHomeTeam"),event.get("strHomeTeam"))
        away=ALIASES.get(event.get("strAwayTeam"),event.get("strAwayTeam"))
        key=(day,home,away)
        observation={
           "provider_event_id":str(event.get("idEvent") or ""),
           "date":day,"home":home,"away":away,
           "fulltime_score":[scores[0],scores[1]],
           "round":event.get("intRound"),
           "venue_as_reported":event.get("strVenue"),
           "status":"POSTMATCH_HISTORICAL_ONLY",
           "publisher_publication_utc":None,
           "historical_available_at_j_minus_n":None,
           "not_prematch_feature_for_target":True
        }
        existing=known.get(key,"UNIDENTIFIED")
        if existing=="UNIDENTIFIED":
            unmatched.append(observation)
        elif existing is None:
            matched.append({**observation,"previous_archive_score":None,
                            "comparison":"SOURCE_ONLY_REQUIRES_CHECK"})
        elif existing==scores:
            matched.append({**observation,"previous_archive_score":existing,
                            "comparison":"AGREES_WITH_ARCHIVED_CSV"})
        else:
            conflict={**observation,"previous_archive_score":existing,
                      "comparison":"CONFLICT"}
            matched.append(conflict)
            conflicts.append(conflict)
    return {"date":day,"league":code,"provider_events_returned":len(raw_events),
            "api_free_result_limit":3,
            "archive_fixtures_on_date":sum(k[0]==day for k in known),
            "matched":matched,"unmatched":unmatched,"conflicts":conflicts,
            "provider_may_omit_other_matches":True}


def fetch_day(code,day):
    url=f"https://www.thesportsdb.com/api/v1/json/123/eventsday.php?d={day}&l={LEAGUES[code]}"
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=18) as r:
        raw=r.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:raise ValueError("response too big")
    return raw


def refresh(state,cutoff=None,fetcher=fetch_day,max_requests=MAX_REQUESTS_PER_CYCLE):
    cutoff=cutoff or datetime.now(timezone(timedelta(hours=1))).date()
    tasks,fixtures=schedule(cutoff)
    checked=state.setdefault("historical_checked",{})
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"raw_sha256").mkdir(exist_ok=True)
    selected=[(day,code) for day,code in tasks if (code+"|"+day) not in checked][:max_requests]
    receipts=[]
    for day,code in selected:
        key=code+"|"+day
        try:
            raw=fetcher(code,day)
            digest=hashlib.sha256(raw).hexdigest()
            data=json.loads(raw.decode("utf-8-sig"))
            assessment=filter_and_reconcile(data,code,day,fixtures[code],cutoff)
            obj=OUT/"raw_sha256"/(digest+".json")
            if not obj.exists():obj.write_bytes(raw)
            assessment.update({"snapshot_collected_utc":utc(),
                               "raw_sha256":digest,
                               "scientific_status":"RESEARCH_ONLY_NOT_PIT",
                               "allowed_use":"HISTORICAL_POST_MATCH_SOURCE_CROSSCHECK_ONLY"})
            save(OUT/code/(day+".json"),assessment)
            checked[key]={"status":"validated","collected_utc":utc(),"raw_sha256":digest,
                          "matches_compared":len(assessment["matched"]),
                          "conflict_count":len(assessment["conflicts"])}
            receipts.append({"key":key,"status":"validated",
                             "matched":len(assessment["matched"]),
                             "conflicts":len(assessment["conflicts"])})
        except urllib.error.HTTPError as e:
            receipts.append({"key":key,"status":"http_error","code":e.code})
            if e.code==429:state["historical_pause_until_epoch"]=time.time()+3600
            else:checked[key]={"status":"failed","error":"HTTP_"+str(e.code)}
            if e.code==429:break
        except (urllib.error.URLError,TimeoutError,OSError,ValueError,TypeError,
                json.JSONDecodeError) as e:
            checked[key]={"status":"failed","error":type(e).__name__+": "+str(e)[:140]}
            receipts.append({"key":key,"status":"failed","error":type(e).__name__})
    completed=sum(x.get("status")=="validated" for x in checked.values())
    report={
      "schema":"BCP_HISTORICAL_BACKFILL_V1","last_refresh_utc":utc(),
      "cutoff_exclusive":cutoff.isoformat(),"provider":"TheSportsDB free eventsday",
      "date_tasks_total":len(tasks),"date_tasks_checked":len(checked),
      "date_tasks_validated":completed,
      "date_tasks_remaining":sum((code+"|"+day) not in checked for day,code in tasks),
      "this_cycle_http_requests":len(receipts),
      "this_cycle":receipts,
      "status":"HISTORICAL_RESEARCH_ONLY",
      "no_live_or_future":True,
      "original_historical_published_at_verified":False,
      "results_not_features_at_j_minus_n":True
    }
    save(OUT/"BACKFILL_STATUS.json",report)
    state["historical_cycle_latest"]=report
    state["historical_http_request_count"]=state.get("historical_http_request_count",0)+len(receipts)
    state["last_five_minute_fetch_epoch"]=time.time()
    return report
