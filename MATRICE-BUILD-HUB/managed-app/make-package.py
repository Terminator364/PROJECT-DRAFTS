from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
HUB=HERE.parent
EXCLUDED_TOP={"managed-app"}
EXCLUDED_NAMES={"__pycache__",".git",".matrix-build-output"}

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def include_hub_file(path:Path)->bool:
    rel=path.relative_to(HUB)
    if not rel.parts: return False
    if rel.parts[0] in EXCLUDED_TOP: return False
    if any(part in EXCLUDED_NAMES for part in rel.parts): return False
    if path.name.endswith(".tmp") or path.name.endswith(".log"): return False
    return path.is_file()

def build(mission_id:str,output:Path):
    if not mission_id or len(mission_id)>160:
        raise SystemExit("INVALID_MISSION_ID")
    template=json.loads((HERE/"manifest.template.json").read_text(encoding="utf-8"))
    template["activation_mission_id"]=mission_id
    with tempfile.TemporaryDirectory(prefix="mbh-managed-package-") as td:
        stage=Path(td)
        payload=stage/"payload"
        payload.mkdir(parents=True)
        shutil.copy2(HERE/"bridge.py",payload/"bridge.py")
        shutil.copy2(HERE/"selftest.py",payload/"selftest.py")
        hubdst=payload/"hub"
        for src in sorted(HUB.rglob("*")):
            if not include_hub_file(src):
                continue
            rel=src.relative_to(HUB)
            dst=hubdst/rel
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(src,dst)
        files=[]
        for p in sorted(payload.rglob("*")):
            if p.is_file():
                files.append({"path":p.relative_to(payload).as_posix(),"sha256":sha256(p)})
        template["files"]=files
        (stage/"manifest.json").write_text(json.dumps(template,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        output.parent.mkdir(parents=True,exist_ok=True)
        if output.exists(): output.unlink()
        with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            z.write(stage/"manifest.json","manifest.json")
            for p in sorted(payload.rglob("*")):
                if p.is_file():
                    z.write(p,(Path("payload")/p.relative_to(payload)).as_posix())
    print(json.dumps({
        "schema":"mbh-managed-package-build-v1",
        "status":"PASS",
        "app_id":template["app_id"],
        "mission_id":mission_id,
        "output":str(output),
        "package_sha256":sha256(output),
        "file_count":len(template["files"])
    },ensure_ascii=False))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--mission-id",required=True)
    ap.add_argument("--output",required=True,type=Path)
    args=ap.parse_args()
    build(args.mission_id,args.output)
