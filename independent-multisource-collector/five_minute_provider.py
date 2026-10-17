#!/usr/bin/env python3
"""Five-minute approved-provider probe; only future pre-match fixtures are stored.

TheSportsDB free v1 docs: 30 requests/minute; eventsday returns at most 3 events.
We poll ONLY EPL and Serie A today/tomorrow (four GETs in 5 minutes).
In-progress/completed games and scores are discarded before saving.
"""
import datetime as dt
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

LEAGUES = {"E0": "4328", "I1": "4332"}
USER_AGENT = "BCP-Standalone-Prematch/1.0 (educational research)"
MAX_RESPONSE = 300_000
NO_PLAY = {"HT", "2H", "1H", "FT", "AET", "PEN", "LIVE", "INT", "POST", "CANC",
           "SUSP", "ABD"}


def kinshasa_now():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=1)))


def parse_start(stamp):
    if not stamp or not isinstance(stamp, str):
        return None
    try:
        t = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=dt.timezone.utc)  # TheSportsDB strTimestamp uses UTC.
        return t.astimezone(dt.timezone.utc)
    except ValueError:
        return None


def verify_and_filter(payload, actual_now=None):
    """Return strictly future scheduled fixtures; never retain match scores."""
    actual_now = actual_now or dt.datetime.now(dt.timezone.utc)
    items = payload.get("events")
    if items is None:
        items = []
    if not isinstance(items, list):
        raise ValueError("Unexpected event list")
    future = []
    excluded = 0
    for e in items:
        if not isinstance(e, dict):
            excluded += 1
            continue
        status = str(e.get("strStatus") or "").upper()
        start = parse_start(e.get("strTimestamp"))
        if status not in {"NS", "NOT STARTED"} or start is None or start <= actual_now:
            excluded += 1
            continue
        if not (e.get("strHomeTeam") and e.get("strAwayTeam") and e.get("dateEvent")):
            excluded += 1
            continue
        future.append({
            "idEvent": str(e.get("idEvent") or ""),
            "source": "TheSportsDB",
            "date": e["dateEvent"],
            "start_utc": start.isoformat(timespec="seconds"),
            "home": e["strHomeTeam"],
            "away": e["strAwayTeam"],
            "venue": e.get("strVenue"),
            "round": e.get("intRound"),
            "status": "PREMATCH_SCHEDULED_UNVERIFIED",
            "asof_utc": actual_now.isoformat(timespec="seconds"),
            "available_at_historical_T": "NOT_VERIFIED",
            "scores_included": False
        })
    return future, excluded


def fetch_day(league, day):
    url = ("https://www.thesportsdb.com/api/v1/json/123/eventsday.php"
           "?d=" + day + "&l=" + LEAGUES[league])
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=18) as response:
        blob = response.read(MAX_RESPONSE + 1)
    if len(blob) > MAX_RESPONSE:
        raise ValueError("Response exceeds 300KB")
    payload = json.loads(blob.decode("utf-8"))
    return payload


def refresh(state, folder, fetcher=fetch_day, now=None):
    """Exactly four small requests unless throttled. Called once per five-minute interval."""
    now = now or kinshasa_now()
    today = now.date()
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    results = []
    counts = {"requests": 0, "future_fixtures": 0, "excluded_live_or_past": 0,
              "errors": 0}
    for code in ("E0", "I1"):
        for offset in (0, 1):
            day = (today + dt.timedelta(days=offset)).isoformat()
            counts["requests"] += 1
            try:
                payload = fetcher(code, day)
                future, excluded = verify_and_filter(
                    payload, actual_now=now.astimezone(dt.timezone.utc))
                counts["future_fixtures"] += len(future)
                counts["excluded_live_or_past"] += excluded
                results.append({"league": code, "date": day, "events": future,
                                "free_tier_truncated_possible": True})
            except urllib.error.HTTPError as error:
                counts["errors"] += 1
                results.append({"league": code, "date": day,
                                "error": "HTTP_" + str(error.code)})
                if error.code == 429:
                    state["tdb_pause_until_epoch"] = time.time() + 3600
                    break
            except (ValueError, TypeError, urllib.error.URLError, TimeoutError, OSError) as error:
                counts["errors"] += 1
                results.append({"league": code, "date": day,
                                "error": type(error).__name__ + ": " + str(error)[:160]})
        if time.time() < state.get("tdb_pause_until_epoch", 0):
            break
    content = json.dumps(results, ensure_ascii=False, sort_keys=True).encode("utf-8")
    digest = hashlib.sha256(content).hexdigest()
    snapshot = {
        "schema": "BCP_PREMATCH_SOURCE_EVENTS_V1",
        "collected_utc": now.astimezone(dt.timezone.utc).isoformat(timespec="seconds"),
        "data_sha256": digest, "status": "RESEARCH_ONLY_PREMATCH_SCHEDULE",
        "source": "TheSportsDB-v1 eventsday (free sample max 3/day/league)",
        "request_count": counts["requests"], "counts": counts, "results": results,
        "no_scores_or_live_features": True,
        "warning": "No evidence of published_at/available_at history at earlier T",
    }
    out = folder / "LATEST_PREMATCH.json"
    tmp = folder / "LATEST_PREMATCH.tmp"
    tmp.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    tmp.replace(out)
    state["latest_prematch"] = {
        "utc": snapshot["collected_utc"], "counts": counts, "sha256": digest}
    state["network_request_count"] = state.get("network_request_count", 0) + counts["requests"]
    state["last_five_minute_fetch_epoch"] = time.time()
    return snapshot
