# QuotaPulse Windows — lightweight 1-window companion
Verified on HP Windows 11, 2026-11-08. **Only PCRC native tools were used**; no commercial Remote Desktop Commander MCP tool calls.

## Local paths
- Source / binary: %LOCALAPPDATA%\QuotaPulse\
- User launch: %USERPROFILE%\Desktop\QuotaPulse.lnk
- Live executable: QuotaPulse.exe
- Staged executable: QuotaPulse.staged.exe
- Rollback: QuotaPulse.rollback.exe
- Last locally verified snapshot: quota.txt
- Native JSON diagnostic: probe-result.json

## Behavior
Native .NET Framework WinForms/GDI+ widget (~420x478 px), with 1 button, 0 resident service, no autostart.
Reads *already open Edge* Desktop Commander Usage page via Windows UI Automation; verifies used + remaining == monthly limit; caches last result when Edge is absent.
Does not call MCP `who_am_i` or other quota-consuming tools. When the page is closed, a live refresh is unavailable: cached figures have timestamp.

## QA evidence (actual Windows)
- C# compilation successful with installed framework CSC (no additional runtime download)
- Two parser selftests: PASS
- Real Edge UI Automation probe on 2026-11-08 at 16:33+01:00:
  `used:7811, limit:10000, remaining:2189, daily_average:976, reset:"1 déc."`
- Screenshot of live window captured: 420x478, no clipping; UI visually reviewed
- Windows process live: session 2, private bytes ~33.9MB, trimmed resident memory 1.7MB at audited snapshot
- Windows desktop shortcut created
- Final binary SHA256: `77629208F954B205DB9D8771F225A211A4C091CF586B3A4C82D437BD9D76BBAF`

## Update (no reinstall)
After editing source, run `build.cmd` to generate/validate staged EXE. Probe it with `QuotaPulse.staged.exe --probe`. Run `promote.ps1` to replace the same path, create desktop shortcut, preserve rollback and relaunch.
The promotion operates only on QuotaPulse executables and does not install a system service.

## Known boundaries
Windows usage reading depends on an authenticated Edge window, unlike a direct native provider API. Production Android uses a distinct WebView implementation and **must be tested independently**; Windows success does not prove Android success.
