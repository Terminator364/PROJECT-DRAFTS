from __future__ import annotations
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
FIXED_DT=(2026,9,18,0,0,0)

def sha256_bytes(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def sha256(path:Path)->str:
    return sha256_bytes(path.read_bytes())

def stable_json(obj:dict)->bytes:
    return (json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode("utf-8")

def add_bytes(z:zipfile.ZipFile,name:str,data:bytes)->None:
    info=zipfile.ZipInfo(name,FIXED_DT)
    info.compress_type=zipfile.ZIP_DEFLATED
    info.external_attr=0o644<<16
    z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)

def build(mission_id:str,source_sha:str,output:Path):
    if not mission_id or len(mission_id)>160:
        raise SystemExit("INVALID_MISSION_ID")
    source_sha=source_sha.strip().lower()
    if len(source_sha)!=40 or any(c not in "0123456789abcdef" for c in source_sha):
        raise SystemExit("INVALID_SOURCE_SHA")
    mf=json.loads((HERE/"manifest.template.json").read_text(encoding="utf-8"))
    reg=json.loads((HERE/"build2_registry.json").read_text(encoding="utf-8"))
    mf["activation_mission_id"]=mission_id
    mf["build2_source_sha"]=source_sha
    operations=mf.setdefault("operations",{})
    ui=mf.setdefault("ui_contract",{}).setdefault("buttons",[])
    known_buttons={str(x.get("operation")) for x in ui if isinstance(x,dict)}
    for lane_id,cfg in sorted(reg.get("lanes",{}).items()):
        op=str(cfg.get("operation") or "")
        project=str(cfg.get("project") or "")
        if not op or not project:
            raise SystemExit("INVALID_LANE_CONTRACT:"+lane_id)
        operations[op]=["{python}","{app_root}/bridge.py",op]
        if op not in known_buttons:
            ui.append({"id":lane_id,"label":"Build "+project,"operation":op})
            known_buttons.add(op)
    hub_bytes=(HERE.parent/"hub.ps1").read_bytes()
    hub_text=hub_bytes.decode("utf-8-sig")
    if hub_text.count("function VerifyReleaseAssets")!=1 or hub_text.count("BUILD_HUB_DOCTOR_PASS")!=1 or hub_text.count("param(")!=1 or hub_text.count("finally{")>2:
        raise SystemExit("HUB_ENGINE_STRUCTURE_INVALID")
    # Comments may document why this probe is forbidden; reject executable code only.
    hub_code="\n".join(line for line in hub_text.splitlines() if not line.lstrip().startswith("#"))
    if "gh auth status" in hub_code:
        raise SystemExit("HUB_ENGINE_UNBOUNDED_GH_AUTH")
    source_authority={
        "schema":"build2.source_authority/1",
        "status":"PINNED",
        "repo":"Terminator364/PROJECT-DRAFTS",
        "branch":"buildhub-v0.5-unified-lanes-20260918",
        "source_sha":source_sha,
        "promotion_mode":"TRANSACTIONAL_EXACT_SHA",
        "hub_sha256":sha256_bytes(hub_bytes)
    }
    payload:dict[str,bytes]={}
    for name in ("bridge.py","selftest.py","build2_core.py","build2_worker.py","build2_supervisor.py","build2_registry.json"):
        payload[name]=(HERE/name).read_bytes()
    payload["build2_source_authority.json"]=stable_json(source_authority)
    mf["files"]=[{"path":name,"sha256":sha256_bytes(data)} for name,data in sorted(payload.items())]
    manifest=stable_json(mf)
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output,"w") as z:
        add_bytes(z,"manifest.json",manifest)
        for name,data in sorted(payload.items()):
            add_bytes(z,"payload/"+name,data)
    print(json.dumps({
        "schema":"mbh-managed-package-build-v3",
        "status":"PASS","app_id":mf["app_id"],"mission_id":mission_id,
        "source_sha":source_sha,"output":str(output),
        "package_sha256":sha256(output),"file_count":len(payload),
        "deterministic_zip":True
    },ensure_ascii=False))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--mission-id",required=True)
    ap.add_argument("--source-sha",required=True)
    ap.add_argument("--output",required=True,type=Path)
    args=ap.parse_args()
    build(args.mission_id,args.source_sha,args.output)
