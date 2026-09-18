from __future__ import annotations

import json
import hashlib
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from build2_supervisor import ensure_persistent_supervisor
from build2_core import (
    ROOT, GLOBAL, BUILD2_VERSION, acquire_heavy_lock, release_heavy_lock,
    heartbeat, lane_root, new_run, next_queue_entry, remove_queue_entry,
    read_json, write_receipt, recover_interrupted_runs, request_cancel,
    get_receipt
)

APP_ROOT=Path(__file__).resolve().parent
STATE_ROOT=Path(os.environ.get("LOCALAPPDATA", str(APP_ROOT))) / "MatriceBuildHub"
SOURCE_ROOT=STATE_ROOT / "PROJECT-DRAFTS"
HUB_ROOT=SOURCE_ROOT / "MATRICE-BUILD-HUB"
REGISTRY_FILE=APP_ROOT / "build2_registry.json"
AUTHORITY_FILE=APP_ROOT / "build2_source_authority.json"
SCHEDULER_PID=GLOBAL / "scheduler.pid.json"
REPO_URL="https://github.com/Terminator364/PROJECT-DRAFTS.git"

def file_sha256(path:Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda:fp.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def verify_hub_engine() -> str:
    a=authority()
    expected=str(a.get("hub_sha256") or "").lower()
    hub=HUB_ROOT/"hub.ps1"
    if not hub.is_file():
        raise RuntimeError("HUB_ENGINE_MISSING")
    got=file_sha256(hub).lower()
    if not expected or got!=expected:
        raise RuntimeError(f"HUB_ENGINE_SHA_MISMATCH expected={expected} got={got}")
    return got

def registry() -> dict:
    return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))

def authority() -> dict:
    if not AUTHORITY_FILE.is_file():
        raise RuntimeError("BUILD2_SOURCE_AUTHORITY_MISSING")
    x=json.loads(AUTHORITY_FILE.read_text(encoding="utf-8"))
    if not x.get("source_sha"):
        raise RuntimeError("BUILD2_SOURCE_SHA_MISSING")
    return x

def lane_config_for_project(project:str) -> tuple[str,dict]:
    for lname,cfg in registry().get("lanes",{}).items():
        if cfg.get("project")==project:
            return lname,cfg
    raise RuntimeError("PROJECT_NOT_REGISTERED:"+project)

def lane_config_for_operation(operation:str) -> tuple[str,dict]:
    for lname,cfg in registry().get("lanes",{}).items():
        if cfg.get("operation")==operation:
            return lname,cfg
    raise RuntimeError("OPERATION_NOT_REGISTERED:"+operation)

def which(name: str) -> str:
    p=shutil.which(name)
    if not p:
        raise RuntimeError("TOOL_MISSING:"+name)
    return p

def run(argv:list[str], cwd:Path|None=None, timeout:int=120) -> subprocess.CompletedProcess:
    return subprocess.run(argv,cwd=str(cwd) if cwd else None,capture_output=True,text=True,shell=False,timeout=timeout)

def ensure_buildhub_source() -> str:
    expected=authority()["source_sha"].lower()
    git=which("git")
    STATE_ROOT.mkdir(parents=True,exist_ok=True)
    if (SOURCE_ROOT/".git").is_dir():
        got=run([git,"-C",str(SOURCE_ROOT),"rev-parse","HEAD"],timeout=20)
        if got.returncode==0 and got.stdout.strip().lower()==expected:
            verify_hub_engine(); return expected
        has=run([git,"-C",str(SOURCE_ROOT),"cat-file","-e",expected+"^{commit}"],timeout=20)
        if has.returncode==0:
            reset=run([git,"-C",str(SOURCE_ROOT),"reset","--hard",expected],timeout=60)
            if reset.returncode==0:
                verify_hub_engine(); return expected
        fetch=run([git,"-C",str(SOURCE_ROOT),"fetch","origin",expected,"--depth=1"],timeout=120)
        if fetch.returncode!=0:
            raise RuntimeError("SOURCE_FETCH_FAILED:"+fetch.stderr[-2000:])
        reset=run([git,"-C",str(SOURCE_ROOT),"reset","--hard",expected],timeout=60)
        if reset.returncode!=0:
            raise RuntimeError("SOURCE_RESET_FAILED:"+reset.stderr[-2000:])
        verify_hub_engine(); return expected
    if SOURCE_ROOT.exists():
        shutil.rmtree(SOURCE_ROOT)
    clone=run([git,"clone","--no-checkout",REPO_URL,str(SOURCE_ROOT)],timeout=180)
    if clone.returncode!=0:
        gh=shutil.which("gh")
        if not gh:
            raise RuntimeError("SOURCE_CLONE_FAILED:"+clone.stderr[-2000:])
        clone=run([gh,"repo","clone","Terminator364/PROJECT-DRAFTS",str(SOURCE_ROOT),"--","--no-checkout"],timeout=180)
        if clone.returncode!=0:
            raise RuntimeError("SOURCE_CLONE_FAILED:"+clone.stderr[-2000:])
    fetch=run([git,"-C",str(SOURCE_ROOT),"fetch","origin",expected,"--depth=1"],timeout=120)
    if fetch.returncode!=0:
        raise RuntimeError("SOURCE_FETCH_FAILED:"+fetch.stderr[-2000:])
    reset=run([git,"-C",str(SOURCE_ROOT),"reset","--hard",expected],timeout=60)
    if reset.returncode!=0:
        raise RuntimeError("SOURCE_RESET_FAILED:"+reset.stderr[-2000:])
    verify_hub_engine(); return expected

def resolve_project_sha(project:str, lane:dict) -> str:
    pinned=(lane.get("source_sha") or "").strip().lower()
    branch=lane["branch"]
    repo=lane["repo"]
    git=which("git")
    remote=f"https://github.com/{repo}.git"
    cp=run([git,"ls-remote",remote,f"refs/heads/{branch}"],timeout=60)
    if cp.returncode!=0 or not cp.stdout.strip():
        raise RuntimeError("PROJECT_SHA_RESOLUTION_FAILED:"+repo+":"+branch)
    head=cp.stdout.split()[0].lower()
    if pinned and head!=pinned:
        raise RuntimeError(f"PROJECT_SOURCE_SHA_MISMATCH expected={pinned} branch_head={head}")
    return pinned or head

def powershell() -> str:
    root=os.environ.get("SystemRoot",r"C:\\Windows")
    p=Path(root)/"System32"/"WindowsPowerShell"/"v1.0"/"powershell.exe"
    return str(p) if p.is_file() else which("powershell.exe")

def stage_from_log(text:str, current:str) -> str:
    low=text.lower()
    if "sign" in low: return "SIGN"
    if "verify" in low or "badging" in low or "certificate" in low: return "VERIFY"
    if "release create" in low or "release upload" in low or "publish" in low: return "PUBLISH"
    if "digest" in low or "readback" in low: return "READBACK"
    if "codespace" in low or "sdkmanager" in low or "gradle" in low: return "BUILDER_PROVISION"
    if "build" in low or "compile" in low: return "BUILD"
    return current

def cancelled(project:str,run_id:str) -> bool:
    st=read_json(lane_root(project)/"runs"/run_id/"state.json",{}) or {}
    return bool(st.get("cancel_requested"))

def terminate_tree(proc:subprocess.Popen, *, grace_seconds:int=3) -> None:
    if proc.poll() is not None:
        return
    try:
        proc.terminate()
    except Exception:
        pass
    deadline=time.time()+max(0,grace_seconds)
    while proc.poll() is None and time.time()<deadline:
        time.sleep(0.2)
    if proc.poll() is not None:
        return
    if os.name=="nt":
        taskkill=shutil.which("taskkill")
        if taskkill:
            try:
                subprocess.run([taskkill,"/PID",str(proc.pid),"/T","/F"],
                               capture_output=True,text=True,shell=False,timeout=15)
            except Exception:
                pass
    if proc.poll() is None:
        try:
            proc.kill()
        except Exception:
            pass

def classify_process_exit(rc:int) -> tuple[str,str]:
    raw=int(rc) & 0xFFFFFFFF
    hx=f"0x{raw:08X}"
    if raw==0xC000013A:
        return "EXTERNAL_TERMINATION_CTRL_EVENT",hx
    if raw>=0xC0000000:
        return "EXTERNAL_TERMINATION_NTSTATUS",hx
    return "BUILD_PROCESS_FAILED",hx

def process_doctor(run_id:str) -> None:
    project="BuildHub"
    evidence=[]
    try:
        heartbeat(project,run_id,"PREFLIGHT","RUNNING",detail="BUILD 2 doctor probes",progress_pct=20)
        a=authority(); evidence.append({"kind":"source_authority","value":a})
        evidence.append({"kind":"build2_version","value":BUILD2_VERSION})
        evidence.append({"kind":"python","executable":sys.executable,"version":sys.version.split()[0]})
        for name in ("bridge.py","build2_worker.py","build2_core.py","selftest.py","build2_registry.json"):
            p=APP_ROOT/name
            evidence.append({"kind":"managed_component","name":name,"sha256":file_sha256(p) if p.is_file() else None})
        evidence.append({"kind":"control_bus","configured":bool(str(os.environ.get("PCA_CONTROL_FOLDER") or "").strip())})
        reg=registry(); evidence.append({"kind":"registry_version","value":reg.get("version")})
        git=which("git"); evidence.append({"kind":"git","value":git})
        gv=run([git,"--version"],timeout=10)
        evidence.append({"kind":"git_version","value":(gv.stdout or gv.stderr).strip()})
        ps=powershell(); evidence.append({"kind":"powershell","value":ps})
        pv=run([ps,"-NoProfile","-Command","$PSVersionTable.PSVersion.ToString()"],timeout=10)
        evidence.append({"kind":"powershell_version","value":(pv.stdout or pv.stderr).strip()})
        source_sha=ensure_buildhub_source()
        evidence.append({"kind":"buildhub_source_sha","value":source_sha})
        evidence.append({"kind":"hub_engine_sha256","value":verify_hub_engine()})
        usage=shutil.disk_usage(str(STATE_ROOT))
        evidence.append({"kind":"disk_free_bytes","value":usage.free})
        if os.name=="nt":
            try:
                import ctypes
                class MS(ctypes.Structure):
                    _fields_=[("dwLength",ctypes.c_ulong),("dwMemoryLoad",ctypes.c_ulong),
                              ("ullTotalPhys",ctypes.c_ulonglong),("ullAvailPhys",ctypes.c_ulonglong),
                              ("ullTotalPageFile",ctypes.c_ulonglong),("ullAvailPageFile",ctypes.c_ulonglong),
                              ("ullTotalVirtual",ctypes.c_ulonglong),("ullAvailVirtual",ctypes.c_ulonglong),
                              ("ullAvailExtendedVirtual",ctypes.c_ulonglong)]
                m=MS(); m.dwLength=ctypes.sizeof(MS)
                ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
                evidence.append({"kind":"memory","load_pct":m.dwMemoryLoad,"avail_phys":m.ullAvailPhys,"avail_commit":m.ullAvailPageFile})
                if m.dwMemoryLoad>=97:
                    write_receipt(project,run_id,"HOLD",stage="PREFLIGHT",evidence=evidence,error_class="MEMORY_CRITICAL",detail="Memory pressure too high for safe heavy build"); return
            except Exception as e:
                evidence.append({"kind":"memory_probe","status":"UNAVAILABLE","detail":str(e)[:200]})
        expected=a.get("source_sha","").lower()
        if (SOURCE_ROOT/".git").is_dir():
            got=run([git,"-C",str(SOURCE_ROOT),"rev-parse","HEAD"],timeout=15)
            evidence.append({"kind":"local_source_head","value":got.stdout.strip().lower() if got.returncode==0 else None})
        gh=shutil.which("gh")
        if gh:
            probe=run([gh,"codespace","list","--limit","1"],timeout=20)
            evidence.append({"kind":"codespaces_probe","status":"PASS" if probe.returncode==0 else "HOLD","stderr":probe.stderr[-500:]})
            if probe.returncode!=0:
                write_receipt(project,run_id,"HOLD",stage="PREFLIGHT",evidence=evidence,error_class="CODESPACES_UNAVAILABLE",detail="Codespaces probe did not pass within bounded doctor"); return
        else:
            write_receipt(project,run_id,"HOLD",stage="PREFLIGHT",evidence=evidence,error_class="GH_MISSING",detail="GitHub CLI unavailable"); return
        write_receipt(project,run_id,"COMPLETE",stage="COMPLETE",evidence=evidence,detail="BUILD 2 doctor PASS")
    except subprocess.TimeoutExpired:
        write_receipt(project,run_id,"HOLD",stage="PREFLIGHT",evidence=evidence,error_class="DOCTOR_TIMEOUT",detail="External doctor probe timed out safely")
    except Exception as e:
        write_receipt(project,run_id,"FAILED_SAFE",stage="PREFLIGHT",evidence=evidence,error_class=type(e).__name__,detail=str(e)[:4000])

def process_run(project:str,run_id:str) -> None:
    if project=="BuildHub":
        process_doctor(run_id); return
    _,lane_cfg=lane_config_for_project(project)
    lane=lane_root(project)
    state_path=lane/"runs"/run_id/"state.json"
    st=read_json(state_path,{}) or {}
    st["status"]="RUNNING"; st["pid"]=os.getpid()
    from build2_core import atomic_json
    atomic_json(state_path,st)
    log=lane/"logs"/f"{run_id}.log"
    try:
        heartbeat(project,run_id,"SOURCE_SYNC","RUNNING",detail="Checking exact BuildHub source and project source",progress_pct=8)
        buildhub_sha=ensure_buildhub_source()
        project_sha=resolve_project_sha(project,lane_cfg)
        st=read_json(state_path,{}) or {}
        st.setdefault("contract",{})["resolved_source_sha"]=project_sha
        st["contract"]["buildhub_source_sha"]=buildhub_sha
        atomic_json(state_path,st)

        if cancelled(project,run_id):
            write_receipt(project,run_id,"CANCELLED",stage="SOURCE_SYNC",detail="Cancelled before preflight"); return

        ps=powershell()
        heartbeat(project,run_id,"PREFLIGHT","RUNNING",detail="Running BuildHub self-test and project contract gates",progress_pct=15)
        pre=run([ps,"-NoProfile","-ExecutionPolicy","Bypass","-File",str(HUB_ROOT/"self-test.ps1")],cwd=HUB_ROOT,timeout=240)
        if pre.returncode!=0:
            write_receipt(project,run_id,"FAILED_SAFE",stage="PREFLIGHT",error_class="SELFTEST_FAILED",detail=(pre.stdout+pre.stderr)[-4000:]); return

        heartbeat(project,run_id,"BUILDER_PROVISION","RUNNING",detail="Starting bounded shared builder",progress_pct=25)
        cmd=[ps,"-NoProfile","-ExecutionPolicy","Bypass","-File",str(HUB_ROOT/"hub.ps1"),"-Project",project,"-Branch",str(lane_cfg["branch"]),"-ExpectedSha",project_sha,"-Mode","Build"]
        log.parent.mkdir(parents=True,exist_ok=True)
        with log.open("w",encoding="utf-8",errors="replace") as lf:
            proc=subprocess.Popen(cmd,cwd=str(HUB_ROOT),stdout=lf,stderr=subprocess.STDOUT,text=True,shell=False)
        last_pos=0; stage="BUILDER_PROVISION"; started=time.time()
        timeout=int(lane_cfg.get("build_timeout_minutes",45))*60 + 900
        while proc.poll() is None:
            if cancelled(project,run_id):
                terminate_tree(proc)
                write_receipt(project,run_id,"CANCELLED",stage=stage,detail="Cancellation executed against the run process subtree"); return
            if time.time()-started>timeout:
                terminate_tree(proc)
                write_receipt(project,run_id,"FAILED_SAFE",stage=stage,error_class="OPERATION_TIMEOUT",detail="Build exceeded bounded timeout; run subtree terminated"); return
            try:
                txt=log.read_text(encoding="utf-8",errors="replace")
                tail=txt[last_pos:]; last_pos=len(txt)
                ns=stage_from_log(tail,stage)
                if ns!=stage:
                    stage=ns
                    pct={"BUILDER_PROVISION":25,"BUILD":45,"SIGN":65,"VERIFY":78,"PUBLISH":88,"READBACK":95}.get(stage,40)
                    heartbeat(project,run_id,stage,"RUNNING",detail=f"Observed stage {stage}",progress_pct=pct,pid=proc.pid)
            except Exception:
                pass
            time.sleep(2)
        rc=proc.returncode
        tail=log.read_text(encoding="utf-8",errors="replace")[-12000:] if log.is_file() else ""
        if rc!=0:
            err_class,rc_hex=classify_process_exit(rc)
            evidence=[
                {"kind":"process_exit","return_code":int(rc),"return_code_unsigned":int(rc)&0xFFFFFFFF,"return_code_hex":rc_hex},
                {"kind":"log","path":str(log),"bytes":log.stat().st_size if log.is_file() else 0}
            ]
            detail=tail[-4000:] if tail else f"Build process exited with {rc_hex} and produced no diagnostic output."
            write_receipt(project,run_id,"FAILED_SAFE",stage=stage,evidence=evidence,error_class=err_class,detail=detail); return
        heartbeat(project,run_id,"READBACK","RUNNING",detail="Build process passed; collecting durable proof",progress_pct=96)
        evidence=[
            {"kind":"buildhub_source_sha","value":buildhub_sha},
            {"kind":"project_source_sha","value":project_sha},
            {"kind":"log","path":str(log)}
        ]
        write_receipt(project,run_id,"COMPLETE",stage="COMPLETE",evidence=evidence,detail="Unified BuildHub operation completed; project-specific artifact gates remain encoded in hub/recipe.")
    except Exception as e:
        write_receipt(project,run_id,"FAILED_SAFE",stage=(read_json(state_path,{}) or {}).get("stage","ACCEPTED"),error_class=type(e).__name__,detail=str(e)[:4000])

def scheduler(gate_path:str|None=None) -> int:
    if gate_path:
        gate=Path(gate_path)
        deadline=time.time()+30
        while not gate.is_file() and time.time()<deadline:
            time.sleep(0.1)
        if not gate.is_file():
            return 75
    recover_interrupted_runs()
    while True:
        nxt=next_queue_entry()
        if not nxt:
            return 0
        qpath,item=nxt
        project=item["project"]; run_id=item["run_id"]
        if not acquire_heavy_lock(run_id,project):
            time.sleep(2); continue
        try:
            remove_queue_entry(qpath)
            process_run(project,run_id)
        finally:
            release_heavy_lock(run_id)

def scheduler_alive() -> bool:
    x=read_json(SCHEDULER_PID,{}) or {}
    pid=int(x.get("pid") or 0)
    if pid<=0: return False
    try: os.kill(pid,0); return True
    except Exception: return False

def ensure_scheduler() -> dict:
    # The supervisor is the durable owner. It is launched outside a transient
    # command-handler job when necessary and owns the scheduler's kill-on-close
    # Windows Job Object.
    return ensure_persistent_supervisor(str(Path(__file__).resolve()))

def enqueue(project:str,operation:str) -> dict:
    if project=="BuildHub":
        result=new_run("BuildHub","doctor",{"build2_version":BUILD2_VERSION,"kind":"system_doctor"},priority=90)
        if result.get("status") in {"QUEUED","IDEMPOTENT_REUSE"}:
            result["scheduler"]=ensure_scheduler()
        return result
    _,cfg=lane_config_for_project(project)
    contract=dict(cfg)
    result=new_run(project,operation,contract)
    if result.get("status") in {"QUEUED","IDEMPOTENT_REUSE"}:
        result["scheduler"]=ensure_scheduler()
    return result

def latest_status() -> dict:
    from build2_core import LATEST
    return read_json(LATEST,{"status":"NO_RUN"})

if __name__=="__main__":
    cmd=sys.argv[1] if len(sys.argv)>1 else ""
    if cmd=="scheduler":
        raise SystemExit(scheduler(sys.argv[2] if len(sys.argv)>2 else None))
    if cmd=="enqueue" and len(sys.argv)==4:
        print(json.dumps(enqueue(sys.argv[2],sys.argv[3]),ensure_ascii=False)); raise SystemExit(0)
    if cmd=="status":
        print(json.dumps(latest_status(),ensure_ascii=False)); raise SystemExit(0)
    if cmd=="receipt" and len(sys.argv)>=3:
        print(json.dumps(get_receipt(sys.argv[2],sys.argv[3] if len(sys.argv)>3 else None),ensure_ascii=False)); raise SystemExit(0)
    if cmd=="cancel" and len(sys.argv)==4:
        print(json.dumps(request_cancel(sys.argv[2],sys.argv[3]),ensure_ascii=False)); raise SystemExit(0)
    raise SystemExit("USAGE")
