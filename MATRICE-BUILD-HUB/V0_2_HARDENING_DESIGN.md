# MATRICE BUILD HUB V0.2 — HARDENING DESIGN

Date: 2026-09-18
Status: hardening branch, not yet promoted to main.

## Mission
Preserve the user's simple workflow:
feedback in ChatGPT -> source change -> one deliberate build -> real verified artifact -> usable link.

The user must not need to learn Gradle, Android SDK, Codespaces, SSH, signing, or CI internals.

## Non-negotiable constraints
- Zero paid dependency.
- GitHub Actions hosted runners remain manual-only and are not used by normal Build Hub production.
- GitHub is the canonical source repository.
- GitHub Codespaces is the primary remote builder while included quota is available.
- Smallest suitable machine first (normally 2 cores / 8 GB RAM).
- No Codespaces prebuilds, because prebuild generation consumes GitHub Actions minutes.
- No silent signing-key rotation.
- No beta is "delivered" unless the actual binary is built and its identity/signature gates pass.
- Failed builds must still return diagnostics.
- A build must be tied to one exact source commit SHA.
- The end-user workflow must remain one launcher + project choice.

## Risks found in V0.1 and V0.2 countermeasures

### R1 — signing identity stored only in expiring Actions artifacts
Impact: catastrophic. Future APK updates become impossible with the existing Android install identity.
Countermeasure:
- one-time migration of signing material into repository-scoped Codespaces development secrets;
- encrypted Windows DPAPI recovery backup stored outside the Git clone;
- old Actions artifact is transition-only, never the durable authority.

### R2 — central adapter can drift away from the project
Impact: wrong or broken build after project evolves.
Countermeasure:
- each production branch owns .matrix-build/build.sh;
- central adapters are fallback/recovery only;
- Hub prefers the branch-local build recipe.

### R3 — prerelease can target the wrong commit
Impact: release metadata does not identify the source that produced the binary.
Countermeasure:
- resolve branch to exact SHA before Codespace creation;
- pass EXPECTED_SOURCE_SHA to the build;
- verify remote HEAD equals expected SHA;
- result manifest must contain source_sha;
- GitHub release is created with --target exact SHA.

### R4 — nested artifacts not published
Impact: build succeeds but APK/EXE link is missing.
Countermeasure:
- build recipe places user-facing deliverables at output root;
- full diagnostic tree is bundled into a ZIP;
- Hub publishes only explicit root deliverables and evidence bundle.

### R5 — stale local Hub
Impact: user executes an old orchestrator against newer project contracts.
Countermeasure:
- bootstrap installs a canonical local clone under LOCALAPPDATA;
- launcher self-updates PROJECT-DRAFTS before invoking Hub;
- state/output live outside the clone.

### R6 — orphan Codespace continues consuming quota/storage
Impact: quota exhaustion.
Countermeasure:
- try/finally stop/delete;
- verify cleanup;
- on cleanup failure, stop as fallback and emit high-severity warning;
- remove stale mbh-* Codespaces from previous interrupted runs before starting.

### R7 — concurrent double-build
Impact: duplicate quota consumption and conflicting releases.
Countermeasure:
- local named mutex;
- unique build ID;
- immutable SHA-scoped prerelease tags.

### R8 — transient network failures during SDK/Gradle downloads
Impact: failed builds and wasted compute.
Countermeasure:
- bounded retries for downloads and sdkmanager;
- no automatic retry of the whole build;
- diagnostics retained for user/ChatGPT analysis.

### R9 — Android toolchain drift
Impact: a build that worked yesterday may fail after unpinned upstream changes.
Countermeasure:
- project contract pins JDK/Gradle/SDK Build Tools/API;
- command-line tools revision pinned by Build Hub adapter;
- versions recorded in BUILD_PROVENANCE.json.

### R10 — memory pressure / Gradle daemon disappears
Impact: build failure even on cloud machine.
Countermeasure:
- minimum 2-core Codespace is 8 GB RAM;
- build scripts cap workers and use controlled Gradle JVM memory;
- no emulator;
- no Android Studio;
- Gradle daemon disabled for ephemeral release build.

### R11 — user quota exhausted
Impact: builder unavailable.
Countermeasure:
- local estimated core-hour ledger;
- internal soft budget below GitHub Free allowance;
- smallest machine selected;
- no paid overage assumption;
- explicit QUOTA_BLOCKED failure classification.

### R12 — publication after partial verification
Impact: bad APK distributed.
Countermeasure:
- scripts fail closed;
- result.json is written only after all gates pass;
- Hub refuses publication without valid result schema and source SHA match.

### R13 — branch name / shell injection
Impact: remote command corruption.
Countermeasure:
- branch/project values validated against conservative allowed character set;
- project registry is authoritative for normal operation.

### R14 — local output lost
Impact: successful build exists only remotely.
Countermeasure:
- copy results before deleting Codespace;
- publish verified prerelease;
- keep local copy in Downloads/MatriceBuildHub.

### R15 — one provider outage
Impact: temporary inability to build.
Countermeasure:
- Codespaces primary;
- local low-RAM builder remains planned fallback;
- GitHub Actions remains exceptional recovery after quota reset;
- adapter contract is portable Linux shell, avoiding lock-in to Actions YAML.

## Included-quota model
GitHub Free currently includes 120 Codespaces core-hours and 15 GB-month storage.
A 2-core machine consumes 2 core-hours per wall-clock hour.
Build Hub internal default cap: 90 core-hours/month, reserving 30 core-hours outside Build Hub.
This is an internal guard, not a substitute for GitHub billing data.

## Certification levels
- DESIGN_READY: files and contracts statically coherent.
- BOOTSTRAP_READY: PC bootstrap/self-test paths implemented.
- CLOUD_SMOKE_PASS: can create a Codespace, run a no-build diagnostic, copy output, and delete it.
- ANDROID_BUILD_PASS: a real APK built.
- SIGNATURE_PASS: APK certificate/package/version gates pass.
- UPDATE_PASS: APK installs over previous beta without uninstall.
- OPERATIONAL: at least two consecutive independent builds succeed with no manual shell work.

V0.2 must not be called OPERATIONAL before these runtime gates are observed.
