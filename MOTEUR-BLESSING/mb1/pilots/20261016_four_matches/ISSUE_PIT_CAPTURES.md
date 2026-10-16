# MB-1 V4 finding — historical source provenance bypass in V1.1.2

**Observed 16 Oct 2026 while testing four actual football fixtures.**

V1.1.2 `validate_measurements(strict_evidence=True)` requires a `data_snapshot_id`, a manifest SHA256, publication time, source_artifact_sha256, and a dated historical prior. It **does not independently establish whether the artifact was captured and immutable before the requested historical analysis freeze.**

Controlled reproducible case: generate accurate public historical scores on **16 October** for a match played **10 October**; mark `published_at_utc` with a date attributed to a September recap and hash the newly constructed Oct 16 JSON. The V1.1.2 reference path computes **75.13396%** and emits `REFERENCE_ONLY_NO_SPORTS_TRAINING`. This is **not a valid 10 October prediction**, even when the data values describe real games that happened in September.

V4 `research_features` correctly rejects any row where `captured_utc > freeze_utc`. The pilot preserves BOTH engine outputs to prevent cherry-picking or missing failures.

**Suggested prioritized correction (without an approval claim):** require `captured_utc` at source artifact level, `captured_utc <= analysis_freeze < kickoff`, verify raw byte SHA256, and require independently timestamped archive provenance when claiming historical point-in-time validation. Treat today's local pre-match capture as a *prospective preliminary source* until independently certified. No trained effect; keep scientific status `EXPERIMENTAL_NOT_APPROVED`.

All scripts, source reconstructions, four input packets, four engine outputs, abstentions, pre-match primitive audits and report are in the verified **24-member** [private Drive pilot bundle](https://drive.google.com/file/d/1h2uYsbwkWwu_hRtkeHrbcFSmRCRQkhiY/view?usp=drivesdk), SHA256 `dd2a856bc490a15dc57fc55109b0ec48972cd0d8264e9e0f8f59c1810a9cbbf6`. The bundle has NOT been installed on Windows.
