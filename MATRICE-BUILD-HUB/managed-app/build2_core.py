from __future__ import annotations

import hashlib
import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any

BUILD2_VERSION = "0.5.3-recovery-unblock-context"
ROOT = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "MatriceBuildHub" / "build2"
LANES = ROOT / "lanes"
GLOBAL = ROOT / "global"
QUEUE = GLOBAL / "queue"
LOCK = GLOBAL / "heavy-build.lock.json"
LATEST = GLOBAL / "latest.json"

TERMINAL = {"COMPLETE", "FAILED_SAFE", "HOLD", "CANCELLED"}
SAFE_RESUME_STAGES = {"ACCEPTED","SOURCE_SYNC","PREFLIGHT","BUILDER_PROVISION","BUILD","SIGN","VERIFY"}

def utc() -> str:
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00","Z")

def atomic_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)

def control_root() -> Path|None:
    raw=str(os.environ.get("PCA_CONTROL_FOLDER") or "").strip()
    return Path(raw) if raw else None

def spool_json(rel: str, data: dict[str,Any]) -> None:
    root=control_root()
    if not root:
        return
    try:
        atomic_json(root/rel,data)
    except Exception:
        # Local run state remains authoritative if Drive is temporarily unavailable.
        pass

def read_json(path: Path, default: Any=None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def lane_name(project: str) -> str:
    if project=="BuildHub":
        return "system"
    lane=re.sub(r"[^a-z0-9]+","_",project.strip().lower()).strip("_")
    if not lane or len(lane)>80:
        raise ValueError(f"BAD_PROJECT_LANE:{project}")
    return lane

def lane_root(project: str) -> Path:
    p = LANES / lane_name(project)
    for d in ("queue","runs","receipts","logs","artifacts/staging","artifacts/published","idempotency"):
        (p / d).mkdir(parents=True, exist_ok=True)
    return p

def canonical_hash(data: Any) -> str:
    raw=json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def _run_paths(project: str, run_id: str) -> tuple[Path,Path,Path]:
    lane=lane_root(project)
    run=lane/"runs"/run_id
    run.mkdir(parents=True, exist_ok=True)
    return run, run/"state.json", lane/"heartbeat.json"

def heartbeat(project: str, run_id: str, stage: str, status: str, *,
              detail: str="", progress_pct: int|None=None, pid: int|None=None,
              error_class: str|None=None, requires_user_action: bool=False,
              artifact: dict[str,Any]|None=None) -> dict[str,Any]:
    run,state_path,hb_path=_run_paths(project,run_id)
    old=read_json(state_path,{}) or {}
    payload={
        "schema":"build2.heartbeat/1",
        "build2_version":BUILD2_VERSION,
        "project":project,
        "lane":lane_name(project),
        "run_id":run_id,
        "operation":old.get("operation"),
        "stage":stage,
        "status":status,
        "timestamp_utc":utc(),
        "pid":pid if pid is not None else os.getpid(),
        "progress_pct":progress_pct,
        "last_event":detail,
        "error_class":error_class,
        "requires_user_action":bool(requires_user_action),
        "artifact":artifact,
    }
    state={**old,**payload,"updated_at":payload["timestamp_utc"]}
    atomic_json(state_path,state)
    atomic_json(hb_path,payload)
    latest={"project":project,"run_id":run_id,"stage":stage,"status":status,"timestamp_utc":payload["timestamp_utc"]}
    atomic_json(LATEST,latest)
    lane=lane_name(project)
    spool_json(f"11_PROJECTS/BUILD2/{lane}/heartbeat.json",payload)
    spool_json("00_CONTEXT/BUILD2_LIVE.json",{**latest,"build2_version":BUILD2_VERSION})
    return payload

def new_run(project: str, operation: str, contract: dict[str,Any], *,
            idempotency_key: str|None=None, priority: int=50) -> dict[str,Any]:
    lane=lane_root(project)
    queued=list_queue()
    if len(queued) >= 8:
        return {"status":"HOLD","code":"QUEUE_FULL","queue_depth":len(queued)}
    material={"project":project,"operation":operation,"contract":contract}
    key=idempotency_key or canonical_hash(material)
    idx=lane/"idempotency"/f"{key}.json"
    prior=read_json(idx)
    if prior:
        st=read_json(lane/"runs"/prior["run_id"]/"state.json",{})
        if st and st.get("status") in {"QUEUED","RUNNING"}:
            return {"status":"IDEMPOTENT_REUSE","run_id":prior["run_id"],"state":st}
    run_id=time.strftime("%Y%m%dT%H%M%SZ",time.gmtime())+"-"+uuid.uuid4().hex[:12]
    run,state_path,_=_run_paths(project,run_id)
    created=utc()
    state={
        "schema":"build2.run_state/1","build2_version":BUILD2_VERSION,
        "project":project,"lane":lane_name(project),"run_id":run_id,
        "operation":operation,"status":"QUEUED","stage":"ACCEPTED",
        "created_at":created,"updated_at":created,"priority":int(priority),
        "idempotency_key":key,"contract":contract,"cancel_requested":False,
        "recovery_class":None,
    }
    atomic_json(state_path,state)
    atomic_json(run/"contract.json",contract)
    atomic_json(idx,{"run_id":run_id,"idempotency_key":key,"created_at":created})
    q=QUEUE/f"{999-int(priority):03d}-{time.time_ns()}-{run_id}.json"
    atomic_json(q,{"schema":"build2.queue_entry/1","run_id":run_id,"project":project,"priority":int(priority),"created_at":created})
    heartbeat(project,run_id,"ACCEPTED","QUEUED",detail="Build accepted into shared bounded queue",progress_pct=0)
    return {"status":"QUEUED","run_id":run_id,"idempotency_key":key}

def list_queue() -> list[dict[str,Any]]:
    QUEUE.mkdir(parents=True,exist_ok=True)
    out=[]
    for p in sorted(QUEUE.glob("*.json")):
        x=read_json(p)
        if x: out.append({**x,"queue_file":str(p)})
    return out

def next_queue_entry() -> tuple[Path,dict[str,Any]]|None:
    QUEUE.mkdir(parents=True,exist_ok=True)
    for p in sorted(QUEUE.glob("*.json")):
        x=read_json(p)
        if x: return p,x
    return None

def remove_queue_entry(path: Path) -> None:
    try: path.unlink()
    except FileNotFoundError: pass

def request_cancel(project: str, run_id: str) -> dict[str,Any]:
    lane=lane_root(project)
    sp=lane/"runs"/run_id/"state.json"
    st=read_json(sp)
    if not st: return {"status":"NOT_FOUND","run_id":run_id}
    if st.get("status") in TERMINAL: return {"status":"ALREADY_TERMINAL","state":st}
    st["cancel_requested"]=True; st["cancel_requested_at"]=utc()
    atomic_json(sp,st)
    heartbeat(project,run_id,st.get("stage","ACCEPTED"),st.get("status","QUEUED"),detail="Cancellation requested")
    return {"status":"CANCEL_REQUESTED","run_id":run_id}

def get_receipt(project: str, run_id: str|None=None) -> dict[str,Any]:
    lane=lane_root(project)
    if run_id:
        p=lane/"receipts"/f"{run_id}.json"
        return read_json(p,{"status":"NOT_FOUND","project":project,"run_id":run_id})
    receipts=sorted((lane/"receipts").glob("*.json"),key=lambda p:p.stat().st_mtime,reverse=True)
    if receipts: return read_json(receipts[0],{"status":"UNREADABLE"})
    hb=read_json(lane/"heartbeat.json")
    return hb or {"status":"NO_RUN","project":project}

def write_receipt(project: str, run_id: str, result: str, *,
                  stage: str, evidence: list[dict[str,Any]]|None=None,
                  artifacts: list[dict[str,Any]]|None=None,
                  error_class: str|None=None, detail: str="") -> dict[str,Any]:
    lane=lane_root(project)
    st=read_json(lane/"runs"/run_id/"state.json",{}) or {}
    rec={
        "schema":"build2.receipt/1","build2_version":BUILD2_VERSION,
        "project":project,"lane":lane_name(project),"run_id":run_id,
        "operation":st.get("operation"),"result":result,"stage":stage,
        "finished_at":utc(),"source_contract_hash":canonical_hash(st.get("contract",{})),
        "evidence":evidence or [],"artifacts":artifacts or [],
        "error_class":error_class,"detail":detail,
        "requires_user_action":False,
    }
    atomic_json(lane/"receipts"/f"{run_id}.json",rec)
    spool_json(f"11_PROJECTS/BUILD2/{lane_name(project)}/receipts/{run_id}.json",rec)
    heartbeat(project,run_id,stage,result,detail=detail,error_class=error_class,
              progress_pct=100 if result=="COMPLETE" else None,artifact=(artifacts or [None])[0])
    return rec

def _pid_alive(pid: int) -> bool:
    if pid<=0: return False
    try:
        os.kill(pid,0); return True
    except Exception:
        return False

def acquire_heavy_lock(run_id: str, project: str) -> bool:
    GLOBAL.mkdir(parents=True,exist_ok=True)
    if LOCK.exists():
        cur=read_json(LOCK,{}) or {}
        pid=int(cur.get("pid") or 0)
        age=time.time()-float(cur.get("epoch") or 0)
        if _pid_alive(pid) and age < 8*3600:
            return False
        try: LOCK.unlink()
        except OSError: return False
    payload={"schema":"build2.heavy_lock/1","run_id":run_id,"project":project,"pid":os.getpid(),"epoch":time.time(),"acquired_at":utc()}
    try:
        fd=os.open(str(LOCK),os.O_WRONLY|os.O_CREAT|os.O_EXCL)
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            json.dump(payload,f,ensure_ascii=False,indent=2); f.write("\n")
        return True
    except FileExistsError:
        return False

def release_heavy_lock(run_id: str) -> None:
    cur=read_json(LOCK,{}) or {}
    if cur.get("run_id")==run_id:
        try: LOCK.unlink()
        except FileNotFoundError: pass

def recover_interrupted_runs() -> list[dict[str,Any]]:
    recovered=[]
    if not LANES.exists(): return recovered
    for lane in LANES.iterdir():
        if not lane.is_dir(): continue
        for sp in (lane/"runs").glob("*/state.json"):
            st=read_json(sp,{}) or {}
            if st.get("status")!="RUNNING": continue
            pid=int(st.get("pid") or 0)
            if _pid_alive(pid): continue
            stage=st.get("stage","ACCEPTED")
            cls="RESUMABLE" if stage in SAFE_RESUME_STAGES else "FAILED_SAFE"
            st["recovery_class"]=cls
            st["status"]="QUEUED" if cls=="RESUMABLE" else "FAILED_SAFE"
            st["updated_at"]=utc()
            atomic_json(sp,st)
            if cls=="RESUMABLE":
                q=QUEUE/f"050-{time.time_ns()}-{st['run_id']}.json"
                atomic_json(q,{"schema":"build2.queue_entry/1","run_id":st["run_id"],"project":st["project"],"priority":50,"created_at":utc(),"recovered":True})
            recovered.append({"run_id":st.get("run_id"),"project":st.get("project"),"recovery_class":cls})
    return recovered
