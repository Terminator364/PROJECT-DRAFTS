# BUILDHUB AX15 — STATIC AUDIT REPORT

Date: 2026-09-18
Repository: Terminator364/PROJECT-DRAFTS
Branch: buildhub-v0.2-hardening-20260918
Audited code snapshot: 4da4a011356a72644f961d48ab91eed31ed4cccf
AX baseline: AX150K V1.3 Operational (2026-09-17), with supplemental anti-Goodhart / evidence-first guards.

## Verdict

STATIC_AUDIT_PASS: PASS
Repository deterministic audit: 70 PASS / 0 FAIL.
ZERO_AUTO_ACTIONS_ACTIVE_BRANCHES: PASS (previous 23/23 manual-only evidence remains valid; active project branch heads have not moved past the manual-only commits).
OPERATIONAL: NO.

This report does not convert static evidence into Windows, Codespaces, Android-device, or update-install evidence.

## Evidence boundaries

Observed / repository-level:
- BuildHub V0.2 registry and JSON contracts parse.
- exact-source-SHA guards are present.
- normal BuildHub flow contains no hosted GitHub Actions dispatch.
- signing secret upload to Codespaces is absent.
- Android signing is local Windows DPAPI.
- release target is bound to exact source SHA.
- release assets are verified by GitHub SHA-256 digest and size before final delivery.
- recovery proof is V2 functional proof: decrypt + archive hash + keystore open + canonical certificate match.
- plaintext disaster-recovery bundle is deleted in finally even on encryption failure.
- shell files are forced to LF by .gitattributes.
- selected remote project recipe is parsed with bash -n before build execution.
- local sdkmanager operations are bounded by timeout.
- launcher/bootstrap refuse stale canonical-source refresh failures.
- budget guard reserves worst-case build timeout plus startup overhead before creating a builder.
- successful certification is blocked if Codespace deletion cannot be confirmed.
- if initial Codespace discovery fails, cleanup re-discovers by BuildId before giving up.
- remote project branches are correctly marked referenced, not materialized, in AX150K_CONTEXT.
- one runtime entry, one release verifier, and one recovery verifier are enforced to detect accidental script duplication.

Not yet observed:
- Windows PowerShell Parser.ParseFile execution on the user's PC.
- real Windows bootstrap.
- real DPAPI vault creation.
- real encrypted disaster-recovery export and restore.
- real Codespace creation/smoke/delete.
- real Android cloud compile.
- local APK signing on the user's Windows PC.
- install/update over the already-installed PhoneMouse beta.
- second independent successful build.

## Defects found and corrected in this hardening continuation

1. Release reuse previously checked expected filenames but not published bytes.
   - Fixed with post-publication GitHub release-asset SHA-256 + size verification.

2. Recovery verification previously proved decryption/hash only, not that signing keys were functionally usable or canonical.
   - Fixed with keystore opening and canonical certificate verification.

3. Failed age encryption could leave a cleartext recovery ZIP in TEMP.
   - Fixed with unconditional finally cleanup.

4. Windows checkout could convert shell scripts to CRLF before copying them to Linux Codespaces.
   - Fixed with .gitattributes eol=lf and shell syntax gates.

5. AX evidence incorrectly called remote project branches materialized.
   - Fixed to referenced with explicit evidence note.

6. sdkmanager license/install operations could wait indefinitely.
   - Fixed with bounded process execution and process-tree termination on timeout.

7. Launcher could continue with an old local BuildHub after git refresh failure.
   - Fixed fail-closed.

8. Signing migration did not require the later-used key password and keytool parsing was locale-sensitive.
   - Fixed complete credential validation and forced English keytool output.

9. An incremental release-integrity patch accidentally duplicated part of hub.ps1.
   - Detected by counter-audit before promotion or execution.
   - hub.ps1 was rebuilt from the last known-good V0.2 blob and hardening was reapplied.
   - regression gates now enforce singleton runtime/release/recovery sections.

10. main and the hardening branch had diverged because main gained a local PhoneMouse fallback after the hardening branch was created.
    - Reconciled with a real two-parent merge commit; no force-push and no loss of either line.

## Promotion rule

The hardening branch may be fast-forwarded to main only while:
- main is an ancestor of the hardening head;
- the static audit remains PASS;
- OPERATIONAL remains false until the real field gates pass.

After promotion, the next action is the one-time Windows bootstrap. The bootstrap runs the PowerShell parser self-test before any cloud build.
