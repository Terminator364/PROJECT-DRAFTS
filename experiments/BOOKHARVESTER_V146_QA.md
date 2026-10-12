# V1.4.6 — fail-closed identity QA (2026-10-12)

Local proof: 69 Python tests and three Node.js extension tests passed. Important regressions reproduced *before* fixing: an HTTP 200 table of contents was accepted as a chapter; Chapter 92 displayed while the extension expected Chapter 91; a renamed HTML file contained the wrong chapter. Each now fails closed. Batch source archive sha256: 11e23c35069d0a2a7537219d877417279260f2a4ff3fd939cbf0a2077f47c82e.

Ranovel: still **not certified**. Cloudflare 403 observed from hosted CI and MBMPC. The domain terms forbid copying material; this QA must not circumvent technical protection or imply license. A human completing an access challenge (if offered) does not confer reproduction rights. This branch is a product quality fix, not a claimed Ranovel acquisition release.

CI policy: one-off, branch-specific Windows qualification checkpoint, then workflow_dispatch only. No recurring GitHub-hosted automation.
