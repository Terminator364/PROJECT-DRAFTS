#!/usr/bin/env python3
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
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
    "setup-local-signing-tools.ps1","export-disaster-recovery.ps1",
    "verify-disaster-recovery.ps1","projects.json","AX150K_ADAPTER.json",
    "AX150K_CONTEXT.json","AX150K_HARNESS.json",
    "adapters/phonemouse.sh","adapters/p2pcr95.sh","adapters/chatgpt-pc.sh",
]
texts = {name: read(name) for name in required}

browser_root = REPO_ROOT / "BROWSER4G"
browser_files = {
    "build": browser_root / "build.ps1",
    "toolchain": browser_root / "ensure-toolchain.ps1",
    "recipe": browser_root / ".matrix-build" / "build.ps1",
}
browser_text = {}
for key, path in browser_files.items():
    ok(f"exists:BROWSER4G:{key}", path.is_file(), str(path))
    browser_text[key] = path.read_text(encoding="utf-8") if path.is_file() else ""

ok("registry-version-0.3", projects.get("version") == "0.3", str(projects.get("version")))
policy = projects.get("policy", {})
ok("hosted-actions-default-zero", policy.get("actions_hosted_default_minutes_per_day") == 0)
ok("codespaces-prebuilds-disabled", policy.get("codespaces_prebuilds") is False)
ok("local-signing-mode", policy.get("signing_mode") == "LOCAL_WINDOWS_DPAPI")
cap = policy.get("internal_monthly_core_hour_cap")
ok(
    "internal-budget-positive-and-below-reference",
    isinstance(cap, (int, float)) and 0 < cap < policy.get("github_free_reference_core_hours", 0),
    str(cap),
)

expected_projects = {"PhoneMouse", "P2PCR95", "ChatGPT-PC", "BROWSER4G"}
actual_projects = set(projects.get("projects", {}))
ok("registry-project-set", actual_projects == expected_projects, repr(actual_projects))

for name, cfg in projects.get("projects", {}).items():
    expected_recipe = "BROWSER4G/.matrix-build/build.ps1" if name == "BROWSER4G" else ".matrix-build/build.sh"
    ok(f"{name}:source-owned-recipe", cfg.get("recipe_path") == expected_recipe, str(cfg.get("recipe_path")))
    ok(f"{name}:branch-set", bool(cfg.get("default_branch")), str(cfg.get("default_branch")))
    ok(f"{name}:repo-set", bool(re.fullmatch(r"Terminator364/[A-Za-z0-9_.-]+", str(cfg.get("repo", "")))), str(cfg.get("repo")))
    if name == "BROWSER4G":
        ok("BROWSER4G:builder-local-windows", cfg.get("builder_kind") == "LOCAL_WINDOWS", str(cfg.get("builder_kind")))
        ok("BROWSER4G:field-publish-gate", cfg.get("publish_gate") == "FIELD_PASS_REQUIRED", str(cfg.get("publish_gate")))
    if name in {"PhoneMouse", "P2PCR95"}:
        sign = cfg.get("signing")
        ok(f"{name}:signing-config-present", isinstance(sign, dict))
        if isinstance(sign, dict):
            ok(f"{name}:cert-sha256-shape", bool(re.fullmatch(r"[0-9a-f]{64}", str(sign.get("certificate_sha256", "")))))

hub = texts.get("hub.ps1", "")
for token in [
    "Local\\MatriceBuildHub.SingleBuild",
    "PREBUILD_DETECTED",
    "SOURCE_MISMATCH",
    "INTERNAL_BUDGET_GUARD",
    "gh codespace delete",
    "--target $Sha",
    "local-sign-apk.ps1",
    "RELEASE_DIGEST_MISMATCH",
    "RELEASE_ASSET_DIGESTS_PASS",
    "isImmutable",
    "AssertRecoveryMarker",
    "INTERNAL_BUDGET_RESERVATION",
    "CODESPACE_DELETE_FAILED",
    "InvokeLocalWindowsProject",
    "LOCAL_SOURCE_MISMATCH",
    "FIELD_GATE_BYPASS",
    "LOCAL_ARTIFACT_HASH_MISMATCH",
]:
    ok(f"hub-invariant:{token}", token in hub)

ok("hub-single-runtime-entry", hub.count('Need "gh" "GH_MISSING"') == 1, str(hub.count('Need "gh" "GH_MISSING"')))
ok("hub-single-release-verifier", hub.count("function VerifyReleaseAssets") == 1, str(hub.count("function VerifyReleaseAssets")))
ok("hub-single-recovery-verifier", hub.count("function AssertRecoveryMarker") == 1, str(hub.count("function AssertRecoveryMarker")))

ok("hub-no-actions-dispatch", "workflow run" not in hub.lower() and "actions/workflows" not in hub.lower())
ok("hub-no-signing-secret-cloud", "KEYSTORE_B64" not in hub and "gh secret set" not in hub)

for token in [
    "1.0.4191.47",
    "7.9.0",
    "992D70CAC5B06C38EFEC91806CABA64CDCC07E6D963A0959DBBBAF264D33B800",
    "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
    "https://api.nuget.org/v3/index.json",
    "/m:1",
]:
    ok(f"BROWSER4G-build:{token}", token in browser_text.get("build", ""))
for token in ["Microsoft.VisualStudio.2022.BuildTools", "Microsoft.VisualStudio.Workload.VCTools", "LOW_DISK_FOR_TOOLCHAIN"]:
    ok(f"BROWSER4G-toolchain:{token}", token in browser_text.get("toolchain", ""))
for token in ["mbh-result-v1", "FIELD_PASS_REQUIRED", "BROWSER4G-P0.exe"]:
    ok(f"BROWSER4G-recipe:{token}", token in browser_text.get("recipe", ""))

local_sign = texts.get("local-sign-apk.ps1", "")
for token in ["zipalign.exe", "apksigner.bat", "APP_ID_MISMATCH", "CERT_MISMATCH"]:
    ok(f"local-sign:{token}", token in local_sign)

migrate = texts.get("migrate-signing.ps1", "")
ok("migrate-uses-dpapi", "ProtectedData" in migrate and "DataProtectionScope]::CurrentUser" in migrate)
ok("migrate-no-codespaces-secret-upload", "secret set" not in migrate and "KEYSTORE_B64" not in migrate)
for token in ["CERT_MISMATCH", "CERT_EXPECTED_INVALID", "disaster_recovery_backup"]:
    ok(f"migrate:{token}", token in migrate)

export_recovery = texts.get("export-disaster-recovery.ps1", "")
ok("recovery-export-plaintext-finally-cleanup", 'if($plainBundle -and (Test-Path $plainBundle))' in export_recovery)

recovery = texts.get("verify-disaster-recovery.ps1", "")
for token in [
    "mbh-disaster-recovery-restore-test-v2",
    "RECOVERY_KEYSTORE_OPEN_FAILED",
    "RECOVERY_CERT_MISMATCH",
    "functional_restore_validation",
]:
    ok(f"recovery:{token}", token in recovery)

runner = texts.get("remote-runner.sh", "")
for token in ["git checkout --detach", "MATRIX_SOURCE_SHA", "timeout", ".matrix-build-output", 'bash -n "$SCRIPT"']:
    ok(f"remote-runner:{token}", token in runner)

setup = texts.get("setup-local-signing-tools.ps1", "")
ok("sdkmanager-bounded", "SDKMANAGER_TIMEOUT" in setup and "WaitForExit($TimeoutSeconds*1000)" in setup)

launcher = texts.get("launcher.ps1", "")
ok("launcher-fails-stale", "HUB_UPDATE_FAILED" in launcher and "continuing with installed version" not in launcher)

bootstrap = texts.get("bootstrap-pc.ps1", "")
ok("bootstrap-refresh-fail-closed", "HUB_FETCH_FAILED" in bootstrap and "HUB_RESET_FAILED" in bootstrap)

attrs = REPO_ROOT / ".gitattributes"
ok("gitattributes-present", attrs.is_file(), str(attrs))
if attrs.is_file():
    attr_text = attrs.read_text(encoding="utf-8")
    ok("shell-eol-lf", bool(re.search(r"(?m)^\*\.sh\s+text\s+eol=lf\s*$", attr_text)))

ok("ax-adapter-reality-gap", adapter.get("reality_gap", {}).get("generic_static_pass_cannot_certify_operational") is True)
ok("ax-harness-trusted", harness.get("trusted") is True)
src_status = {s.get("id"): s.get("status") for s in context.get("sources", [])}
ok("ax-real-pc-not-falsely-materialized", src_status.get("user_pc_runtime") == "inaccessible_until_field_run")
ok("ax-codespace-not-falsely-materialized", src_status.get("github_codespaces_runtime") == "inaccessible_until_field_run")
for remote_id in ["github_phonemouse_beta11", "github_p2pcr95_beta03", "github_chatgpt_pc_active"]:
    ok(f"ax-remote-source-referenced:{remote_id}", src_status.get(remote_id) == "referenced", str(src_status.get(remote_id)))

gates = adapter.get("certification_gates", [])
ok("certification-is-multigate", isinstance(gates, list) and len(gates) >= 12)
for critical in [
    "STATIC_AUDIT_PASS",
    "ZERO_AUTO_ACTIONS_ACTIVE_BRANCHES",
    "LOCAL_BOOTSTRAP_PASS",
    "LOCAL_SIGNING_VAULT_PASS",
    "DISASTER_RECOVERY_EXPORT_PASS",
    "DISASTER_RECOVERY_RESTORE_TEST_PASS",
    "CLOUD_SMOKE_PASS",
    "ANDROID_CLOUD_BUILD_PASS",
    "LOCAL_SIGNATURE_PASS",
    "RELEASE_ASSET_DIGESTS_PASS",
    "UPDATE_OVER_EXISTING_APP_PASS",
    "SECOND_INDEPENDENT_BUILD_PASS",
]:
    ok(f"certification-gate:{critical}", critical in gates)

# Anti-Goodhart: the harness reports checks, not invented AX150K target counts.
serialized = "\n".join(texts.values())
for inflated in ["150000", "100000", "15000000", "70000", "50000"]:
    ok(f"anti-goodhart:no-claimed-target-{inflated}", inflated not in serialized)

summary = {
    "schema": "buildhub-static-harness-v2",
    "status": "PASS" if not failures else "FAIL",
    "passes": len(passes),
    "failures": len(failures),
    "failed_checks": failures,
}
print(json.dumps(summary, indent=2))
sys.exit(0 if not failures else 1)
