# BookHarvester V1.3 — 3 real-book texts, complete offline page simulation

Status: **PASS for controlled end-to-end book pipeline; FAIL/NOT CERTIFIED for live Ranovel chapter extraction**.

## Evidence

- GitHub Actions success: https://github.com/Terminator364/PROJECT-DRAFTS/actions/runs/38198261622
- SHA256-checked V1.3 source archive; 23 core tests passed.
- Downloaded **three real, public-domain complete source texts** (one HTTPS file per work) from Project Gutenberg, then parsed them into 77 actual chapters.
- Generated local HTML web-page fixtures **from those real texts** (not fake chapter prose), used the real BookHarvester parser, simulated HTTP 403 stop and recovery, preserved SQLite state, and generated PDF/EPUB per book. The 77 page fetches used an in-memory test adapter, **not direct remote chapter-page requests**.

| Work | Test sample (random but deterministic) | All chapters | PDF pages | EPUB chapters |
|---|---:|---:|---:|---:|
| Alice's Adventures in Wonderland | 4, 5, 12 | 12/12 | 154 | 12 |
| The Marvelous Land of Oz | 6, 9, 18 | 24/24 | 264 | 24 |
| Anne of the Island | 23, 38, 39 | 41/41 | 453 | 41 |
| **Total** | **9 distinct samples** | **77/77** | **871** | **77** |

## Separate site-specific gate

Ranovel / I Am the Demon Lord remains **not validated**. On previous GitHub runner and the user's PC, the verified chapter URLs returned HTTP 403 even though its novel landing page returned HTTP 200 from the PC. Other systems' indexed copies do not prove a working downloadable URL. Do not bypass access restrictions. The cross-browser extension can only capture chapter pages that a browser session is authorized to display, subject to extension approval by the user.

## Resource limits / CI policy

The Carnegie Mellon hypertext mirror used as a separate source reference declares a **crawl-delay: 10** for general bots. To avoid wasting hosted minutes and placing 77 closely spaced requests against a server requesting low rate, the full 77-chapter test retrieved three bulk public-domain source files from Project Gutenberg and drove per-page extraction locally. This is labeled a controlled site simulation, not full remote harvesting.

## Next gate

On a browser showing permitted Ranovel chapters: pick three random real chapter indices across beginning/middle/end, verify actual content length/uniqueness and title, pause/resume, EPUB and PDF. Only then certify live compatibility or attempt the whole 236-chapter reading work. Respect the platform's access rules and authors' rights.
