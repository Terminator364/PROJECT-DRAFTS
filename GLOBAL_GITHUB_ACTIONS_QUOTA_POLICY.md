# GLOBAL — GitHub Actions Monthly Quota Policy

Applies to **all current and future repositories/projects** owned by Terminator364.

Canonical external policy (Drive):
- 00_GLOBAL_CHATGPT_GITHUB_ACTIONS_QUOTA_POLICY
- Drive ID: 1AO2fdEmkoU9BI4seyMegU9AESH4_u9Qp--54CibtLeE

## Operating rule

GitHub Actions are **allowed**, but they are a scarce monthly resource.

Default development mode:
- LOCAL / ZERO-ACTIONS-MINUTES
- build and test locally when practical
- use static validation, targeted tests, cached artifacts and existing evidence
- do not run CI just because code changed
- avoid push-triggered iterative development workflows
- batch expensive checks
- prefer one manual final/periodic proof run after local validation
- never burn minutes to diagnose syntax/source issues that can be checked locally
- stop retry loops when failure is quota/account/infrastructure related

Financial constraint:
- no additional paid Actions quota should be assumed
- the monthly included allowance should be managed to last the full month whenever possible

User-intervention rule:
- do not require the user to administer GitHub Actions manually
- the assistant manages technical workflow; user is only involved for genuine physical-device testing or external authorization

Temporary blocking of Actions is quota management, **not a permanent ban**.

## Current effective mode — 2026-09-18

P2PCR95: local build/test until a GitHub Actions run is materially worth the quota.
PhoneMouse: inherit this rule.
ChatGPT-PC: inherit this rule.
PROJECT-DRAFTS and future repositories: inherit this rule by default.
