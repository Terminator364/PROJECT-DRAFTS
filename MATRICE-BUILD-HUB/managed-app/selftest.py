from __future__ import annotations

import ast
import importlib.util
import json
import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent

def fail(code:str)->None:
    raise SystemExit("BUILD2_SELFTEST_FAIL:"+code)

required_files=[
    "bridge.py","build2_core.py","build2_worker.py",
    "build2_registry.json","build2_source_authority.json"
]
for name in required_files:
    if not (HERE/name).is_file():
        fail("MISSING_"+name)

for name in ("bridge.py","build2_core.py","build2_worker.py"):
    text=(HERE/name).read_text(encoding="utf-8")
    try:
        ast.parse(text,filename=name)
    except SyntaxError as e:
        fail("SYNTAX_"+name+":"+str(e))
    for forbidden in ("shell=True","os.system(","subprocess.call(","cmd.exe /c","powershell -Command"):
        if forbidden in text:
            fail("FORBIDDEN_"+name+":"+forbidden)

hub=HERE.parent/"hub.ps1"
if not hub.is_file():
    fail("MISSING_hub.ps1")
hub_text=hub.read_text(encoding="utf-8-sig",errors="strict")
if hub_text.count("function VerifyReleaseAssets")!=1:
    fail("HUB_VERIFY_RELEASE_DUPLICATED")
if hub_text.count("BUILD_HUB_DOCTOR_PASS")!=1:
    fail("HUB_DOCTOR_DUPLICATED")
if hub_text.count("param(")!=1:
    fail("HUB_PARAM_DUPLICATED")
if hub_text.count("finally{")>2:
    fail("HUB_FINALLY_STRUCTURE")
if "gh auth status" in hub_text:
    fail("HUB_UNBOUNDED_GH_AUTH_PREFLIGHT")
if os.name=="nt":
    ps=shutil.which("powershell.exe")
    if not ps:
        fail("POWERSHELL_MISSING_FOR_PARSE")
    parse_cmd=(
        "$e=$null;$t=$null;"
        "[System.Management.Automation.Language.Parser]::ParseFile('"
        +str(hub).replace("'","''")
        +"',[ref]$t,[ref]$e)|Out-Null;"
        "if($e.Count -gt 0){$e|ForEach-Object{$_.ToString()};exit 1}"
    )
    cp=subprocess.run([ps,"-NoProfile","-Command",parse_cmd],capture_output=True,text=True,shell=False,timeout=30)
    if cp.returncode!=0:
        fail("HUB_POWERSHELL_PARSE:"+((cp.stdout or "")+(cp.stderr or ""))[-500:])

bridge=(HERE/"bridge.py").read_text(encoding="utf-8")
for op in ("doctor","last_build_status","cancel_build","get_receipt"):
    if f'"{op}"' not in bridge:
        fail("BRIDGE_SYSTEM_OPERATION_"+op)
if "lane_config_for_operation" not in bridge:
    fail("BRIDGE_NOT_REGISTRY_DRIVEN")

worker=(HERE/"build2_worker.py").read_text(encoding="utf-8")
for token in (
    'cat-file","-e"', '"fetch","origin",expected,"--depth=1"',
    'PROJECT_SOURCE_SHA_MISMATCH','process_doctor','CODESPACES_UNAVAILABLE',
    'acquire_heavy_lock','request_cancel','FAILED_SAFE'
):
    if token not in worker:
        fail("WORKER_TOKEN_"+token)
if 'gh,"auth","status"' in worker or '"auth","status"' in worker:
    fail("GH_AUTH_EVERY_OPERATION_REGRESSION")

reg=json.loads((HERE/"build2_registry.json").read_text(encoding="utf-8"))
if reg.get("version")!="0.5.0-unified-lanes":
    fail("REGISTRY_VERSION")
gp=reg.get("global_policy",{})
if gp.get("max_heavy_builds")!=1 or gp.get("zero_manual_normal_flow") is not True:
    fail("GLOBAL_POLICY")
lanes=reg.get("lanes",{})
for lane in ("phonemouse","p2pcr95","chatgpt_pc"):
    if lane not in lanes:
        fail("LANE_"+lane)
    if not lanes[lane].get("project") or not lanes[lane].get("operation"):
        fail("LANE_CONTRACT_"+lane)
pm=lanes["phonemouse"]
if pm.get("resource_profile",{}).get("max_workers")!=1:
    fail("PHONEMOUSE_MAX_WORKERS")
if pm.get("gates",{}).get("canonical_patch")!="beta11-overrides/canonical":
    fail("PHONEMOUSE_CANONICAL_PATCH")
p2=lanes["p2pcr95"]
if p2.get("source_sha")!="c673f2a9f36477c35c65e9d87dec04590ef9551c":
    fail("P2PCR95_SHA")
if p2.get("expected",{}).get("version_code")!=5:
    fail("P2PCR95_VERSION_CODE")

authority=json.loads((HERE/"build2_source_authority.json").read_text(encoding="utf-8"))
sha=authority.get("source_sha","")
if authority.get("status")!="PINNED" or len(sha)!=40:
    fail("SOURCE_AUTHORITY")

# Functional state-machine smoke in an isolated LOCALAPPDATA.
with tempfile.TemporaryDirectory(prefix="mbh-build2-selftest-") as td:
    old=os.environ.get("LOCALAPPDATA")
    os.environ["LOCALAPPDATA"]=td
    spec=importlib.util.spec_from_file_location("build2_core_selftest",HERE/"build2_core.py")
    if spec is None or spec.loader is None:
        fail("CORE_IMPORT_SPEC")
    core=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    if core.lane_name("Fresh App 01")!="fresh_app_01":
        fail("GENERIC_LANE_NAMING")
    contract={"repo":"example/test","branch":"main","source_sha":"0"*40}
    a=core.new_run("P2PCR95","build_p2pcr95",contract,idempotency_key="selftest-key")
    if a.get("status")!="QUEUED":
        fail("NEW_RUN")
    b=core.new_run("P2PCR95","build_p2pcr95",contract,idempotency_key="selftest-key")
    if b.get("status")!="IDEMPOTENT_REUSE" or b.get("run_id")!=a.get("run_id"):
        fail("IDEMPOTENCE")
    rid=a["run_id"]
    hb=core.heartbeat("P2PCR95",rid,"PREFLIGHT","RUNNING",detail="selftest",progress_pct=10)
    if hb.get("run_id")!=rid or hb.get("stage")!="PREFLIGHT":
        fail("HEARTBEAT")
    rec=core.write_receipt("P2PCR95",rid,"COMPLETE",stage="COMPLETE",evidence=[{"kind":"selftest","value":"PASS"}])
    if rec.get("result")!="COMPLETE":
        fail("RECEIPT")
    got=core.get_receipt("P2PCR95",rid)
    if got.get("run_id")!=rid:
        fail("RECEIPT_READBACK")
    c2=core.new_run("P2PCR95","build_p2pcr95",contract,idempotency_key="selftest-key")
    if c2.get("status")!="QUEUED" or c2.get("run_id")==rid:
        fail("POST_COMPLETE_REPRO_RUN")
    if old is None:
        os.environ.pop("LOCALAPPDATA",None)
    else:
        os.environ["LOCALAPPDATA"]=old

print(json.dumps({
    "schema":"build2.selftest/1",
    "status":"PASS",
    "version":"0.5.0-unified-lanes",
    "lanes":["phonemouse","p2pcr95","chatgpt_pc"],
    "checks":{
        "syntax":"PASS","no_arbitrary_shell":"PASS","local_first":"PASS",
        "p2pcr95_exact_candidate":"PASS","phonemouse_low_ram_contract":"PASS",
        "run_id_idempotence":"PASS","heartbeat_receipt":"PASS","generic_lane_onboarding":"PASS","post_complete_repro_run":"PASS"
    }
},ensure_ascii=False))
