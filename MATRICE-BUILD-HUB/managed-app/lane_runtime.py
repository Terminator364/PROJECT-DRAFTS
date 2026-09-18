from __future__ import annotations

import hashlib
import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any

SCHEMA = "build2.lane_runtime/1"
HEARTBEAT_SCHEMA = "build2.heartbeat/1"
RECEIPT_SCHEMA = "build2.receipt/1"
RUN_SCHEMA = "build2.run_state/1"
ALLOWED_STAGES = (
    "ACCEPTED", "SOURCE_SYNC", "PREFLIGHT", "BUILDER_PROVISION",
    "BUILD", "SIGN", "VERIFY", "PUBLISH", "READBACK", "COMPLETE",
    "FAILED_SAFE", "HOLD", "CANCELLED",
)
TERMINAL = {"COMPLETE", "FAILED_SAFE", "HOLD", "CANCELLED"}
PROJECT_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


def utc_iso() -> str:
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp." + uuid.uuid4().hex[:8])
    data = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def normalize_project(project: str) -> str:
    p = str(project or "").strip().lower().replace(" ", "_")
    if not PROJECT_RE.fullmatch(p):
        raise ValueError("INVALID_PROJECT")
    return p


def make_idempotency_key(project: str, operation: str, source_sha: str, version: str = "") -> str:
    raw = "\n".join((normalize_project(project), str(operation), str(source_sha).lower(), str(version)))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class LaneStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.lanes = self.root / "lanes"
        self.global_root = self.root / "global"
        self.idempotency_root = self.root / "idempotency"
        for p in (self.lanes, self.global_root, self.idempotency_root):
            p.mkdir(parents=True, exist_ok=True)

    def lane_root(self, project: str) -> Path:
        return self.lanes / normalize_project(project)

    def run_root(self, project: str, run_id: str) -> Path:
        if not re.fullmatch(r"[A-Za-z0-9._-]{8,96}", str(run_id or "")):
            raise ValueError("INVALID_RUN_ID")
        return self.lane_root(project) / "runs" / run_id

    def create_or_reuse_run(
        self,
        *,
        project: str,
        operation: str,
        idempotency_key: str,
        contract: dict[str, Any],
    ) -> dict[str, Any]:
        project = normalize_project(project)
        idx = self.idempotency_root / (hashlib.sha256(idempotency_key.encode("utf-8")).hexdigest() + ".json")
        existing = read_json(idx)
        if existing:
            state = read_json(self.run_root(project, existing["run_id"]) / "state.json")
            if state:
                return {"status": "REUSED", "run": state}

        run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + uuid.uuid4().hex[:12]
        rr = self.run_root(project, run_id)
        state = {
            "schema": RUN_SCHEMA,
            "run_id": run_id,
            "project": project,
            "operation": operation,
            "idempotency_key": idempotency_key,
            "stage": "ACCEPTED",
            "status": "QUEUED",
            "restart_classification": "RESUMABLE",
            "created_at": utc_iso(),
            "updated_at": utc_iso(),
            "contract": contract,
        }
        atomic_write_json(rr / "state.json", state)
        atomic_write_json(idx, {"schema": "build2.idempotency/1", "run_id": run_id, "project": project})
        self.write_heartbeat(project, run_id, operation, "ACCEPTED", "QUEUED", last_event="run accepted")
        return {"status": "CREATED", "run": state}

    def update_state(self, project: str, run_id: str, *, stage: str, status: str, **extra: Any) -> dict[str, Any]:
        if stage not in ALLOWED_STAGES:
            raise ValueError("INVALID_STAGE")
        path = self.run_root(project, run_id) / "state.json"
        state = read_json(path)
        if not state:
            raise FileNotFoundError("RUN_NOT_FOUND")
        if state.get("stage") in TERMINAL:
            raise RuntimeError("TERMINAL_RUN_IMMUTABLE")
        state.update(extra)
        state["stage"] = stage
        state["status"] = status
        state["updated_at"] = utc_iso()
        if stage in TERMINAL:
            state["restart_classification"] = "COMPLETED" if stage == "COMPLETE" else "FAILED_SAFE"
        atomic_write_json(path, state)
        return state

    def write_heartbeat(
        self,
        project: str,
        run_id: str,
        operation: str,
        stage: str,
        status: str,
        *,
        progress_pct: int | None = None,
        last_event: str = "",
        error_class: str | None = None,
        requires_user_action: bool = False,
        artifact: str | None = None,
        artifact_sha256: str | None = None,
    ) -> dict[str, Any]:
        if stage not in ALLOWED_STAGES:
            raise ValueError("INVALID_STAGE")
        hb = {
            "schema": HEARTBEAT_SCHEMA,
            "run_id": run_id,
            "project": normalize_project(project),
            "operation": operation,
            "stage": stage,
            "status": status,
            "timestamp_utc": utc_iso(),
            "pid": os.getpid(),
            "progress_pct": progress_pct,
            "last_event": last_event,
            "error_class": error_class,
            "requires_user_action": bool(requires_user_action),
            "artifact": artifact,
            "artifact_sha256": artifact_sha256,
        }
        lane = self.lane_root(project)
        atomic_write_json(lane / "heartbeat.json", hb)
        atomic_write_json(self.run_root(project, run_id) / "heartbeat.json", hb)
        return hb

    def write_receipt(self, project: str, run_id: str, receipt: dict[str, Any]) -> Path:
        out = dict(receipt)
        out.setdefault("schema", RECEIPT_SCHEMA)
        out["run_id"] = run_id
        out["project"] = normalize_project(project)
        out.setdefault("finished_at", utc_iso())
        rr = self.run_root(project, run_id)
        path = rr / "receipt.json"
        atomic_write_json(path, out)
        atomic_write_json(self.lane_root(project) / "receipts" / f"{run_id}.json", out)
        return path

    def acquire_heavy_slot(self, project: str, run_id: str, stale_after_s: int = 8 * 3600) -> dict[str, Any]:
        lock = self.global_root / "heavy_build.lock"
        payload = {
            "schema": "build2.heavy_lock/1",
            "project": normalize_project(project),
            "run_id": run_id,
            "pid": os.getpid(),
            "acquired_at": utc_iso(),
            "acquired_epoch": time.time(),
        }
        for _ in range(2):
            try:
                fd = os.open(str(lock), os.O_WRONLY | os.O_CREAT | os.O_EXCL)
                try:
                    os.write(fd, (json.dumps(payload) + "\n").encode("utf-8"))
                finally:
                    os.close(fd)
                return {"status": "ACQUIRED", **payload}
            except FileExistsError:
                current = read_json(lock, {}) or {}
                age = time.time() - float(current.get("acquired_epoch", 0) or 0)
                if age > stale_after_s:
                    try:
                        lock.unlink()
                        continue
                    except OSError:
                        pass
                return {"status": "BUSY", "holder": current}
        return {"status": "BUSY"}

    def release_heavy_slot(self, run_id: str) -> bool:
        lock = self.global_root / "heavy_build.lock"
        current = read_json(lock, {}) or {}
        if current.get("run_id") != run_id:
            return False
        try:
            lock.unlink()
            return True
        except FileNotFoundError:
            return True
