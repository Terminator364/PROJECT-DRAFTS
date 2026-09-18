# MATRICE BUILD HUB V0.3 — TUNNEL-FIRST AUTOMATION

Date: 2026-09-18  
Status: **PREFIELD / NOT DEPLOYED**

## Rule

The normal BuildHub workflow is no longer a user-operated PowerShell/CMD workflow.

Normal path:

**ChatGPT → ChatGPT-PC Control Bus → mission-scoped R2/2003 → managed BuildHub → named build operation → cloud compiler → local lightweight signing/verification → publication → receipt/readback → ChatGPT.**

The user is not the build operator.

## Forbidden as normal workflow

Do not ask the user to:
- move a BuildHub/PhoneMouse file between Drive, Downloads and folders;
- type PowerShell, CMD, Git, Gradle, Java, Python or GitHub CLI commands;
- take routine terminal screenshots so ChatGPT can infer state;
- download/install build dependencies manually;
- launch `.cmd`, `.bat` or `.ps1` to perform a normal build;
- repeat the same already-valid R2/2003 approval inside the same unchanged mission scope.

Receipts, status probes and logs from ChatGPT-PC are the primary technical evidence.

## Human boundaries that remain legitimate

Zero-manual does **not** mean bypassing external consent/security:
- Windows UAC;
- OAuth or third-party provider consent;
- R3/R4 boundaries;
- Android system permission/install screens when Android requires them;
- subjective UX evaluation on real hardware.

These boundaries must be surfaced only when actually reached.

## Manual launchers

`INSTALL-BUILDHUB.cmd`, `hub.cmd`, `local-phonemouse.cmd` and direct PowerShell entry points remain available only as **BREAK_GLASS / RECOVERY** paths.

Documentation must never present them as the normal product workflow once the tunnel bridge is field-qualified.

## ChatGPT-PC bridge

Pre-field source branch:

`Terminator364/ChatGPT-PC@work/buildhub-managed-r2-bridge-20260918`

The bridge is deliberately fail-closed:
- no arbitrary remote shell;
- managed deployment must match mission-scoped R2/2003;
- deployment package SHA-256 can be pinned;
- managed app id can be pinned;
- only named operations registered in the managed app manifest can run;
- operation scope can be pinned;
- execution remains `shell=False` under app-root and resource limits.

Current G6 field runtime is not modified by this design work while its P0 foundation freeze remains active.

## PhoneMouse

Current field truth:
- installed/field-proven line: **BETA10 / VC16**;
- candidate source: **BETA11 / VC17**;
- branch: `beta11-visual-20260918`;
- BETA11 is not delivered until a real APK is built, signed with the canonical certificate, verified and published.

The previous local PhoneMouse build kit is retained only as break-glass fallback. It is **not** the target operating model.

## Promotion gates

Do not mark tunnel automation operational until:
1. ChatGPT-PC bridge static/regression gates pass;
2. G6 P0 foundation permits deployment;
3. managed BuildHub package is hash-bound and deployed through Control Bus;
4. zero-click R2 activation produces a receipt;
5. `doctor` runs by named operation without user shell work;
6. one real PhoneMouse BETA11 build completes;
7. local signing and canonical certificate verification pass;
8. release/Drive publication readback passes;
9. a second independent build confirms repeatability.

Until then: **PREFIELD, not OPERATIONAL.**
