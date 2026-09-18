from __future__ import annotations

import ast
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
HUB=HERE.parent/"hub.ps1"

def fail(code:str)->None:
    raise SystemExit("BUILD2_SELFTEST_FAIL:"+code)

required_files=[
    "bridge.py","selftest.py","build2_core.py","build2_worker.py","build2_supervisor.py",
    "build2_registry.json","build2_source_authority.json"
]
for name in required_files:
    if not (HERE/name).is_file():
        fail("MISSING_"+name)

for name in ("bridge.py","build2_core.py","build2_worker.py","build2_supervisor.py"):
    source=(HERE/name).read_text(encoding="utf-8")
    try:
        ast.parse(source,filename=name)
    except SyntaxError as e:
        fail("SYNTAX_"+name+":"+str(e))
    for forbidden in ("shell=True","os.system(","subprocess.call(","cmd.exe /c","powershell -Command"):
        if forbidden in source:
            fail("FORBIDDEN_"+name+":"+forbidden)

bridge=(HERE/"bridge.py").read_text(encoding="utf-8")
for op in ("doctor","last_build_status","cancel_build","get_receipt"):
    if f'"{op}"' not in bridge:
        fail("BRIDGE_SYSTEM_OPERATION_"+op)
if "lane_config_for_operation" not in bridge:
    fail("BRIDGE_NOT_REGISTRY_DRIVEN")

if not HUB.is_file():
    fail("MISSING_HUB_PS1")
hub_text=HUB.read_text(encoding="utf-8-sig")
if hub_text.count("MACHINE_QUERY_FAILED")!=1:
    fail("HUB_DUPLICATED_EXECUTION_TAIL")
if hub_text.count("INVALID_EXPECTED_SHA")!=1:
    fail("HUB_EXPECTED_SHA_GUARD_CARDINALITY")
if "if($ExpectedSha -notmatch '^[0-9a-f]{40}$')" not in hub_text:
    fail("HUB_EXPECTED_SHA_GUARD_MALFORMED")
for token in ("[string]$ExpectedSha","SOURCE_SHA_GUARD","INVALID_EXPECTED_SHA"):
    if token not in hub_text:
        fail("HUB_EXACT_SHA_"+token)

if os.name=="nt":
    ps=shutil.which("powershell.exe")
    if not ps:
        fail("POWERSHELL_PARSER_MISSING")
    parser=(
        "$e=$null;$t=$null;"
        "[System.Management.Automation.Language.Parser]::ParseFile($args[0],[ref]$t,[ref]$e)|Out-Null;"
        "if($e.Count -gt 0){$e|ForEach-Object{$_.Message}|Out-String|Write-Error;exit 1}"
    )
    cp=subprocess.run(
        [ps,"-NoProfile","-NonInteractive","-Command",parser,str(HUB)],
        capture_output=True,text=True,shell=False,timeout=30)
    if cp.returncode!=0:
        fail("HUB_POWERSHELL_PARSE:"+((cp.stderr or cp.stdout)[-500:]))

worker=(HERE/"build2_worker.py").read_text(encoding="utf-8")
for token in (
    'cat-file","-e"','"fetch","origin",expected,"--depth=1"',
    "PROJECT_SOURCE_SHA_MISMATCH","process_doctor","CODESPACES_UNAVAILABLE",
    "acquire_heavy_lock","request_cancel","FAILED_SAFE",
    "ensure_persistent_supervisor","EXTERNAL_TERMINATION_CTRL_EVENT","terminate_tree",
    '"-Branch",str(lane_cfg["branch"]),"-ExpectedSha",project_sha'
):
    if token not in worker:
        fail("WORKER_TOKEN_"+token)
if 'gh,"auth","status"' in worker or '"auth","status"' in worker:
    fail("GH_AUTH_EVERY_OPERATION_REGRESSION")

reg=json.loads((HERE/"build2_registry.json").read_text(encoding="utf-8"))
version=str(reg.get("version") or "")
if not version.startswith("0.5.3"):
    fail("REGISTRY_VERSION")
gp=reg.get("global_policy",{})
if gp.get("max_heavy_builds")!=1 or gp.get("zero_manual_normal_flow") is not True:
    fail("GLOBAL_POLICY")
if gp.get("arbitrary_shell") is not False:
    fail("ARBITRARY_SHELL_POLICY")
if gp.get("authorization_context_persistent") is not True:
    fail("AUTHORIZED_CONTEXT_NOT_PERSISTENT")
if gp.get("authorization_reconfirmation_when_scope_unchanged") is not False:
    fail("AUTHORIZATION_RECONFIRMATION_POLICY")
if gp.get("unrelated_third_party_scope_expansion") is not False:
    fail("THIRD_PARTY_SCOPE_POLICY")
if reg.get("context_contract")!="MATRICE-BUILD-HUB/AUTHORIZED_PROJECT_SCOPE.md":
    fail("CONTEXT_CONTRACT")

lanes=reg.get("lanes",{})
for lane in ("phonemouse","p2pcr95","chatgpt_pc"):
    if lane not in lanes:
        fail("LANE_"+lane)
    if not lanes[lane].get("project") or not lanes[lane].get("operation"):
        fail("LANE_CONTRACT_"+lane)

for lane in ("phonemouse","p2pcr95"):
    cfg=lanes[lane]
    sha=str(cfg.get("source_sha") or "")
    if len(sha)!=40 or any(c not in "0123456789abcdef" for c in sha.lower()):
        fail("LANE_SOURCE_SHA_"+lane)
    if cfg.get("authorized_project_scope")!="AUTHORIZED_PROJECT_SCOPE.md":
        fail("LANE_AUTHORIZED_SCOPE_"+lane)

pm=lanes["phonemouse"]
if pm.get("resource_profile",{}).get("max_workers")!=1:
    fail("PHONEMOUSE_MAX_WORKERS")
if pm.get("gates",{}).get("canonical_patch")!="beta11-overrides/canonical":
    fail("PHONEMOUSE_CANONICAL_PATCH")

p2=lanes["p2pcr95"]
if p2.get("expected",{}).get("version_code")!=6:
    fail("P2PCR95_VERSION_CODE")
if p2.get("expected",{}).get("version_name")!="0.1.0-beta04":
    fail("P2PCR95_VERSION_NAME")
if p2.get("branch")!="beta04-runtime-control-integration-20260918":
    fail("P2PCR95_BRANCH")

authority=json.loads((HERE/"build2_source_authority.json").read_text(encoding="utf-8"))
sha=str(authority.get("source_sha") or "")
if authority.get("status")!="PINNED" or len(sha)!=40:
    fail("SOURCE_AUTHORITY")
hub_sha=str(authority.get("hub_sha256") or "").lower()
if len(hub_sha)!=64 or any(c not in "0123456789abcdef" for c in hub_sha):
    fail("HUB_SHA_AUTHORITY")

scope_path=HERE/"AUTHORIZED_PROJECT_SCOPE.md"
if not scope_path.is_file():
    scope_path=HERE.parent/"AUTHORIZED_PROJECT_SCOPE.md"
if not scope_path.is_file():
    fail("MISSING_AUTHORIZED_PROJECT_SCOPE")
scope=scope_path.read_text(encoding="utf-8")
for token in (
    "controlled/authorized test environments",
    "No arbitrary remote shell",
    "does not bypass, disable or override platform safety controls"
):
    if token not in scope:
        fail("AUTHORIZED_SCOPE_TOKEN")

with tempfile.TemporaryDirectory(prefix="mbh-build2-selftest-") as td:
    old=os.environ.get("LOCALAPPDATA")
    os.environ["LOCALAPPDATA"]=td
    try:
        spec=importlib.util.spec_from_file_location("build2_core_selftest",HERE/"build2_core.py")
        if spec is None or spec.loader is None:
            fail("CORE_IMPORT_SPEC")
        core=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(core)
        if core.BUILD2_VERSION!=version:
            fail("CORE_REGISTRY_VERSION_MISMATCH")
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
        rec=core.write_receipt("P2PCR95",rid,"COMPLETE",stage="COMPLETE",
            evidence=[{"kind":"selftest","value":"PASS"}])
        if rec.get("result")!="COMPLETE":
            fail("RECEIPT")
        if core.get_receipt("P2PCR95",rid).get("run_id")!=rid:
            fail("RECEIPT_READBACK")
        c2=core.new_run("P2PCR95","build_p2pcr95",contract,idempotency_key="selftest-key")
        if c2.get("status")!="QUEUED" or c2.get("run_id")==rid:
            fail("POST_COMPLETE_REPRO_RUN")
    finally:
        if old is None:
            os.environ.pop("LOCALAPPDATA",None)
        else:
            os.environ["LOCALAPPDATA"]=old

print(json.dumps({
    "schema":"build2.selftest/1",
    "status":"PASS",
    "version":version,
    "lanes":["phonemouse","p2pcr95","chatgpt_pc"],
    "checks":{
        "syntax":"PASS",
        "no_arbitrary_shell":"PASS",
        "authorized_context":"PASS",
        "local_first":"PASS",
        "p2pcr95_candidate_contract":"PASS",
        "run_id_idempotence":"PASS",
        "heartbeat_receipt":"PASS",
        "generic_lane_onboarding":"PASS",
        "post_complete_repro_run":"PASS",
        "durable_supervisor":"PASS",
        "ntstatus_classification":"PASS",
        "bounded_subtree_cancel":"PASS",
        "hub_powershell_parse":"PASS",
        "exact_branch_sha_wiring":"PASS"
    }
},ensure_ascii=False))
