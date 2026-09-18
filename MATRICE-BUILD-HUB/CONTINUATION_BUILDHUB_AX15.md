# BUILDHUB AX15 — CONTINUATION CHECKPOINT

Continuation code:

`BUILDHUB AX15 RECOVER`

Date: 2026-09-18
Canonical repository: Terminator364/PROJECT-DRAFTS
V0.2 hardening branch: buildhub-v0.2-hardening-20260918
Static-audit report: MATRICE-BUILD-HUB/STATIC_AUDIT_REPORT_20260918.md
State recorded through parent snapshot: 4acb15c0f76ec8b21f9a6c5b8f893486c50c71d8

## Recovery behavior

When the user types `BUILDHUB AX15 RECOVER`, recover GitHub first. Do not restart V0.1 or repeat already-proven design work.

After V0.2 static promotion, inspect `main` first and use the hardening branch only as audit/history reference.

## Mission

Preserve this user workflow:

feedback/bug in ChatGPT -> repository correction -> deliberate BuildHub run -> exact-SHA cloud build -> local Android signing when required -> verification -> GitHub prerelease -> usable link.

No manual Gradle/SSH/Codespaces developer workflow should be pushed onto the user.

## Frozen AX baseline

- AX150K V1.3 Operational
- reference date: 2026-09-17
- supplemental development guards:
  - anti-Goodhart / TARGET_COUNT_NOT_SUFFICIENT
  - causal novelty / salami-slicing control
  - independent oracles
  - bounded causal-neighborhood interactions
  - reality-gap contract
  - version-specific evidence and stale-proof invalidation

Do not treat AX150K target counts as proof by themselves.

## Active architecture

- GitHub is canonical source.
- Normal GitHub Actions hosted-runner usage: zero; active production workflows are manual-only.
- GitHub Codespaces is the primary remote compiler while included quota is available.
- no Codespaces prebuilds.
- smallest suitable machine first.
- project recipe is source-owned: `.matrix-build/build.sh`.
- branch resolves to one exact source SHA before builder creation.
- selected remote recipe is parsed before build execution.
- Android cloud output is unsigned.
- Android signing keys remain on Windows in DPAPI CurrentUser vault.
- local signer verifies package, version and canonical certificate.
- encrypted disaster-recovery export + functional restore proof are mandatory before signed APK production.
- published release assets are verified against GitHub SHA-256 digest + size.
- Codespace cleanup is mandatory; successful certification fails if deletion is not confirmed.
- internal quota guard reserves worst-case project timeout + startup allowance.
- shell files use LF across Windows -> Linux.
- launcher/bootstrap fail closed if canonical source cannot refresh.
- existing local PhoneMouse builder is retained only as an emergency fallback.

## Production branches

PhoneMouse:
- Terminator364/PhoneMouse
- beta11-visual-20260918
- active head observed: 868afa5488ce722f80c9ee9d9a42b7078722a0a8

P2PCR95:
- Terminator364/P2PCR95
- beta03-native-updater-20260918
- active head observed: 4d3974119e77d115e02226d341aaf875ba72a2d0

ChatGPT-PC:
- Terminator364/ChatGPT-PC
- work/worker-v024-local-heartbeat-spool
- active head observed: aab3138237c31ac8171fb0e883a6a901a4fec371

These observed heads contain the manual-only workflow changes. Previous evidence remains 14 + 6 + 3 = 23 active workflows checked manual-only.

## Major V0.2 hardening now integrated

- exact-SHA source/result/release binding
- source-owned recipes
- no hosted Actions dispatch in normal BuildHub
- local named build mutex
- prebuild refusal
- bounded remote build
- failure classification
- estimated Codespaces ledger + projected budget reservation
- stale/orphan Codespace cleanup and certification block on failed deletion
- Android toolchain pinning
- Windows-only DPAPI signing vault
- canonical cert check during signing migration
- complete signing-credential validation
- locale-stable keytool parsing
- portable age-encrypted disaster-recovery export
- plaintext recovery cleanup on all exits
- functional recovery restore test: decrypt + hash + open keystore + cert match
- recovery marker V2 semantic validation before signed production
- release-asset SHA-256 + size verification after publication
- LF shell portability contract
- selected recipe `bash -n` gate
- bounded Windows sdkmanager operations
- stale launcher/build bootstrap fail-closed
- AX evidence classification fixed: remote branches are referenced, not materialized
- anti-duplication guards for central hub structure
- main-only local PhoneMouse fallback reconciled via two-parent merge without force-push

## Important counter-audit incident

A release-integrity incremental patch accidentally duplicated part of `hub.ps1`.

The defect was detected before promotion or execution.

Response:
1. promotion was stopped;
2. `hub.ps1` was restored from the known-good V0.2 blob at checkpoint `b06291d117d8997365076d6c5b3773ddcdbdc89a`;
3. all intended hardening was reapplied from the clean source;
4. singleton guards were added for runtime entry, release verifier, and recovery verifier;
5. repository deterministic audit was rerun.

This incident must remain in the evidence trail; do not erase it from future summaries.

## Current certification

- DESIGN_READY: PASS
- STATIC_AUDIT_PASS: PASS — deterministic repository audit 70/70
- ZERO_AUTO_ACTIONS_ACTIVE_BRANCHES: PASS
- LOCAL_BOOTSTRAP_PASS: PENDING real Windows PC
- LOCAL_SIGNING_VAULT_PASS: PENDING real Windows PC
- DISASTER_RECOVERY_EXPORT_PASS: PENDING
- DISASTER_RECOVERY_RESTORE_TEST_PASS: PENDING
- CLOUD_SMOKE_PASS: PENDING
- ANDROID_CLOUD_BUILD_PASS: PENDING
- LOCAL_SIGNATURE_PASS: PENDING
- RELEASE_ASSET_DIGESTS_PASS: PENDING real publication
- UPDATE_OVER_EXISTING_APP_PASS: PENDING real Android device
- SECOND_INDEPENDENT_BUILD_PASS: PENDING
- OPERATIONAL: NO

A static PASS is not field evidence.

## Static promotion completed

- `main` was fast-forwarded without force to field-candidate snapshot `6a634255724f609988a546e7051ca0c4b060fc28`.
- Post-promotion verification confirmed one runtime entry, one release verifier, one recovery verifier, and the digest/budget/cleanup/recovery guards on `main`.
- Subsequent documentation-only commits may advance the exact main SHA; code qualification remains tied to the static-audit report and the code snapshot it records.

## Next atomic actions

1. On the user's real Windows PC, run the one-time `bootstrap-pc.ps1`.
   - The bootstrap runs PowerShell `Parser.ParseFile` over all BuildHub PS1 files before any build.
   - Complete GitHub/Codespaces authorization if prompted.
   - Migrate PhoneMouse + P2PCR95 signing identities to local DPAPI vault.
   - Export encrypted disaster-recovery backup.
   - Select it again and complete the functional restore test.
2. Launch BuildHub and choose option 4: cloud smoke only.
3. If smoke PASS, run a real PhoneMouse BETA11 build.
4. Verify local canonical signature/package/version and GitHub release digests.
5. Install BETA11 over the existing beta WITHOUT uninstalling.
6. Repeat an independent build.
7. Then qualify P2PCR95 BETA03.
8. Only after the runtime gates pass may OPERATIONAL become YES.

## Absolute rules

- No automatic GitHub Actions.
- No Android signing key in Codespaces.
- No replacement signing key.
- No force-push to promote BuildHub.
- No claiming runtime PASS from static evidence.
- No hiding failed/corrupted intermediate attempts.
- No manual-developer workflow imposed on the user.
- Keep `BUILDHUB AX15 RECOVER` as the canonical continuation command.
