#!/usr/bin/env python3
"""BCP data worker: local-only audit. Zero HTTP requests, 60s heartbeat, 5m audit."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import time

from collector import audit

HERE=Path(__file__).resolve().parent

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

def atomic(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(".pending")
    tmp.write_text(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    os.replace(tmp,path)

def event(folder, what, **fields):
    with (folder/"events.jsonl").open("a",encoding="utf-8") as fp:
        fp.write(json.dumps({"utc":now(),"event":what,**fields},ensure_ascii=False)+"\n")

def inspect_cache(source_folder, group):
    manifest=json.loads((source_folder/"manifest.json").read_text(encoding="utf-8"))
    reports={}
    errors=[]
    for key, src in manifest["sources"].items():
        if src.get("status")!="validated": continue
        if group=="E0" and not key.endswith("_E0"): continue
        checksum=src["sha256"]
        name=source_folder/"raw"/(checksum+".csv")
        try:
            raw=name.read_bytes()
            digest=hashlib.sha256(raw).hexdigest()
            if digest!=checksum: raise ValueError("checksum mismatch")
            summary=audit(raw, dt.datetime.now().date())
            reports[key]={"sha256":digest,
                "bytes":len(raw),"matches":summary["accepted_historical"],
                "invalid":summary["invalid_rows"],
                "over15_research_frequency":summary["over15_frequency"],
                "point_in_time_verified":False}
        except (OSError, ValueError, KeyError) as error:
            errors.append({"key":key,"reason":str(error)})
    return reports,errors

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-dir",default="integration")
    parser.add_argument("--output",required=True)
    parser.add_argument("--group",choices=["ALL","E0"],default="ALL")
    parser.add_argument("--deadline-epoch",type=float,required=True)
    parser.add_argument("--heartbeat-seconds",type=int,default=60)
    parser.add_argument("--audit-seconds",type=int,default=300)
    opt=parser.parse_args()
    if not 10<=opt.heartbeat_seconds<=600 or opt.audit_seconds<opt.heartbeat_seconds:
        raise ValueError("invalid interval")
    root=(HERE/opt.output).resolve()
    source=(HERE/opt.source_dir).resolve()
    if HERE not in root.parents or HERE not in source.parents:
        raise ValueError("data directories must stay within project")
    root.mkdir(exist_ok=True)
    statefile=root/"checkpoint.json"
    if statefile.exists():
        s=json.loads(statefile.read_text(encoding="utf-8"))
    else:
        s={"run_id":"BCP-LOCAL-"+dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
           "started_utc":now(),"ticks":0,"audits":0,"last_audit_epoch":0,
           "network_requests":0,"status":"running","group":opt.group,
           "deadline_epoch":opt.deadline_epoch}
    if s.get("status")=="completed": return
    s["pid"]=os.getpid()
    event(root,"started",pid=s["pid"],group=opt.group,network_enabled=False)
    while time.time()<s["deadline_epoch"]:
        if (root/"STOP").exists():
            s["status"]="stopped_by_user"
            break
        if not s["last_audit_epoch"] or time.time()-s["last_audit_epoch"]>=opt.audit_seconds:
            reports,errors=inspect_cache(source,opt.group)
            s["audits"]+=1
            snapshot={"audit_utc":now(),"research_only":True,"network_requests":0,
                "source_root":str(source),"group":opt.group,"files":reports,"errors":errors}
            atomic(root/("snapshot_%04d.json"%s["audits"]),snapshot)
            atomic(root/"latest_audit.json",snapshot)
            s["last_audit_epoch"]=time.time()
            event(root,"local_audit",audit=s["audits"],source_count=len(reports),
                  problems=len(errors),network_requests=0)
        s["ticks"]+=1
        s["heartbeat_utc"]=now()
        atomic(statefile,s)
        event(root,"heartbeat",tick=s["ticks"])
        time.sleep(min(opt.heartbeat_seconds,max(0,s["deadline_epoch"]-time.time())))
    if s["status"]=="running": s["status"]="completed"
    s["finished_utc"]=now()
    atomic(statefile,s)
    atomic(root/"receipt.json",{"run_id":s["run_id"],"status":s["status"],
        "heartbeat_count":s["ticks"],"local_audit_count":s["audits"],
        "network_requests":0,"finished_utc":now()})
    event(root,"finished",status=s["status"])

if __name__=="__main__":
    main()
