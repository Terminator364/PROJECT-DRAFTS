from __future__ import annotations
import json
import os
import subprocess
import sys
from pathlib import Path

APP_ROOT=Path(__file__).resolve().parent
HUB_ROOT=APP_ROOT/"hub"
STATE_ROOT=Path(os.environ.get("LOCALAPPDATA", str(APP_ROOT))) / "MatriceBuildHub"
RESULT_FILE=STATE_ROOT / "managed-bridge-last-result.json"

OPERATIONS={
    "doctor":["-Mode","Doctor"],
    "build_phonemouse":["-Project","PhoneMouse","-Mode","Build"],
    "build_p2pcr95":["-Project","P2PCR95","-Mode","Build"],
    "build_chatgpt_pc":["-Project","ChatGPT-PC","-Mode","Build"],
}

def fail(code:str,message:str,rc:int=2):
    payload={"schema":"mbh-managed-bridge-result-v1","status":"FAIL","code":code,"message":message}
    print(json.dumps(payload,ensure_ascii=False))
    raise SystemExit(rc)

def write_result(payload:dict):
    STATE_ROOT.mkdir(parents=True,exist_ok=True)
    tmp=RESULT_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    os.replace(tmp,RESULT_FILE)

def powershell_exe()->str:
    root=os.environ.get("SystemRoot",r"C:\Windows")
    candidate=Path(root)/"System32"/"WindowsPowerShell"/"v1.0"/"powershell.exe"
    if candidate.is_file(): return str(candidate)
    return "powershell.exe"

def run(operation:str)->int:
    if operation=="last_build_status":
        if RESULT_FILE.is_file():
            print(RESULT_FILE.read_text(encoding="utf-8",errors="replace"))
        else:
            print(json.dumps({"schema":"mbh-managed-bridge-result-v1","status":"NO_RESULT"}))
        return 0
    if operation not in OPERATIONS:
        fail("OPERATION_NOT_REGISTERED","Unknown managed operation.")
    hub=HUB_ROOT/"hub.ps1"
    if not hub.is_file():
        fail("HUB_PAYLOAD_MISSING","Embedded BuildHub hub.ps1 is missing.")
    selftest=HUB_ROOT/"self-test.ps1"
    if not selftest.is_file():
        fail("SELF_TEST_MISSING","Embedded BuildHub self-test.ps1 is missing.")
    ps=powershell_exe()
    pre=[ps,"-NoProfile","-ExecutionPolicy","Bypass","-File",str(selftest)]
    p=subprocess.run(pre,cwd=HUB_ROOT,capture_output=True,text=True,shell=False,timeout=180)
    if p.returncode!=0:
        payload={"schema":"mbh-managed-bridge-result-v1","status":"FAIL","operation":operation,"code":"STATIC_SELF_TEST_FAILED","returncode":p.returncode,"stdout":p.stdout[-12000:],"stderr":p.stderr[-12000:]}
        write_result(payload); print(json.dumps(payload,ensure_ascii=False)); return p.returncode or 3
    argv=[ps,"-NoProfile","-ExecutionPolicy","Bypass","-File",str(hub),*OPERATIONS[operation]]
    try:
        p=subprocess.run(argv,cwd=HUB_ROOT,capture_output=True,text=True,shell=False,timeout=7500)
    except subprocess.TimeoutExpired as e:
        payload={"schema":"mbh-managed-bridge-result-v1","status":"FAIL","operation":operation,"code":"OPERATION_TIMEOUT","stdout":(e.stdout or "")[-12000:],"stderr":(e.stderr or "")[-12000:]}
        write_result(payload); print(json.dumps(payload,ensure_ascii=False)); return 124
    payload={
        "schema":"mbh-managed-bridge-result-v1",
        "status":"PASS" if p.returncode==0 else "FAIL",
        "operation":operation,
        "returncode":p.returncode,
        "stdout":p.stdout[-20000:],
        "stderr":p.stderr[-20000:],
    }
    write_result(payload)
    print(json.dumps(payload,ensure_ascii=False))
    return p.returncode

if __name__=="__main__":
    if len(sys.argv)!=2:
        fail("USAGE","Exactly one registered operation name is required.")
    raise SystemExit(run(sys.argv[1]))
