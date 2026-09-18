# BROWSER4G — CONTINUATION CHECKPOINT

Continuation code:

`BROWSER4G CONTINUE`

Date: 2026-09-18  
Canonical repository: `Terminator364/PROJECT-DRAFTS`  
Working branch: `browser4g-p0-20260918`

## Recovery rule

When the user types `BROWSER4G CONTINUE`, recover this repository state first. Do not restart the browser design from zero and do not skip the P0 field gates.

## Current certification

- Design: `DESIGN_HARDENED`
- Browser source: `P0.1_SOURCE_READY`
- Build: `BUILD_UNVERIFIED`
- Runtime: `RUNTIME_UNVERIFIED`
- Field: `FIELD_UNVERIFIED`
- Multi-tab: **BLOCKED until P0_FIELD_PASS**
- BuildHub V0.3 BROWSER4G integration: **STATIC_QUALIFIED / FIELD_UNVERIFIED**
- GitHub-hosted Actions used by this work: **0**
- Software budget target: **0 USD**

No static result may be restated as a real Windows build or field PASS.

## Static evidence

Code/config snapshot audited through branch commit:

`49e1c061ad7014000259d37bc7b3623f6ba3c885`

Documentation-only alignment followed that snapshot before this checkpoint.

Independent structural/invariant audit after sparse-checkout integration:

- **66 / 66 PASS**
- registry V0.3
- BROWSER4G `LOCAL_WINDOWS`
- exact detached source SHA
- guarded sparse checkout limited to `BROWSER4G`
- 60-minute first-build bound
- source-owned PowerShell recipe
- field publication gate
- artifact SHA-256 verification
- old Codespaces/Linux path retained for existing projects
- no GitHub Actions dispatch
- WebView2 SDK / NuGet / toolchain pins
- static WebView2 loader
- Runtime Health Guard
- full WebView2-process memory telemetry

Lexical/XML form audit after the same integration:

- **9 / 9 PASS**
- 5 PowerShell scripts
- C++ source
- Python AX15 harness
- Visual C++ project XML
- NuGet packages XML

These are static checks only. The authoritative PowerShell parser, MSVC linker/compiler, WebView2 runtime and the real 4 GB PC remain field evidence.

## P0.1 browser baseline

- Native Win32 / C++17 / x64.
- WebView2 SDK pinned to `1.0.4191.47`.
- One active WebView2 only: SLOT A.
- Explicit UDF: `%LOCALAPPDATA%\BROWSER4G\P0\UserData`.
- Static WebView2 loader: expected deliverable is one EXE.
- Runtime Health Guard keyed by `build + SDK + runtime`.
- Local no-network DOM/JavaScript micro-probe before external navigation.
- No automatic runtime downgrade.
- Telemetry every 15 s:
  - host Working Set + Private Usage;
  - WebView2 processes exposed by `ICoreWebView2Environment8::GetProcessInfos` (API excludes crashpad);
  - aggregate WebView2 Working Set + Private Usage;
  - aggregate host + WebView2 totals;
  - physical-memory availability/load;
  - Windows commit total/limit/percentage.
- No adaptive governor yet.
- No multiple tabs yet.
- No SQLite history/favorites/recovery yet.
- No custom download/BITS path yet.
- No automatic WebView2 Evergreen Runtime repair/install yet.

## Reproducible local build chain

- Visual Studio 2022 Build Tools / MSVC x64 detected through `vswhere`.
- If missing, conditional zero-cost provisioning through winget:
  - `Microsoft.VisualStudio.2022.BuildTools`
  - `Microsoft.VisualStudio.Workload.VCTools`
- Toolchain install refuses when system-drive free space is below the safety floor.
- NuGet CLI pinned to `7.9.0`.
- NuGet SHA-256 pinned to:
  `992D70CAC5B06C38EFEC91806CABA64CDCC07E6D963A0959DBBBAF264D33B800`
- WebView2 restore forced from `https://api.nuget.org/v3/index.json`.
- MSBuild limited to one worker: `/m:1`.

## BuildHub V0.3 integration

BROWSER4G registry contract:

- repo: `Terminator364/PROJECT-DRAFTS`
- builder: `LOCAL_WINDOWS`
- branch: `browser4g-p0-20260918`
- recipe: `BROWSER4G/.matrix-build/build.ps1`
- timeout: 60 minutes
- sparse materialization: `BROWSER4G` only
- publication: blocked by `FIELD_PASS_REQUIRED`

The local Windows engine:

1. resolves the branch to an exact GitHub SHA;
2. clones into an isolated temporary directory;
3. enables guarded cone sparse checkout;
4. detached-checkouts the exact SHA;
5. verifies the checked-out SHA;
6. verifies that the recipe cannot escape the source root;
7. runs the recipe under a bounded job;
8. validates `mbh-result-v1`;
9. verifies declared deliverables and EXE SHA-256 sidecar;
10. writes an evidence ZIP;
11. cleans the temporary source tree.

Existing PhoneMouse, P2PCR95 and ChatGPT-PC keep the previous Codespaces/Linux path.

## P0 field gate

Do not enable multi-tab until the real target Windows PC proves at least:

1. compilation succeeds under real MSVC;
2. one mono-EXE artifact is produced;
3. app starts without crash;
4. `RUNTIME_PROBE_PASS` is logged;
5. WebView2 renders;
6. external navigation works after the health probe;
7. host + WebView2 telemetry is recorded for at least 10 minutes on a stable page;
8. no obvious monotonic leak is observed in that interval;
9. restart with unchanged health signature works;
10. later runtime/build/SDK change re-triggers the probe.

## Next atomic action

Run the first **real Windows BROWSER4G BuildHub build** on the target PC. Capture:

- MSVC/toolchain outcome;
- exact source SHA;
- resulting EXE SHA-256;
- PowerShell self-test output;
- BuildHub result/evidence directory;
- first runtime log and telemetry.

Only then may `BUILD_UNVERIFIED` advance.

## Absolute rules

- No GitHub-hosted Actions for routine BROWSER4G production.
- No claim of field evidence from static checks.
- No multi-tab before P0_FIELD_PASS.
- No promise of full DOM/form/travel-log restoration for COLD tabs.
- No automatic downgrade of a UDF to an older WebView2 runtime.
- Preserve the 0 USD architecture whenever technically possible.
