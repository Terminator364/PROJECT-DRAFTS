#!/usr/bin/env python3
"""BCP autonomous historical-data audit. Standard library only, no live match data."""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import time
import traceback
import urllib.request

SOURCES = {
    "E0_2025_2026": "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
    "E0_2026_2027": "https://www.football-data.co.uk/mmz4281/2627/E0.csv",
}
MANDATORY = ("Date", "HomeTeam", "AwayTeam", "FTR", "FTHG", "FTAG")


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def atomic_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, path)


def event(path, name, **data):
    record = {"utc": utc(), "event": name, **data}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()


def match_date(value):
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(str(value).strip(), fmt).date()
        except ValueError:
            pass
    return None


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "BCP-PreMatch-Audit/1.0"})
    with urllib.request.urlopen(req, timeout=18) as reply:
        data = reply.read(3_000_001)
        if len(data) > 3_000_000:
            raise ValueError("Source exceeds 3 MB maximum")
        return data


def evaluate(raw, season, cutoff):
    decoded = raw.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(decoded))
    fields = reader.fieldnames or []
    missing = [name for name in MANDATORY if name not in fields]
    if missing:
        raise ValueError("Missing mandatory columns: " + ", ".join(missing))
    rows = 0
    retained = []
    rejected = {}
    for row in reader:
        rows += 1
        date = match_date(row.get("Date", ""))
        if date is None:
            reason = "invalid_date"
        elif date >= cutoff:
            reason = "today_or_future_excluded"
        elif row.get("FTR", "").strip() not in ("H", "D", "A"):
            reason = "not_completed"
        elif not row.get("HomeTeam", "").strip() or not row.get("AwayTeam", "").strip():
            reason = "missing_teams"
        else:
            try:
                hg, ag = int(row.get("FTHG", "")), int(row.get("FTAG", ""))
                if hg < 0 or ag < 0:
                    raise ValueError()
                expected = "H" if hg > ag else ("A" if hg < ag else "D")
                reason = None if row["FTR"].strip() == expected else "inconsistent_result"
            except (ValueError, TypeError):
                reason = "invalid_score"
        if reason:
            rejected[reason] = rejected.get(reason, 0) + 1
            continue
        retained.append((date.isoformat(), row["HomeTeam"].strip(),
                         row["AwayTeam"].strip(), hg, ag))
    retained.sort()
    teams = {}
    def update(team, gf, ga, venue):
        rec = teams.setdefault(team, {"played": 0, "points": 0, "gf": 0, "ga": 0,
                                      "home": 0, "away": 0, "results": []})
        rec["played"] += 1
        rec[venue] += 1
        rec["gf"] += gf
        rec["ga"] += ga
        points = 3 if gf > ga else (1 if gf == ga else 0)
        rec["points"] += points
        rec["results"].append(points)
    for date, home, away, hg, ag in retained:
        update(home, hg, ag, "home")
        update(away, ag, hg, "away")
    for rec in teams.values():
        rec["last5_points"] = sum(rec.pop("results")[-5:])
    return {
        "season": season, "input_rows": rows, "accepted_pre_match_history": len(retained),
        "rejected": rejected, "team_count": len(teams), "teams": teams,
        "cutoff_exclusive": cutoff.isoformat(), "method": "completed games dated before today only",
        "no_prediction_or_betting_signal": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-seconds", type=int, default=3600)
    parser.add_argument("--interval-seconds", type=int, default=60)
    parser.add_argument("--refresh-seconds", type=int, default=600)
    parser.add_argument("--run-dir", default="runtime")
    opts = parser.parse_args()
    if not (3 <= opts.duration_seconds <= 7200 and
            2 <= opts.interval_seconds <= 600 and 3 <= opts.refresh_seconds <= 3600):
        raise ValueError("Unsafe test parameters")
    root = Path(__file__).resolve().parent
    dest = (root / opts.run_dir).resolve()
    if root != dest and root not in dest.parents:
        raise ValueError("Run directory must stay within the project")
    dest.mkdir(parents=True, exist_ok=True)
    state_path = dest / "checkpoint.json"
    log_path = dest / "events.jsonl"
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if state.get("status") == "completed":
            event(log_path, "already_completed", run_id=state.get("run_id"))
            return
    else:
        now = time.time()
        state = {
            "run_id": "BCP-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
            "started_utc": utc(), "started_epoch": now, "deadline_epoch": now + opts.duration_seconds,
            "duration_seconds": opts.duration_seconds, "tick": 0,
            "last_refresh_epoch": 0, "status": "running", "pid": os.getpid(),
            "source_checksums": {}, "last_error": None,
        }
    state["pid"] = os.getpid()
    event(log_path, "resumed" if state["tick"] else "started",
          run_id=state["run_id"], pid=state["pid"])
    atomic_json(state_path, state)
    while time.time() < state["deadline_epoch"]:
        if (dest / "STOP").exists():
            state["status"] = "stopped_by_user"
            break
        state["tick"] += 1
        do_fetch = not state["source_checksums"] or (
            time.time() - state["last_refresh_epoch"] >= opts.refresh_seconds)
        if do_fetch:
            fresh = {}
            for season, url in SOURCES.items():
                try:
                    data = fetch(url)
                    info = evaluate(data, season, dt.date.today())
                    checksum = hashlib.sha256(data).hexdigest()
                    fresh[season] = dict(info, source_url=url, sha256=checksum,
                                         fetched_utc=utc())
                    raw_dir = dest / "raw"
                    raw_dir.mkdir(exist_ok=True)
                    (raw_dir / (season + ".csv")).write_bytes(data)
                    state["source_checksums"][season] = checksum
                    event(log_path, "source_validated", season=season, sha256=checksum,
                          accepted=info["accepted_pre_match_history"],
                          rejected=info["rejected"])
                except Exception as exc:
                    state["last_error"] = type(exc).__name__ + ": " + str(exc)
                    event(log_path, "source_error", season=season, error=state["last_error"])
            if fresh:
                current_path = dest / "analysis.json"
                previous = {}
                if current_path.exists():
                    previous = json.loads(current_path.read_text(encoding="utf-8")).get("seasons", {})
                previous.update(fresh)
                atomic_json(current_path, {
                    "run_id": state["run_id"], "generated_utc": utc(),
                    "restriction": "no live data, no same-day games, no forecasts",
                    "seasons": previous,
                })
                state["last_refresh_epoch"] = time.time()
        state["heartbeat_utc"] = utc()
        state["elapsed_seconds"] = int(time.time() - state["started_epoch"])
        state["status"] = "running"
        atomic_json(state_path, state)
        event(log_path, "heartbeat", tick=state["tick"],
              elapsed_seconds=state["elapsed_seconds"], fetched=do_fetch)
        delay = min(opts.interval_seconds, max(0, state["deadline_epoch"] - time.time()))
        if delay:
            time.sleep(delay)
    if state["status"] == "running":
        state["status"] = "completed"
    state["finished_utc"] = utc()
    state["elapsed_seconds"] = int(time.time() - state["started_epoch"])
    atomic_json(state_path, state)
    atomic_json(dest / "receipt.json", {
        "run_id": state["run_id"], "status": state["status"], "ticks": state["tick"],
        "started_utc": state["started_utc"], "finished_utc": state["finished_utc"],
        "elapsed_seconds": state["elapsed_seconds"], "source_checksums": state["source_checksums"],
        "last_error": state["last_error"],
    })
    event(log_path, "finished", status=state["status"], ticks=state["tick"])


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        error = traceback.format_exc()
        fallback = Path(__file__).resolve().parent / "fatal-error.log"
        fallback.write_text(utc() + "\n" + error, encoding="utf-8")
        sys.exit(1)
