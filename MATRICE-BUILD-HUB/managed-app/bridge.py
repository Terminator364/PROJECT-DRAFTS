from __future__ import annotations
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

APP_ROOT=Path(__file__).resolve().parent
STATE_ROOT=Path(os.environ.get("LOCALAPPDATA", str(APP_ROOT))) / "MatriceBuildHub"
RESULT_FILE=STATE_ROOT / "managed-bridge-last-result.json"
SOURCE_ROOT=STATE_ROOT / "PROJECT-DRAFTS"
HUB_ROOT=SOURCE_ROOT / "MATRICE-BUILD-HUB"
REPO="Terminator364/PROJECT-DRAFTS"
SOURCE_SHA="7d61ab980d6718fdb49322282bf00c56fe9bb7c8"

OPERATIONS={
    "doctor":["-Mode","Doctor"],
    "build_phonemouse":["-Project","PhoneMouse","-Mode","Build"],
    "build_p2pcr95":["-Project","P2PCR95","-Mode","Build"],
    "build_chatgpt_pc":["-Project","ChatGPT-PC","-Mode","Build"],
}

def payload(status:str,**extra):
    return {"schema":"mbh-managed-bridge-result-v2","status":status,**extra}

def write_result(data:dict):
    STATE_ROOT.mkdir(parents=True,exist_ok=True)
    tmp=RESULT_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    os.replace(tmp,RESULT_FILE)

def fail(code:str,message:str,rc:int=2):
    data=payload("FAIL",code=code,message=message)
    write_result(data)
    print(json.dumps(data,ensure_ascii=False))
    raise SystemExit(rc)

def which(name:str)->str:
    p=shutil.which(name)
    if not p: fail("TOOL_MISSING",f"{name} is not installed.")
    return p

def run_checked(argv:list[str],cwd:Path|None=None,timeout:int=300)->subprocess.CompletedProcess:
    try:
        cp=subprocess.run(argv,cwd=str(cwd) if cwd else None,capture_output=True,text=True,shell=False,timeout=timeout)
    except subprocess.TimeoutExpired as e:
        fail("PROCESS_TIMEOUT",f"Timed out: {argv[0]}",124)
    if cp.returncode!=0:
        data=payload("FAIL",code="PROCESS_FAILED",argv0=Path(argv[0]).name,returncode=cp.returncode,stdout=(cp.stdout or "")[-12000:],stderr=(cp.stderr or "")[-12000:])
        write_result(data); print(json.dumps(data,ensure_ascii=False)); raise SystemExit(cp.returncode or 3)
    return cp

def ensure_source()->dict:
    gh=which("gh"); git=which("git")
    auth=run_checked([gh,"auth","status","-h","github.com"],timeout=30)
    STATE_ROOT.mkdir(parents=True,exist_ok=True)
    if not (SOURCE_ROOT/".git").is_dir():
        if SOURCE_ROOT.exists(): shutil.rmtree(SOURCE_ROOT)
        run_checked([gh,"repo","clone",REPO,str(SOURCE_ROOT)],timeout=300)
    run_checked([git,"-C",str(SOURCE_ROOT),"fetch","origin",SOURCE_SHA,"--quiet"],timeout=180)
    run_checked([git,"-C",str(SOURCE_ROOT),"reset","--hard",SOURCE_SHA,"--quiet"],timeout=60)
    got=run_checked([git,"-C",str(SOURCE_ROOT),"rev-parse","HEAD"],timeout=30).stdout.strip().lower()
    if got!=SOURCE_SHA:
        fail("SOURCE_SHA_MISMATCH",f"Expected {SOURCE_SHA}, got {got}.")
    hub=HUB_ROOT/"hub.ps1"
    st=HUB_ROOT/"self-test.ps1"
    if not hub.is_file() or not st.is_file():
        fail("HUB_SOURCE_MISSING","Pinned BuildHub source is incomplete.")
    return {"source_sha":got,"source_root":str(SOURCE_ROOT),"gh_auth":"PASS"}

def powershell_exe()->str:
    root=os.environ.get("SystemRoot",r"C:\Windows")
    p=Path(root)/"System32"/"WindowsPowerShell"/"v1.0"/"powershell.exe"
    return str(p) if p.is_file() else which("powershell.exe")

def run(operation:str)->int:
    if operation=="last_build_status":
        if RESULT_FILE.is_file(): print(RESULT_FILE.read_text(encoding="utf-8",errors="replace"))
        else: print(json.dumps(payload("NO_RESULT")))
        return 0
    if operation not in OPERATIONS:
        fail("OPERATION_NOT_REGISTERED","Unknown managed operation.")
    sync=ensure_source()
    ps=powershell_exe()
    pre=run_checked([ps,"-NoProfile","-ExecutionPolicy","Bypass","-File",str(HUB_ROOT/"self-test.ps1")],cwd=HUB_ROOT,timeout=240)
    argv=[ps,"-NoProfile","-ExecutionPolicy","Bypass","-File",str(HUB_ROOT/"hub.ps1"),*OPERATIONS[operation]]
    try:
        cp=subprocess.run(argv,cwd=str(HUB_ROOT),capture_output=True,text=True,shell=False,timeout=7500)
    except subprocess.TimeoutExpired as e:
        data=payload("FAIL",operation=operation,code="OPERATION_TIMEOUT",source_sha=sync["source_sha"],stdout=(e.stdout or "")[-12000:],stderr=(e.stderr or "")[-12000:])
        write_result(data); print(json.dumps(data,ensure_ascii=False)); return 124
    data=payload("PASS" if cp.returncode==0 else "FAIL",operation=operation,returncode=cp.returncode,source_sha=sync["source_sha"],stdout=(cp.stdout or "")[-20000:],stderr=(cp.stderr or "")[-20000:])
    write_result(data); print(json.dumps(data,ensure_ascii=False))
    return cp.returncode

if __name__=="__main__":
    if len(sys.argv)!=2: fail("USAGE","Exactly one registered operation name is required.")
    raise SystemExit(run(sys.argv[1]))
