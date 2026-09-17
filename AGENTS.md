# AGENTS.md — GitHub Actions Ultra-Low-Budget Governor

## Authority and scope
This is a standing repository-owner instruction. It applies to ChatGPT, Codex, GitHub-connected agents, automation authors, and future contributors working in this repository.

It remains in force until the repository owner explicitly revokes or changes it.

## Primary objective
GitHub-hosted Actions minutes are a scarce resource.

**Normal target: 0 GitHub-hosted runner minutes per day.**
**Global planning target across all Terminator364 ChatGPT repositories: about 30 GitHub-hosted runner minutes per month, not 2,000.**

Remote CI is an exception, not the default development loop.

## Hard operating rules
1. Do not add automatic GitHub-hosted Actions triggers for ordinary `push`, `pull_request`, or `schedule` events without explicit owner approval.
2. Existing GitHub-hosted workflows should default to `workflow_dispatch` only.
3. Do not run a remote workflow after every commit. Batch changes and validate remotely only at a meaningful checkpoint.
4. Exhaust local/static/connector-based validation first when it can answer the question without a GitHub-hosted runner.
5. Never rerun an unchanged failed workflow. Diagnose and change something material before another remote run.
6. Prefer one targeted job over a matrix or multiple overlapping workflows.
7. Use Windows/macOS/Android-heavy remote jobs only when platform-specific evidence is indispensable.
8. Routine commits should use a CI-skip annotation when any automatic workflow might still exist and the commit does not require remote validation.
9. A remote run is justified mainly for: installable APK/EXE generation, release candidate, signing/release evidence, OS-specific validation, or a final checkpoint that cannot be reproduced locally.
10. Do not weaken product quality to save minutes. Move verification to cheaper/local stages and reserve remote runners for evidence that truly requires them.

## Soft monthly allocation
The global target is approximately 30 GitHub-hosted runner minutes/month across the current active repositories:
- PhoneMouse: target ceiling 15 min/month.
- P2PCR95: target ceiling 9 min/month.
- ChatGPT-PC: target ceiling 6 min/month.
- PROJECT-DRAFTS: 0 min/month by default.

These are planning ceilings, not permission to spend them automatically. Unused minutes should remain unused.

A future repository starts with **0 automatic Actions and 0 allocated minutes** until its real CI need is known. Creating a new repository must not increase the global target automatically.

## New-repository bootstrap rule
Any project promoted from PROJECT-DRAFTS or created as a new ChatGPT-managed Terminator364 repository must copy this AGENTS.md into the repository root before adding or enabling GitHub Actions.

## Remote-run decision gate
Before dispatching any GitHub-hosted workflow, the agent must be able to answer YES to all of:
- Is this remote run necessary to obtain evidence unavailable cheaply/local?
- Have relevant changes been batched?
- Has the previous failure, if any, been materially addressed?
- Is this the smallest targeted workflow/job that can answer the question?
- Is the expected value of this run greater than its Actions cost?

If any answer is NO, do not dispatch the workflow.

## Current emergency state
As of 2026-09-18, the account reached 100% of its included GitHub Actions minutes for the billing cycle. Until capacity resets or the owner explicitly changes the policy, treat GitHub-hosted Actions as effectively unavailable except for an owner-authorized critical checkpoint.
