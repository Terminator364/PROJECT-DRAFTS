# BUILDHUB AX15 — CONTINUATION CHECKPOINT

Continuation code:

BUILDHUB AX15 RECOVER

Date: 2026-09-18
Canonical repository: Terminator364/PROJECT-DRAFTS
Hardening branch: buildhub-v0.2-hardening-20260918
Checkpoint head SHA: 7cecb187a845f311dc0ba193946603c0b2dff5a4

## Meaning of the continuation code

When the user types exactly:

BUILDHUB AX15 RECOVER

in a new ChatGPT conversation, immediately recover the latest BuildHub state from GitHub and continue the AX15GO hardening batch. Do not restart design from zero.

## Project mission

MATRICE BUILD HUB is the centralized zero-cost production system intended to preserve the user's simple workflow:

user reports bug/improvement -> ChatGPT updates repository -> BuildHub creates cloud builder -> build -> local Android signing -> verified artifact -> GitHub prerelease -> usable link.

The user is non-technical. Do not replace this with a manual Gradle/SSH/PowerShell workflow.

## Active architecture

- GitHub = canonical source.
- GitHub Actions hosted runners = manual-only / exceptional.
- Codespaces = primary cloud compiler while included quota is available.
- Smallest suitable Codespace first.
- No Codespaces prebuilds.
- Android signing private keys stay LOCAL on Windows under DPAPI.
- Cloud produces unsigned APK.
- Windows performs zipalign + apksigner + certificate/package/version verification.
- Project build recipes are source-owned under .matrix-build/build.sh.
- Exact source SHA is bound to build result and GitHub prerelease.
- Codespace is stopped/deleted after job.
- BuildHub maintains a local estimated Codespaces core-hour ledger.
- Internal BuildHub cap currently 90 core-hours/month, below the GitHub Free reference allowance.

## Active production branches

PhoneMouse:
- repo: Terminator364/PhoneMouse
- branch: beta11-visual-20260918
- recipe: .matrix-build/build.sh

P2PCR95:
- repo: Terminator364/P2PCR95
- branch: beta03-native-updater-20260918
- recipe: .matrix-build/build.sh

ChatGPT-PC:
- repo: Terminator364/ChatGPT-PC
- branch: work/worker-v024-local-heartbeat-spool
- recipe: .matrix-build/build.sh

## AX15GO batch

Frozen operational reference:
- AX150K V1.3 Operational
- date: 2026-09-17
- status: operational reference with explicit evidence limits

Supplemental development guards in use:
- anti-Goodhart / TARGET_COUNT_NOT_SUFFICIENT
- causal novelty / salami-slicing controls
- independent oracle requirement
- bounded causal-neighborhood interactions
- reality-gap contract
- version-specific evidence / stale-proof invalidation

BuildHub files include:
- AX150K_CONTEXT.json
- AX150K_ADAPTER.json
- AX150K_HARNESS.json
- .ax15go/buildhub_static_harness.py
- self-test.ps1

## Important fixes already integrated

- source-owned build recipes for all 3 active projects
- active-branch automatic workflows neutralized
- PhoneMouse active branch: 14/14 workflows manual-only
- P2PCR95 active branch: 6/6 workflows manual-only
- ChatGPT-PC active branch: 3/3 workflows manual-only
- SHA pinning before remote build
- release target pinned to exact source SHA
- prebuild detection/refusal
- local named mutex preventing concurrent builds
- stale BuildHub Codespace cleanup
- stop/delete cleanup in finally
- bounded remote build timeout
- network/toolchain failure classification
- BuildHub estimated quota ledger
- Android toolchain pinning
- local signing instead of cloud signing
- DPAPI local signing vault
- signing certificate verification planned/in hardening
- P2PCR95 BETA02.1 transition EXE durable-input migration
- portable encrypted disaster-recovery export
- separate disaster-recovery restore verification
- PowerShell syntax self-test
- Python independent static harness
- launcher self-update check
- bootstrap installation path
- fixed bootstrap literal \r\n defect
- added repo + codespace GitHub auth scopes
- mitigated sdkmanager license-pipe deadlock
- persisted JDK path for cross-process reliability

## Current certification state

DESIGN_READY: advanced
STATIC_AUDIT_PASS: pending final full rerun
ZERO_AUTO_ACTIONS_ACTIVE_BRANCHES: PASS
LOCAL_BOOTSTRAP_PASS: not yet observed on real user PC
LOCAL_SIGNING_VAULT_PASS: not yet observed on real user PC
DISASTER_RECOVERY_EXPORT_PASS: not yet observed
DISASTER_RECOVERY_RESTORE_TEST_PASS: not yet observed
CLOUD_SMOKE_PASS: not yet observed
ANDROID_CLOUD_BUILD_PASS: not yet observed
LOCAL_SIGNATURE_PASS: not yet observed
UPDATE_OVER_EXISTING_APP_PASS: not yet observed
SECOND_INDEPENDENT_BUILD_PASS: not yet observed
OPERATIONAL: NO

Do not claim runtime PASS without real evidence.

## Next atomic actions after recovery

1. Verify whether the latest migrate-signing.ps1 certificate-validation patch was committed successfully; user interrupted immediately after that tool call.
2. Re-read bootstrap-pc.ps1, launcher.ps1, hub.ps1, setup-local-signing-tools.ps1, migrate-signing.ps1, local-sign-apk.ps1, remote-runner.sh.
3. Run/perform full static audit:
   - PowerShell syntax
   - JSON contracts
   - shell syntax
   - no cloud signing secrets
   - no hosted Actions dispatch from BuildHub
   - exact SHA/release invariants
   - fail-closed behavior
4. Audit the 3 project .matrix-build/build.sh recipes again after all changes.
5. Finish the disaster-recovery workflow and ensure it is not falsely counted as restored until verify-disaster-recovery.ps1 PASS.
6. Update README/installation instructions to V0.2 architecture.
7. Only if static gates pass, promote BuildHub hardening branch toward main.
8. On the user's real PC:
   - run bootstrap once
   - run option 4 cloud smoke
   - then PhoneMouse BETA11 real build
   - local-sign it
   - verify certificate/package/version
   - install over BETA10 without uninstall
   - verify update behavior
   - perform second independent build before OPERATIONAL certification

## Absolute rules

- Do not reactivate automatic GitHub Actions.
- Do not burn Actions minutes during BuildHub hardening.
- Do not move Android signing keys into Codespaces.
- Do not generate replacement signing keys.
- Do not call static checks equivalent to real field evidence.
- Do not restart from V0.1.
- Do not weaken the user experience into a manual developer workflow.
- Keep the user-facing production flow centralized and simple.
