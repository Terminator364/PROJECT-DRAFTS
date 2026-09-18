#!/usr/bin/env python3
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
failures = []
passes = []

def ok(name, cond, detail=""):
    (passes if cond else failures).append({"name": name, "detail": detail})

def read(name):
    p = ROOT / name
    ok(f"exists:{name}", p.is_file(), str(p))
    return p.read_text(encoding="utf-8") if p.is_file() else ""

def load_json(name):
    p = ROOT / name
    ok(f"exists:{name}", p.is_file(), str(p))
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        passes.append({"name": f"json:{name}", "detail": "valid"})
        return data
    except Exception as e:
        failures.append({"name": f"json:{name}", "detail": repr(e)})
        return {}

projects = load_json("projects.json")
adapter = load_json("AX150K_ADAPTER.json")
context = load_json("AX150K_CONTEXT.json")
harness = load_json("AX150K_HARNESS.json")

required = [
    "hub.ps1","launcher.ps1","bootstrap-pc.ps1","remote-runner.sh",
    "local-sign-apk.ps1","migrate-signing.ps1","migrate-durable-inputs.ps1",
    "setup-local-signing-tools.ps1","projects.json","AX150K_ADAPTER.json",
    "AX150K_CONTEXT.json","AX150K_HARNESS.json"
]
texts = {name: read(name) for name in required if name.endswith((".ps1",".sh",".json"))}

ok("registry-version-0.2", projects.get("version") == "0.2", str(projects.get("version")))
policy = projects.get("policy", {})
ok("hosted-actions-default-zero", policy.get("actions_hosted_default_minutes_per_day") == 0)
ok("codespaces-prebuilds-disabled", policy.get("codespaces_prebuilds") is False)
ok("local-signing-mode", policy.get("signing_mode") == "LOCAL_WINDOWS_DPAPI")
cap = policy.get("internal_monthly_core_hour_cap")
ok("internal-budget-positive-and-below-reference", isinstance(cap,(int,float)) and 0 < cap < policy.get("github_free_reference_core_hours",0), str(cap))

expected_projects = {"PhoneMouse","P2PCR95","ChatGPT-PC"}
actual_projects = set(projects.get("projects",{}))
ok("registry-project-set", actual_projects == expected_projects, repr(actual_projects))

for name, cfg in projects.get("projects",{}).items():
    ok(f"{name}:source-owned-recipe", cfg.get("recipe_path") == ".matrix-build/build.sh", str(cfg.get("recipe_path")))
    ok(f"{name}:branch-set", bool(cfg.get("default_branch")), str(cfg.get("default_branch")))
    ok(f"{name}:repo-set", bool(re.fullmatch(r"Terminator364/[A-Za-z0-9_.-]+", str(cfg.get("repo","")))), str(cfg.get("repo")))
    if name in {"PhoneMouse","P2PCR95"}:
        sign = cfg.get("signing")
        ok(f"{name}:signing-config-present", isinstance(sign,dict))
        if isinstance(sign,dict):
            ok(f"{name}:cert-sha256-shape", bool(re.fullmatch(r"[0-9a-f]{64}", str(sign.get("certificate_sha256","")))))

hub = texts.get("hub.ps1","")
for token in [
    "Local\\MatriceBuildHub.SingleBuild",
    "PREBUILD_DETECTED",
    "SOURCE_MISMATCH",
    "INTERNAL_BUDGET_GUARD",
    "gh codespace delete",
    "--target $Sha",
    "local-sign-apk.ps1",
]:
    ok(f"hub-invariant:{token}", token in hub)

ok("hub-no-actions-dispatch", "workflow run" not in hub.lower() and "actions/workflows" not in hub.lower())
ok("hub-no-signing-secret-cloud", "KEYSTORE_B64" not in hub and "gh secret set" not in hub)

local_sign = texts.get("local-sign-apk.ps1","")
for token in ["zipalign.exe","apksigner.bat","APP_ID_MISMATCH","CERT_MISMATCH","Windows DPAPI"]:
    if token == "Windows DPAPI":
        # DPAPI is owned by migrate-signing, not signer text.
        continue
    ok(f"local-sign:{token}", token in local_sign)

migrate = texts.get("migrate-signing.ps1","")
ok("migrate-uses-dpapi", "ProtectedData" in migrate and "DataProtectionScope]::CurrentUser" in migrate)
ok("migrate-no-codespaces-secret-upload", "secret set" not in migrate and "KEYSTORE_B64" not in migrate)
ok("migrate-disaster-recovery-flag", "DISASTER_RECOVERY_BACKUP" in migrate or "disaster_recovery_backup" in migrate)

runner = texts.get("remote-runner.sh","")
for token in ["git checkout --detach", "MATRIX_SOURCE_SHA", "timeout", ".matrix-build-output"]:
    ok(f"remote-runner:{token}", token in runner)

ok("ax-adapter-reality-gap", adapter.get("reality_gap",{}).get("generic_static_pass_cannot_certify_operational") is True)
ok("ax-harness-trusted", harness.get("trusted") is True)
src_status = {s.get("id"):s.get("status") for s in context.get("sources",[])}
ok("ax-real-pc-not-falsely-materialized", src_status.get("user_pc_runtime") == "inaccessible_until_field_run")
ok("ax-codespace-not-falsely-materialized", src_status.get("github_codespaces_runtime") == "inaccessible_until_field_run")

# Anti-Goodhart: certification cannot be a simple count.
gates = adapter.get("certification_gates", [])
ok("certification-is-multigate", isinstance(gates,list) and len(gates) >= 8)
for critical in ["LOCAL_BOOTSTRAP_PASS","CLOUD_SMOKE_PASS","LOCAL_SIGNATURE_PASS","UPDATE_OVER_EXISTING_APP_PASS","SECOND_INDEPENDENT_BUILD_PASS"]:
    ok(f"certification-gate:{critical}", critical in gates)

summary = {
    "schema":"buildhub-static-harness-v1",
    "status":"PASS" if not failures else "FAIL",
    "passes":len(passes),
    "failures":len(failures),
    "failed_checks":failures,
}
print(json.dumps(summary, indent=2))
sys.exit(0 if not failures else 1)
