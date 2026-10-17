#!/usr/bin/env python3
"""Experimental multi-league archive collector. Never used to calculate MATRICE IC."""
import argparse, csv, datetime as dt, hashlib, io, json, os, pathlib, time
import urllib.request

BASE = pathlib.Path(__file__).resolve().parent
LEAGUES = {"E0":"England","D1":"Germany","SP1":"Spain","I1":"Italy","F1":"France"}
SEASONS = ("2526","2627")
NEEDED = {"Date","HomeTeam","AwayTeam","FTHG","FTAG","FTR"}

def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

def save(path, data):
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(data,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    os.replace(tmp,path)

def date_of(s):
    for fmt in ("%d/%m/%Y","%d/%m/%y"):
        try: return dt.datetime.strptime(s.strip(),fmt).date()
        except ValueError: continue
    raise ValueError("invalid date")

def audit(raw, cutoff):
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig",errors="replace")))
    fields=set(reader.fieldnames or [])
    if not NEEDED <= fields: raise ValueError("missing required CSV columns")
    accepted=0; rejected=0; goals=0; over=0; seen=set()
    for r in reader:
        try:
            day=date_of(r["Date"])
            if day>=cutoff: continue
            home=r["HomeTeam"].strip(); away=r["AwayTeam"].strip()
            h=int(r["FTHG"]); a=int(r["FTAG"])
            if not home or not away or home==away or min(h,a)<0: raise ValueError()
            if r["FTR"].strip()!=("H" if h>a else "A" if a>h else "D"): raise ValueError()
            key=(day.isoformat(),home,away)
            if key in seen: raise ValueError()
            seen.add(key)
            accepted+=1; goals+=h+a; over+=int(h+a>=2)
        except (ValueError,TypeError,KeyError,AttributeError): rejected+=1
    return {"accepted_historical":accepted,"invalid_rows":rejected,
        "columns":sorted(fields),"over15_frequency":round(over/accepted,6) if accepted else None,
        "mean_goals":round(goals/accepted,6) if accepted else None,
        "cutoff_exclusive":cutoff.isoformat(),"pit_certified":False}

def fetch(url):
    raise RuntimeError("External CSV polling disabled to comply with Football-Data fair data usage policy; run local_audit.py against cached archives instead.")

def coverage(registry,items):
    report=[]
    for f in registry["families"]:
        candidates=set(f.get("candidate_fields",[]))
        columns=[set(x["audit"]["columns"]) for x in items.values() if x["status"]=="validated"]
        report.append({"id":f["id"],"coverage_mode":f["coverage_mode"],
            "candidate_fields":sorted(candidates),
            "observed_fields":sorted(set.union(*columns)&candidates) if columns else [],
            "ic_effect":"DISABLED","research_status":"OBSERVATION_ONLY"})
    return {"total_families":len(report),"families":report,
        "warning":"Observed source columns do not prove full family coverage or PIT evidence"}

def cycle(root,state,registry):
    updated=0
    for code in LEAGUES:
        for season in SEASONS:
            key=season+"_"+code
            url="https://www.football-data.co.uk/mmz4281/"+season+"/"+code+".csv"
            try:
                raw=fetch(url); fields=audit(raw,dt.datetime.now().date())
                sha=hashlib.sha256(raw).hexdigest()
                target=root/"raw"/(sha+".csv")
                if not target.exists(): target.write_bytes(raw)
                previous=state["sources"].get(key,{})
                if previous.get("sha256")!=sha: updated+=1
                state["sources"][key]={"status":"validated","url":url,"sha256":sha,
                    "bytes":len(raw),"collected_at_utc":utc(),"audit":fields,
                    "evidence_type":"RESEARCH_ONLY_HISTORICAL_AVAILABILITY_UNVERIFIED"}
            except Exception as e:
                state["sources"][key]={"status":"error","url":url,
                    "error":type(e).__name__+": "+str(e),"utc":utc()}
            save(root/"checkpoint.json",state)
    valid=[s for s in state["sources"].values() if s["status"]=="validated"]
    save(root/"manifest.json",{"run_id":state["run_id"],"collected_utc":utc(),
        "validated_sources":len(valid),"total_historical_matches":sum(
        x["audit"]["accepted_historical"] for x in valid),
        "changed_sources":updated,"sources":state["sources"],
        "contract":"RESEARCH_ONLY / no certified historical point-in-time"})
    save(root/"coverage_62.json",coverage(registry,state["sources"]))
    state["last_poll_epoch"]=time.time()
    save(root/"checkpoint.json",state)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--once",action="store_true")
    p.add_argument("--duration",type=int,default=3600)
    p.add_argument("--interval",type=int,default=60)
    p.add_argument("--refresh",type=int,default=1200)
    p.add_argument("--output",default="runtime")
    args=p.parse_args()
    if not 5<=args.duration<=7200 or not 2<=args.interval<=600 or not 5<=args.refresh<=3600:
        raise ValueError("invalid timing")
    root=(BASE/args.output).resolve()
    if BASE not in root.parents: raise ValueError("output must be below project")
    (root/"raw").mkdir(parents=True,exist_ok=True)
    registry=json.loads((BASE/"matrice_62_registry.json").read_text(encoding="utf-8"))
    assert len(registry["families"])==62 and len({x["id"] for x in registry["families"]})==62
    checkpoint=root/"checkpoint.json"
    if checkpoint.exists():
        state=json.loads(checkpoint.read_text(encoding="utf-8"))
        if state["status"]=="completed": return
    else:
        t=time.time()
        state={"run_id":"BCP-V2-"+dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
            "started_utc":utc(),"started_epoch":t,"deadline_epoch":t+args.duration,
            "cycle":0,"last_poll_epoch":0,"status":"running","sources":{}}
    state["worker_pid"]=os.getpid()
    while True:
        if (root/"STOP").exists(): state["status"]="stopped"; break
        if not args.once and time.time()>=state["deadline_epoch"]:
            state["status"]="completed"; break
        state["cycle"]+=1
        if not state["last_poll_epoch"] or time.time()-state["last_poll_epoch"]>=args.refresh:
            cycle(root,state,registry)
        state["heartbeat_utc"]=utc(); save(checkpoint,state)
        with (root/"events.jsonl").open("a",encoding="utf-8") as f:
            f.write(json.dumps({"utc":utc(),"event":"heartbeat","cycle":state["cycle"],
                "validated":sum(x["status"]=="validated" for x in state["sources"].values())})+"\n")
        if args.once: state["status"]="completed"; break
        time.sleep(min(args.interval,max(0,state["deadline_epoch"]-time.time())))
    state["finished_utc"]=utc(); save(checkpoint,state)
    save(root/"receipt.json",{"run_id":state["run_id"],"status":state["status"],
        "cycles":state["cycle"],"finished_utc":utc(),"research_only":True})

if __name__=="__main__":
    main()
