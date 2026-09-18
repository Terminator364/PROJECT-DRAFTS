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

def stable_json(obj)->bytes:
    return (json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode("utf-8")

def add_bytes(z:zipfile.ZipFile,name:str,data:bytes)->None:
    i=zipfile.ZipInfo(name,FIXED_DT)
    i.compress_type=zipfile.ZIP_DEFLATED
    i.external_attr=0o644<<16
    z.writestr(i,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)

def build(sequence:int, source_sha:str, output:Path):
    if sequence<1:
        raise SystemExit("INVALID_SEQUENCE")
    source_sha=source_sha.strip().lower()
    if len(source_sha)!=40 or any(c not in "0123456789abcdef" for c in source_sha):
        raise SystemExit("INVALID_SOURCE_SHA")
    template=json.loads((HERE/"manifest.template.json").read_text(encoding="utf-8"))
    reg=json.loads((HERE/"build2_registry.json").read_text(encoding="utf-8"))

    operations={
        "doctor":["{python}","{app_root}/bridge.py","doctor"],
        "last_build_status":["{python}","{app_root}/bridge.py","last_build_status"],
        "cancel_build":["{python}","{app_root}/bridge.py","cancel_build"],
        "get_receipt":["{python}","{app_root}/bridge.py","get_receipt"],
    }
    buttons=[
        {"id":"doctor","label":"Doctor","operation":"doctor"},
        {"id":"status","label":"État","operation":"last_build_status"},
        {"id":"cancel","label":"Annuler","operation":"cancel_build"},
        {"id":"receipt","label":"Reçu","operation":"get_receipt"},
    ]
    for lane_id,cfg in sorted(reg.get("lanes",{}).items()):
        op=str(cfg.get("operation") or "")
        project=str(cfg.get("project") or "")
        if not op or not project:
            raise SystemExit("INVALID_LANE_CONTRACT:"+lane_id)
        operations[op]=["{python}","{app_root}/bridge.py",op]
        buttons.append({"id":lane_id,"label":"Build "+project,"operation":op})

    hub_bytes=(HERE.parent/"hub.ps1").read_bytes()
    hub_text=hub_bytes.decode("utf-8-sig")
    if hub_text.count("function VerifyReleaseAssets")!=1 or hub_text.count("BUILD_HUB_DOCTOR_PASS")!=1 or hub_text.count("param(")!=1 or hub_text.count("finally{")>2:
        raise SystemExit("HUB_ENGINE_STRUCTURE_INVALID")
    # Comments may document why this probe is forbidden; reject executable code only.
    hub_code="\n".join(line for line in hub_text.splitlines() if not line.lstrip().startswith("#"))
    if "gh auth status" in hub_code:
        raise SystemExit("HUB_ENGINE_UNBOUNDED_GH_AUTH")
    authority={
        "schema":"build2.source_authority/1",
        "status":"PINNED",
        "repo":"Terminator364/PROJECT-DRAFTS",
        "branch":"buildhub-v0.5-unified-lanes-20260918",
        "source_sha":source_sha,
        "promotion_mode":"TRANSACTIONAL_EXACT_SHA",
        "hub_sha256":sha256_bytes(hub_bytes)
    }
    payload={}
    for name in ("bridge.py","selftest.py","build2_core.py","build2_worker.py","build2_registry.json"):
        payload[name]=(HERE/name).read_bytes()
    payload["build2_source_authority.json"]=stable_json(authority)

    manifest={
        "schema":1,
        "package_type":"managed_app_update",
        "target_app":"matrice-build-hub",
        "sequence":sequence,
        "update_id":f"mbh-build2-v050-unified-lanes-seq{sequence}",
        "version":"0.5.0-unified-lanes",
        "build2_source_sha":source_sha,
        "files":[{"path":n,"sha256":sha256_bytes(d)} for n,d in sorted(payload.items())],
        "manifest_patch":{
            "display_name":"MATRICE BUILD HUB — BUILD 2",
            "operations":operations,
            "ui_contract":{"mode":"NATIVE_ON_DEMAND","buttons":buttons},
            "resource_profile":{
                "class":"INTERACTIVE_ON_DEMAND",
                "memory_limit_mb":192,
                "background_qos":"ECO",
                "battery_policy":"DEFER_WHEN_LOW"
            },
            "log_paths":["logs/app.log"]
        }
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output,"w") as z:
        add_bytes(z,"manifest.json",stable_json(manifest))
        for name,data in sorted(payload.items()):
            add_bytes(z,"payload/"+name,data)
    print(json.dumps({
        "schema":"build2.update_package/1","status":"PASS",
        "target_app":"matrice-build-hub","sequence":sequence,
        "source_sha":source_sha,"package_sha256":sha256(output),
        "output":str(output),"deterministic_zip":True,
        "operation_count":len(operations),"lane_count":len(reg.get("lanes",{}))
    },ensure_ascii=False))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--sequence",required=True,type=int)
    ap.add_argument("--source-sha",required=True)
    ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args()
    build(a.sequence,a.source_sha,a.output)
