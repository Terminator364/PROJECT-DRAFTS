from __future__ import annotations
import argparse
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def build(mission_id:str,output:Path):
    if not mission_id or len(mission_id)>160: raise SystemExit("INVALID_MISSION_ID")
    mf=json.loads((HERE/"manifest.template.json").read_text(encoding="utf-8"))
    mf["activation_mission_id"]=mission_id
    payload_files=[HERE/"bridge.py",HERE/"selftest.py"]
    mf["files"]=[{"path":p.name,"sha256":sha256(p)} for p in payload_files]
    with tempfile.TemporaryDirectory(prefix="mbh-managed-package-") as td:
        stage=Path(td); (stage/"payload").mkdir()
        (stage/"manifest.json").write_text(json.dumps(mf,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        for p in payload_files: (stage/"payload"/p.name).write_bytes(p.read_bytes())
        output.parent.mkdir(parents=True,exist_ok=True)
        if output.exists(): output.unlink()
        with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            z.write(stage/"manifest.json","manifest.json")
            for p in payload_files: z.write(stage/"payload"/p.name,"payload/"+p.name)
    print(json.dumps({"schema":"mbh-managed-package-build-v2","status":"PASS","app_id":mf["app_id"],"mission_id":mission_id,"output":str(output),"package_sha256":sha256(output),"file_count":len(mf["files"])},ensure_ascii=False))

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--mission-id",required=True); ap.add_argument("--output",required=True,type=Path)
    args=ap.parse_args(); build(args.mission_id,args.output)
