#!/usr/bin/env python3
"""Standalone data-collection lab (not the MATRICE prediction engine).
Runs local audits every 5m; selectively refreshes OpenFootball once per 24h.
Football-Data and TheSportsDB remain cached only pending source-specific limits.
"""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parent
PILOT = ROOT / "02_BCP_COLLECTE" / "TEST_20261017" / "v2"
RAW = ROOT / "03_FOURNISSEURS" / "OPENFOOTBALL_SHA256"
ROUNDS = ROOT / "05_JOURNEES"
REPORTS = ROOT / "08_RAPPORTS"
LOGS = ROOT / "09_JOURNAUX"
EXECUTION = ROOT / "07_EXECUTION"
SOURCES = {
    "E0": ("https://raw.githubusercontent.com/openfootball/football.json/master/2026-27/en.1.json", "Premier League"),
    "I1": ("https://raw.githubusercontent.com/openfootball/football.json/master/2026-27/it.1.json", "Serie A"),
}
FRESHNESS_SECONDS = 86400
LOCAL_AUDIT_SECONDS = 300
HEARTBEAT_SECONDS = 60


def iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def cutoff():
    # Kinshasa and West Africa Time remain UTC+1 throughout the year.
    return datetime.now(timezone(timedelta(hours=1))).date()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".pending")
    tmp.write_text(json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    os.replace(tmp, path)


def log(event, **fields):
    LOGS.mkdir(parents=True, exist_ok=True)
    with (LOGS / "master_events.jsonl").open("a", encoding="utf-8") as fp:
        fp.write(json.dumps({"utc": iso(), "event": event, **fields},
                            ensure_ascii=False, sort_keys=True) + "\n")
        fp.flush()


def refresh_openfootball(state):
    """Only one open-source supplier is network-enabled. Two small GETs daily."""
    RAW.mkdir(parents=True, exist_ok=True)
    for league, (url, label) in SOURCES.items():
        entry = state["sources"].setdefault(league, {})
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "BCP-Standalone-Research/1.0"})
            with urllib.request.urlopen(request, timeout=20) as stream:
                raw = stream.read(800001)
            if len(raw) > 800000:
                raise ValueError("OpenFootball payload exceeds safety cap")
            parsed = json.loads(raw.decode("utf-8-sig"))
            fixtures = parsed.get("matches", [])
            if not isinstance(fixtures, list) or len(fixtures) < 100:
                raise ValueError("Unexpected fixture coverage")
            if any(not all(k in row for k in ("round", "date", "team1", "team2"))
                   for row in fixtures):
                raise ValueError("Incomplete fixture identity")
            digest = hashlib.sha256(raw).hexdigest()
            obj = RAW / (digest + ".json")
            if not obj.exists():
                obj.write_bytes(raw)
            latest = PILOT / ("openfootball_" + league + "_2627.json")
            tmp = latest.with_name(latest.name + ".pending")
            tmp.write_bytes(raw)
            os.replace(tmp, latest)
            entry.update({"status": "validated", "url": url, "league": label,
                          "sha256": digest, "matches": len(fixtures), "collected_utc": iso(),
                          "source_available_at_historical_T": "UNVERIFIED"})
            log("open_source_refreshed", league=league, matches=len(fixtures), sha256=digest)
        except Exception as exc:
            entry["error"] = type(exc).__name__ + ": " + str(exc)
            entry["last_failure_utc"] = iso()
            log("open_source_refresh_error", league=league, error=entry["error"])
        save(EXECUTION / "MASTER_STATE.json", state)
    state["last_openfootball_fetch_epoch"] = time.time()
    save(EXECUTION / "MASTER_STATE.json", state)


def build_reports(state):
    """No network IO: reconcile immutable cached CSV against OpenFootball JSON."""
    sys.path.insert(0, str(PILOT))
    import matchday_crosscheck as matching
    from third_party_adapter import compare as compare_third
    manifest = json.loads((PILOT / "integration" / "manifest.json").read_text(encoding="utf-8"))
    out = {"generated_utc": iso(), "cutoff_exclusive": cutoff().isoformat(),
           "project": "COLLECTEUR_AUTONOME_MULTISOURCES",
           "data_status": "RESEARCH_ONLY_NOT_PIT_CERTIFIED",
           "leagues": {}, "providers": {
               "Football-Data": "cached only; repeated network polling disabled",
               "OpenFootball": "daily automated check; public domain",
               "TheSportsDB": "cached limited sample; repeated polling disabled",
           }}
    ROUNDS.mkdir(parents=True, exist_ok=True)
    for code in ("E0", "I1"):
        ref = manifest["sources"]["2627_" + code]
        raw_csv = (PILOT / "integration" / "raw" / (ref["sha256"] + ".csv")).read_bytes()
        if hashlib.sha256(raw_csv).hexdigest() != ref["sha256"]:
            raise ValueError("Football-Data archive SHA-256 mismatch " + code)
        other = (PILOT / ("openfootball_" + code + "_2627.json")).read_bytes()
        audit = matching.run(raw_csv, other, code, cutoff())
        save(ROUNDS / (code + "_JOURNEES.json"), audit)
        out["leagues"][code] = {
            "name": audit["league"],
            "scheduled_matchdays": audit["n_matchdays_schedule"],
            "scheduled_fixtures": audit["total_schedule_fixtures"],
            "historical_fixtures_reconciled": audit["csv_rows_reconciled"],
            "scores_two_sources_agree": audit["source_statuses"].get("two_sources_agree", 0),
            "scores_single_source": audit["source_statuses"].get("score_only_football_data", 0),
            "score_conflicts": audit["source_statuses"].get("score_conflict", 0),
            "unmapped_names": audit["unmapped_aliases"],
            "anomaly_count": len(audit["anomalies"]),
            "months": audit["month_priority"],
            "third_source": compare_third(code, audit, cutoff(), PILOT),
        }
    save(REPORTS / "LATEST_TWO_LEAGUES.json", out)
    log("local_audit_completed", leagues=2, cutoff=out["cutoff_exclusive"],
        anomalies=sum(x["anomaly_count"] for x in out["leagues"].values()))
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--hours", type=int, default=24)
    args = parser.parse_args()
    if not 1 <= args.hours <= 168:
        raise ValueError("hours must be 1..168")
    for directory in (EXECUTION, REPORTS, LOGS, ROUNDS, RAW):
        directory.mkdir(parents=True, exist_ok=True)
    # A local loopback port prevents two master workers from running simultaneously.
    guard = socket.socket()
    try:
        guard.bind(("127.0.0.1", 29731))
    except OSError:
        log("already_running")
        print("ALREADY_RUNNING")
        return
    path = EXECUTION / "MASTER_STATE.json"
    if path.exists():
        state = json.loads(path.read_text(encoding="utf-8"))
    else:
        state = {"run_id": "MASTER-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                 "created_utc": iso(), "audits": 0, "ticks": 0, "sources": {},
                 "last_openfootball_fetch_epoch": 0, "last_local_audit_epoch": 0}
    state["status"] = "running"
    state["pid"] = os.getpid()
    state["deadline_epoch"] = max(state.get("deadline_epoch", 0),
                                  time.time() + (60 if args.once else args.hours * 3600))
    save(path, state)
    log("master_started", run_id=state["run_id"], pid=state["pid"], offline=args.offline)
    try:
        while time.time() < state["deadline_epoch"]:
            if (EXECUTION / "STOP").exists():
                state["status"] = "stopped_by_user"
                break
            if not args.offline and time.time() - state["last_openfootball_fetch_epoch"] >= FRESHNESS_SECONDS:
                refresh_openfootball(state)
            if not state["last_local_audit_epoch"] or time.time() - state["last_local_audit_epoch"] >= LOCAL_AUDIT_SECONDS:
                try:
                    summary = build_reports(state)
                    state["audits"] += 1
                    state["last_audit_error"] = None
                    state["last_audit_league_count"] = len(summary["leagues"])
                except Exception as exc:
                    state["last_audit_error"] = type(exc).__name__ + ": " + str(exc)
                    log("local_audit_failed", error=state["last_audit_error"])
                state["last_local_audit_epoch"] = time.time()
            state["ticks"] += 1
            state["heartbeat_utc"] = iso()
            save(path, state)
            log("heartbeat", tick=state["ticks"], audits=state["audits"])
            if args.once:
                break
            time.sleep(min(HEARTBEAT_SECONDS, max(0, state["deadline_epoch"] - time.time())))
        if state["status"] == "running":
            state["status"] = "completed"
    finally:
        state["finished_or_stopped_utc"] = iso()
        save(path, state)
        save(EXECUTION / "LAST_RECEIPT.json", {
            "run_id": state["run_id"], "status": state["status"],
            "heartbeat_count": state["ticks"], "audit_count": state["audits"],
            "error": state.get("last_audit_error"),
            "finished_or_stopped_utc": state["finished_or_stopped_utc"],
        })
        log("master_finished", status=state["status"])
        guard.close()


if __name__ == "__main__":
    main()
