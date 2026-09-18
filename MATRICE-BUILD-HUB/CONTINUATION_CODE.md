# MATRICE BUILD HUB — CONTINUATION CODE

Exact continuation code:

`BUILDHUB AX15GO CONTINUE`

## Meaning
When this code is entered in a new ChatGPT conversation:

1. Recover the latest state of MATRICE BUILD HUB from:
   - Terminator364/PROJECT-DRAFTS
   - branch: buildhub-v0.2-hardening-20260918
   - folder: MATRICE-BUILD-HUB
2. Treat AX150K V1.3 Operational (2026-09-17) as the frozen stable AX15GO baseline for this hardening batch.
3. Preserve the supplemental V1.4 DEV guards already integrated:
   - anti-Goodhart / TARGET_COUNT_NOT_SUFFICIENT
   - false-novelty / salami-slicing detection
   - independent oracles
   - bounded causal-neighborhood interactions
   - reality-gap contract
   - version-specific evidence and stale-proof invalidation
4. Do NOT restart the design from scratch.
5. Resume from the current certification state below.

## Current BuildHub state
- V0.2 hardening branch exists and is the active source of truth.
- All active workflows are manual-only:
  - PhoneMouse BETA11: 14/14 manual-only
  - P2PCR95 BETA03: 6/6 manual-only
  - ChatGPT-PC active branch: 3/3 manual-only
  - Total checked: 23 workflows, zero push/PR/schedule triggers.
- Android build architecture:
  - cloud Codespaces compiles unsigned APK;
  - Windows PC performs zipalign + apksigner locally;
  - signing keys never enter Codespaces.
- Signing identities:
  - migration script rebuilt cleanly;
  - canonical certificate fingerprint validation required before DPAPI vaulting;
  - Windows DPAPI CurrentUser vault;
  - portable encrypted disaster-recovery export + independent restore test required.
- Hub protections:
  - exact source SHA binding;
  - source-owned .matrix-build/build.sh recipes;
  - source recipe syntax checked in smoke;
  - no prebuilds;
  - Codespace idle timeout 10m;
  - Codespace retention period 1h;
  - stop/delete cleanup;
  - local quota ledger and internal cap;
  - no blind full-build retries;
  - bounded download retries only;
  - unsigned APK removed after successful local signing;
  - existing prerelease must match commit + prerelease mode + expected assets;
  - signed APK publication blocked until disaster-recovery restore test passes.
- AX15GO manifests:
  - AX150K_CONTEXT.json
  - AX150K_ADAPTER.json
  - AX150K_HARNESS.json
  - self-test.ps1
  - .ax15go/buildhub_static_harness.py

## Important defects already found and fixed
- bootstrap literal \\r\\n corruption;
- sdkmanager redirected-output deadlock risk;
- missing cross-process JAVA_HOME persistence;
- migrate-signing.ps1 corruption from incremental patches (fully replaced);
- weak keystore validation (now certificate-checked);
- branch-level automatic Actions triggers;
- release reuse without asset completeness verification;
- orphan Codespace retention risk;
- unsigned APK ambiguity in final outputs.

## Certification state
Current state:
`DESIGN_READY + HARDENED_STATIC_ARCHITECTURE`

NOT yet:
`OPERATIONAL`

Field gates still required:
1. STATIC_SELF_TEST_PASS on the real Windows PC.
2. LOCAL_BOOTSTRAP_PASS.
3. LOCAL_SIGNING_VAULT_PASS for PhoneMouse and P2PCR95.
4. DISASTER_RECOVERY_EXPORT_PASS.
5. DISASTER_RECOVERY_RESTORE_TEST_PASS.
6. CLOUD_SMOKE_PASS using Codespaces without GitHub Actions.
7. Real PhoneMouse BETA11 cloud compilation.
8. Local Windows signing with canonical certificate.
9. Install/update BETA11 over the existing PhoneMouse beta WITHOUT uninstalling.
10. Repeat with a second independent build.
11. Then validate P2PCR95 BETA03.
12. Promote V0.2 hardening branch to main only after the required gates pass.

## First action on recovery
Re-audit the current branch head for unexpected drift, run/inspect static self-test readiness, and prepare the one-time Windows bootstrap. Do not claim OPERATIONAL before real PC/Codespaces/Android evidence exists.
