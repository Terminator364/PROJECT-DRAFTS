"""Compare cached TheSportsDB sample to two full historical sources, no HTTP calls."""
import hashlib
import json
from pathlib import Path

NAMES = {
    "Coventry City": "Coventry", "Hull City": "Hull",
    "Manchester United": "Man United", "Manchester City": "Man City",
    "Nottingham Forest": "Nott'm Forest",
    "Brighton and Hove Albion": "Brighton",
    "Ipswich Town": "Ipswich", "Leeds United": "Leeds",
    "Newcastle United": "Newcastle", "Tottenham Hotspur": "Tottenham",
    "Inter Milan": "Inter", "AC Milan": "Milan"
}

def compare(code, matchday_audit, cutoff, pilot_directory):
    file = Path(pilot_directory) / "provider_snapshots" / ("thesportsdb_" + code + "_2627.json")
    if not file.is_file():
        return {"status": "missing_snapshot", "sample_matches": 0}
    raw = file.read_bytes()
    data = json.loads(raw)
    events = data.get("events") or []
    ids = {(m["date"], m["home"], m["away"]): m
           for group in matchday_audit["by_matchday"].values()
           for m in group["matches"]}
    compared = 0
    triple_agree = 0
    triple_conflict = []
    missing = []
    for e in events:
        matchdate = e.get("dateEvent")
        if not matchdate or matchdate >= cutoff.isoformat():
            continue
        home = NAMES.get(e.get("strHomeTeam"), e.get("strHomeTeam"))
        away = NAMES.get(e.get("strAwayTeam"), e.get("strAwayTeam"))
        key = (matchdate, home, away)
        m = ids.get(key)
        if m is None:
            missing.append([matchdate, home, away])
            continue
        try:
            third_score = [int(e["intHomeScore"]), int(e["intAwayScore"])]
        except (ValueError, TypeError, KeyError):
            continue
        compared += 1
        a, b = m.get("score_football_data"), m.get("score_openfootball")
        if a == b == third_score:
            triple_agree += 1
        else:
            triple_conflict.append({"match": list(key), "football_data": a,
                                    "openfootball": b, "the_sportsdb": third_score})
    return {"status": "cached_limited_sample", "source_sha256": hashlib.sha256(raw).hexdigest(),
            "sample_matches": len(events), "scores_compared": compared,
            "three_way_agreement": triple_agree, "three_way_disagreements": triple_conflict,
            "unmatched_names": missing,
            "warning": "free-key season query returned only limited sample; October unverified"}
