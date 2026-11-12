# Blessing BookHarvester V1.2 — Windows Edge certification report

Date: 2026-10-12

## Final Windows qualification

- **GitHub Actions: SUCCESS** — https://github.com/Terminator364/PROJECT-DRAFTS/actions/runs/38195137729
- Test report `qa-v12.xml`: **31 tests, 0 failures, 0 errors, 0 skipped**.
- Runtime probe: `{ "ok": true, "version": "1.2.0-edge-beta", "ui": "ok" }`.
- PyInstaller Windows portable onedir build completed.
- Real Windows runner installer script completed and desktop shortcut target exists.
- Microsoft Edge extension folder and manifest installed.
- Compiled Windows EXE imported three distinct synthetic chapter texts and exported a verified PDF.
- End-to-end stress tests: 236 synthetic chapters, resume 3 -> 5, corrupted text/duplicate detection, 403 refusal, PDF/EPUB, JavaScript Edge worker mocked navigation.

## Release

- Artifact: `Blessing-BookHarvester-Windows-Edge-V1.2.0` — https://github.com/Terminator364/PROJECT-DRAFTS/actions/runs/38195137729/artifacts/11722688239
- SHA256 of ZIP release: `91574bcf2b8103605b25a0d00c9210ebe387a36831d5f638d81bfeded829bc01`
- SHA256 of Windows EXE within ZIP: `91ba2c3410452ba4f8b133772823b00759a5ec2259229c9299b6eef973728050`

## Strict limitations

- **Ranovel is NOT site-certified.** GitHub-hosted real network attempts on Run 38193147240 (HTTP client) and Run 38193303543 (browser) returned HTTP 403. They are not marked success, nor do we bypass the restriction.
- The new Edge extension reads pages normally accessible to the reader in their authorized browser session, and stops if the site denies access. A 3-real-chapter test must be performed on the user's machine (MBMPC) if allowed.
- Edge requires one manual extension approval under edge://extensions; no silent security bypass.
- Chapter data stays local. No copyrighted novel contents included in repository or test artifact.
- Desktop Commander reported MBMPC offline during this run; installation on that physical PC is not claimed.

## Release gate

**PASS: portable Windows application with the Edge helper on controlled chapter fixtures.**
**BLOCKED: Ranovel real site integration until user-authorized Edge proves chapter access.**
