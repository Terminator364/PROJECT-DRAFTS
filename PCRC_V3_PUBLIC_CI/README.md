# PCRC V3 — isolated PUBLIC CI lane, 12 November 2026

This is a public, self-contained, synthetic contract lab in PROJECT-DRAFTS.

The *real* V3 code, owners, PCs, hostnames, private URLs, signatures, keys,
SQLite databases, session receipts, Site configuration, HP logs and release
artifacts remain in the private ChatGPT-PC repository / owner's HP.

The Python files in this folder are newly written public test models. They
DO NOT import or fetch private code and are not byte-identical to the private
implementation. A green CI proves **only these abstract fail-closed invariants**
on a GitHub-hosted public runner, not that GO-3's private code has passed
GitHub Actions and not that a release was signed or installed.

The actual private source must be tested on the owner's HP as an independent
local receipt. CI in the private repository is currently blocked by exhausted
private hosted-runner allowance; avoid retry loops.

The sole workflow is restricted to one public branch and these paths; standard
Ubuntu runner only; no schedule, secrets, third-party private checkout, downloads
from private endpoints, production mutation, or artifact publication. One
batched push is used as the explicit owner-approved public CI checkpoint.
