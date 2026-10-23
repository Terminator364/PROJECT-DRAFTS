#!/usr/bin/env python3
"""BCP Remote V4 ADB companion. Physical authorised ADB device -> loopback only.
Never exposes an unauthenticated remote shell or any Internet listener.
"""
import os, pathlib, re, subprocess, sys, time, json
ROOT=pathlib.Path(os.environ["LOCALAPPDATA"])/"BCP-USB-Rescue"
ADB=ROOT/"tools"/"platform-tools"/"adb.exe"
STATE=ROOT/"private-state"
WORKSPACE=ROOT/"workspace"
LOG=ROOT/"logs"/"adb-v4.jsonl"
AGENT=ROOT/"windows"/"bridge_agent.py"
assert AGENT.is_file(),"Missing legacy R3.3 agent"
sys.path.insert(0,str(AGENT.parent))
from bridge_agent import Bridge,reverse_once
def emit(code,detail):
    LOG.parent.mkdir(parents=True,exist_ok=True)
    with LOG.open("a",encoding="utf-8") as f:
        f.write(json.dumps({"utc":int(time.time()),"code":code,"detail":detail},separators=(",",":"))+"\n")
def adb(*args,timeout=9):
    return subprocess.run([str(ADB),*args],capture_output=True,text=True,timeout=timeout,check=False)
def unique_authorized_serial():
    r=adb("devices","-l")
    if r.returncode: return None
    serials=[]
    for line in r.stdout.splitlines():
        match=re.match(r"^([A-Za-z0-9._:-]{4,90})\s+device(?:\s|$)",line)
        if match: serials.append(match.group(1))
    return serials[0] if len(serials)==1 else None
def main():
    if not ADB.is_file():
        emit("WAIT_ADB","Android platform-tools are not installed in trusted local path");return 4
    bridge=Bridge(STATE,WORKSPACE)
    previous=""
    emit("GUARDIAN_START","ADB loopback forward 18768 to Android 8768, no public listener")
    while True:
        try:
            serial=unique_authorized_serial()
            if not serial:
                if previous:
                    try:adb("-s",previous,"forward","--remove","tcp:18768")
                    except Exception:pass
                previous=""
                time.sleep(7);continue
            if serial!=previous:
                if previous:
                    try:adb("-s",previous,"forward","--remove","tcp:18768")
                    except Exception:pass
                previous=serial
                emit("DEVICE_AUTHORIZED","One trusted USB ADB device detected")
            result=adb("-s",serial,"forward","tcp:18768","tcp:8768")
            if result.returncode!=0:
                time.sleep(5);continue
            try:
                answer=reverse_once(bridge,"127.0.0.1","127.0.0.1",port=18768,timeout=3)
                if answer=="RPC_REPLIED": emit("AUTHENTICATED_REPLY","Android request answered with signed RPC")
            except (OSError,ValueError,TimeoutError):
                pass
        except (OSError,subprocess.TimeoutExpired) as exc:
            emit("RETRY",type(exc).__name__)
        time.sleep(2)
if __name__=="__main__":
    raise SystemExit(main())