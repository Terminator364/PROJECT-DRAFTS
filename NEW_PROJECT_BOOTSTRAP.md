# NEW PROJECT BOOTSTRAP — Terminator364 / ChatGPT

This checklist is mandatory for every new ChatGPT-managed GitHub project.

## Before creating a permanent repository
- Start the project in `Terminator364/PROJECT-DRAFTS`.
- Read the root `AGENTS.md`.
- Read `CI_BUDGET_POLICY.json`.
- Assume GitHub-hosted Actions budget = **0 by default**.

## When promoting to a dedicated repository
- Copy `AGENTS.md` to the new repository root before enabling CI.
- Do not create automatic `push`, `pull_request`, or `schedule` workflows.
- Prefer no `.github/workflows` directory at all until there is a concrete remote-run requirement.
- When a workflow becomes necessary, default it to `workflow_dispatch` only.
- Keep remote jobs narrow, targeted, and checkpoint-based.
- Use local/static validation first.
- Never retry an unchanged failed workflow.
- Never enable a matrix or multi-OS job merely for convenience.
- Do not increase the global monthly Actions target merely because a new project exists.

## Required ChatGPT behavior
Any ChatGPT conversation or agent that creates or restructures a Terminator364 project must treat the ultra-low GitHub Actions policy as a standing architectural constraint.

If the conversation lacks prior context, the repository files are authoritative.

If a proposed workflow conflicts with the policy, the agent must preserve the policy unless the owner explicitly overrides it.

## Success condition
A new repository is compliant when:
- root `AGENTS.md` exists;
- no automatic GitHub-hosted workflow exists by default;
- Actions usage is expected to remain at zero during ordinary development;
- remote Actions are reserved for indispensable release/build/platform-specific checkpoints.
