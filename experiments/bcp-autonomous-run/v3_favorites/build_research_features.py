#!/usr/bin/env python3
"""Candidate historical pre-match features. Event-time cutoff; NOT certified PIT."""
from datetime import date
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
OUT=BASE/"outputs"

def load(code):
    rows=[]
    for n in range(1,8):
        doc=json.loads((OUT/f"{code}_matchday_{n:02d}.json").read_text(encoding="utf8"))
        rows+=doc["fixtures"]
    assert len(rows)==70
    return rows

def stats(history, team, venue):
    games=[]
    for row in history:
        if team not in (row["home"],row["away"]): continue
        if venue and row[venue]!=team: continue
        score=row["historical_score"]
        home=row["home"]==team
        goals_for=score[0] if home else score[1]
        goals_against=score[1] if home else score[0]
        points=3 if goals_for>goals_against else 1 if goals_for==goals_against else 0
        games.append((row["date"],goals_for,goals_against,points))
    games.sort(key=lambda x:x[0])
    n=len(games)
    return {"games":n,
        "goals_for_mean":round(sum(x[1] for x in games)/n,4) if n else None,
        "goals_against_mean":round(sum(x[2] for x in games)/n,4) if n else None,
        "last_five_points":sum(x[3] for x in games[-5:]) if n else None,
        "last_game_date":games[-1][0] if n else None}

def compute(code):
    rows=load(code)
    report=[]
    for target in sorted(rows,key=lambda r:(r["round"],r["date"],r["home"])):
        day=target["date"]
        evidence=[r for r in rows if r["date"]<day and isinstance(r["historical_score"],list)]
        league_n=len(evidence)
        over=sum(int(sum(r["historical_score"])>=2) for r in evidence)
        home=stats(evidence,target["home"],None)
        away=stats(evidence,target["away"],None)
        home_specific=stats(evidence,target["home"],"home")
        away_specific=stats(evidence,target["away"],"away")
        record={"date":day,"matchday":target["round"],
            "home":target["home"],"away":target["away"],
            "max_evidence_date":max((r["date"] for r in evidence),default=None),
            "LEAGUE_BASE":{"historical_matches":league_n,
                "historical_over15_rate":round(over/league_n,5) if league_n else None},
            "TEAM_STRENGTH_CANDIDATE":{"home_all":home,"away_all":away,
                "home_home_venue":home_specific,"away_away_venue":away_specific},
            "REST_CONGESTION_CANDIDATE":{"home_days_since_last_match":(
                (date.fromisoformat(day)-date.fromisoformat(home["last_game_date"])).days
                if home["last_game_date"] else None),
                "away_days_since_last_match":(
                (date.fromisoformat(day)-date.fromisoformat(away["last_game_date"])).days
                if away["last_game_date"] else None)},
            "evidence_rule":"only completed outcomes with match_date STRICTLY earlier than fixture date",
            "PIT_availability_verified":False,
            "status":"OBSERVATION_ONLY_NO_IC"}
        if record["max_evidence_date"] and not record["max_evidence_date"]<day:
            raise AssertionError("TEMPORAL_LEAK")
        report.append(record)
    return {"league":code,"n_fixtures":len(report),"features":report,
        "warning":"Event-time anti-leak is necessary but insufficient for historic PIT. No source published_at/available_at validation.",
        "model_effects":"DISABLED"}

if __name__=="__main__":
    for code in ("E0","I1"):
        result=compute(code)
        path=OUT/f"{code}_RESEARCH_FEATURES.json"
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf8")
        sample=[r for r in result["features"] if r["matchday"]==7][0]
        print(code,"FEATURES",result["n_fixtures"],"MD7_EVIDENCE",sample["LEAGUE_BASE"]["historical_matches"],
              "MAX_EVIDENCE",sample["max_evidence_date"])
